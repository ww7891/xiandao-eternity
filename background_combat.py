"""
后台战斗模拟器
- 在独立线程中运行战斗逻辑（玩家不动，自动向最近敌人攻击）
- 主线程读取状态用于渲染或显示状态指示器
"""

import threading
import time
import math
import random
from profession_data import PROFESSIONS, get_profession
from enemy_data import get_realm_enemies, ENEMY_TEMPLATES
from drop_data import roll_drop, process_drops


class BackgroundCombat:
    """后台战斗模拟器，线程安全"""

    def __init__(self, map_id, arena_w=1280, arena_h=720, ling_shi_wallet=None):
        from adventure_data import get_map
        map_data = get_map(map_id)
        if map_data is None:
            raise ValueError(f"地图 {map_id} 不存在")

        self.map_id = map_id
        self.map_data = map_data
        self.arena_w = arena_w
        self.arena_h = arena_h
        self.realm_index = map_data["realm"]
        self.template = get_realm_enemies(self.realm_index)
        self.ling_shi_wallet = ling_shi_wallet

        self._lock = threading.Lock()
        prof = get_profession()
        if prof is None:
            prof = PROFESSIONS["sword"]
        self.prof_data = prof
        self.prof = prof["id"]

        import realm_data
        self.realm_data = realm_data
        player = realm_data.player
        self.player_x = arena_w / 2
        self.player_y = arena_h / 2
        self.player_radius = 16
        self.player_speed = 0
        self.player_max_hp = player["hp"]
        self.player_hp = player["hp"]
        self.player_attack = player["attack"]
        self.player_defense = player["defense"]
        self.player_invincible = 0.0
        self.player_attack_timer = 0.0
        self.player_alive = True

        # 灵力条
        self.player_max_mp = player.get("max_mp", 100)
        self.player_mp = player.get("mp", self.player_max_mp)
        self.mp_regen_rate = 1.0  # 每秒恢复1点灵力

        self.enemies = []
        self.enemy_id_counter = 0

        self.projectiles = []
        self.tornadoes = []
        self.slashes = []

        self.particles = []
        self.damage_numbers = []

        self.kill_count = 0
        self.elite_count = 0
        self.total_drops = []
        self.boss_unlocked = False
        self.boss_active = False
        self.boss_defeated = False
        self.result = None
        self.shake_timer = 0.0
        self.shake_x = 0
        self.shake_y = 0

        self.spawn_timer = 0.0
        self.spawn_interval = 0.8
        self.max_enemies = 20
        self.elite_threshold = 10

        self.end_reason = None
        self._running = False
        self._thread = None
        self._start_time = None
        self._max_duration = 3600  # 最大运行时间1小时，防止永久卡死

        self._snapshot_cache = None
        self._snapshot_lock = threading.Lock()

    def _with_lock(self, fn):
        with self._lock:
            return fn()

    @property
    def running(self):
        return self._with_lock(lambda: self._running)

    @property
    def player_hp_safe(self):
        return self._with_lock(lambda: self.player_hp)

    @property
    def player_max_hp_safe(self):
        return self._with_lock(lambda: self.player_max_hp)

    @property
    def kill_count_safe(self):
        return self._with_lock(lambda: self.kill_count)

    @property
    def boss_unlocked_safe(self):
        return self._with_lock(lambda: self.boss_unlocked)

    @property
    def boss_active_safe(self):
        return self._with_lock(lambda: self.boss_active)

    @property
    def is_over(self):
        return self._with_lock(lambda: self.end_reason is not None)

    @property
    def end_reason_safe(self):
        return self._with_lock(lambda: self.end_reason)

    def get_combat_end_info(self):
        """线程安全地获取战斗结束信息"""
        with self._lock:
            if self.end_reason is None:
                return None
            return {
                "reason": self.end_reason,
                "drops": list(self.total_drops),
            }

    def _build_snapshot(self):
        enemies_data = [dict(e) for e in self.enemies if e["alive"]]
        return {
            "player": {
                "x": self.player_x, "y": self.player_y,
                "radius": self.player_radius, "hp": self.player_hp,
                "max_hp": self.player_max_hp, "alive": self.player_alive,
                "invincible": self.player_invincible,
                "prof": self.prof, "prof_data": self.prof_data,
                "mp": self.player_mp, "max_mp": self.player_max_mp,
            },
            "enemies": enemies_data,
            "projectiles": [dict(p) for p in self.projectiles if p["alive"]],
            "tornadoes": [{
                "x": t["x"], "y": t["y"], "damage": t["damage"],
                "color": t["color"], "radius": t["radius"],
                "alive": t["alive"], "lifetime": t["lifetime"],
                "age": t["age"], "angle": t["angle"],
            } for t in self.tornadoes if t["alive"]],
            "slashes": [{
                "x": s["x"], "y": s["y"], "angle": s["angle"],
                "damage": s["damage"], "color": s["color"],
                "radius": s["radius"], "alive": s["alive"],
                "lifetime": s["lifetime"], "age": s["age"],
            } for s in self.slashes if s["alive"]],
            "kill_count": self.kill_count,
            "boss_unlocked": self.boss_unlocked,
            "boss_active": self.boss_active,
            "damage_numbers": [dict(dn) for dn in self.damage_numbers],
            "shake_x": self.shake_x, "shake_y": self.shake_y,
            "arena_w": self.arena_w, "arena_h": self.arena_h,
            "map_data": self.map_data,
        }

    def snapshot(self):
        """获取战斗快照（非阻塞，优先使用缓存）"""
        # 先尝试读取缓存（无需获取 _lock）
        with self._snapshot_lock:
            cache = self._snapshot_cache
            if cache is not None:
                return cache

        # 缓存失效时，尝试非阻塞获取锁来重建快照
        # 如果无法立即获取锁，返回最后已知状态避免主线程阻塞
        if self._lock.acquire(blocking=False):
            try:
                sn = self._build_snapshot()
                with self._snapshot_lock:
                    self._snapshot_cache = sn
                return sn
            finally:
                self._lock.release()

        # 无法获取锁（后台线程正在更新），返回最后的快照或空快照
        with self._snapshot_lock:
            cache = self._snapshot_cache
            if cache is not None:
                return cache

        # 极端情况：完全没有缓存，返回最小有效快照
        return self._build_empty_snapshot()

    def _build_empty_snapshot(self):
        """构建最小空快照（防止渲染崩溃）"""
        return {
            "player": {
                "x": self.arena_w / 2, "y": self.arena_h / 2,
                "radius": 16, "hp": 1, "max_hp": 100,
                "alive": True, "invincible": 0.0,
                "prof": self.prof, "prof_data": self.prof_data,
                "mp": 0, "max_mp": 100,
            },
            "enemies": [],
            "projectiles": [],
            "tornadoes": [],
            "slashes": [],
            "kill_count": 0,
            "boss_unlocked": False,
            "boss_active": False,
            "damage_numbers": [],
            "shake_x": 0, "shake_y": 0,
            "arena_w": self.arena_w, "arena_h": self.arena_h,
            "map_data": self.map_data,
        }

    def status_snapshot(self):
        """获取战斗状态快照（轻量级，非阻塞）"""
        # 优先从缓存读取
        with self._snapshot_lock:
            if self._snapshot_cache is not None:
                cache = self._snapshot_cache
                return {
                    "player_hp": cache["player"]["hp"],
                    "player_max_hp": cache["player"]["max_hp"],
                    "player_alive": cache["player"]["alive"],
                    "kill_count": cache["kill_count"],
                    "boss_unlocked": cache["boss_unlocked"],
                    "boss_active": cache["boss_active"],
                    "end_reason": self.end_reason_safe,
                    "enemy_count": len(cache["enemies"]),
                    "map_name": self.map_data["name"],
                }

        # 缓存不可用时，直接读取基本属性（不获取 _lock，可能读到过渡值但不会阻塞）
        return {
            "player_hp": self.player_hp,
            "player_max_hp": self.player_max_hp,
            "player_alive": self.player_alive,
            "kill_count": self.kill_count,
            "boss_unlocked": self.boss_unlocked,
            "boss_active": self.boss_active,
            "end_reason": self.end_reason,
            "enemy_count": len([e for e in self.enemies if e.get("alive", False)]),
            "map_name": self.map_data["name"],
        }

    def _create_enemy(self, x, y, etype):
        self.enemy_id_counter += 1
        t = self.template
        if etype == "boss":
            b = t["boss"]
            return {
                "x": x, "y": y, "type": "boss",
                "hp": b["hp"], "max_hp": b["hp"],
                "damage": b["dmg"], "speed": b["speed"],
                "radius": b["size"], "color": b["color"],
                "name": b["name"], "alive": True,
                "eid": self.enemy_id_counter, "hit_flash": 0.0,
                "facing_left": False,
            }
        elif etype == "elite":
            mult = t["elite_mult"]
            return {
                "x": x, "y": y, "type": "elite",
                "hp": t["mob_hp"] * mult, "max_hp": t["mob_hp"] * mult,
                "damage": t["mob_dmg"] * mult,
                "speed": t["mob_speed"] * 0.8,
                "radius": 18, "color": t["elite_color"],
                "name": random.choice(t["elite_names"]),
                "alive": True, "eid": self.enemy_id_counter,
                "hit_flash": 0.0,
                "facing_left": False,
            }
        else:
            return {
                "x": x, "y": y, "type": "mob",
                "hp": t["mob_hp"], "max_hp": t["mob_hp"],
                "damage": t["mob_dmg"], "speed": t["mob_speed"],
                "radius": 10, "color": t["mob_color"],
                "name": random.choice(t["mob_names"]),
                "alive": True, "eid": self.enemy_id_counter,
                "hit_flash": 0.0,
                "facing_left": False,
            }

    def _update(self, dt):
        player = self.realm_data.player
        self.player_attack = player["attack"]
        self.player_defense = player["defense"]

        # 灵力恢复
        self.player_mp = min(self.player_max_mp, self.player_mp + self.mp_regen_rate * dt)

        self.player_attack_timer -= dt
        if self.player_invincible > 0:
            self.player_invincible -= dt

        # 自动攻击最近敌人
        alive_enemies = [e for e in self.enemies if e["alive"]]
        if self.player_attack_timer <= 0 and alive_enemies:
            nearest = min(alive_enemies,
                         key=lambda e: math.hypot(e["x"] - self.player_x, e["y"] - self.player_y))
            pd = self.prof_data

            # 基础攻击不消耗灵力，只有灵技才消耗

            if pd["attack_type"] == "projectile":
                dx = nearest["x"] - self.player_x
                dy = nearest["y"] - self.player_y
                dist = math.hypot(dx, dy) or 1
                speed = pd["attack_speed"] * 60
                dmg_mult = pd.get("dmg_mult", 1.0)  # 职业伤害乘区
                self.projectiles.append({
                    "x": self.player_x, "y": self.player_y,
                    "vx": dx / dist * speed, "vy": dy / dist * speed,
                    "damage": int(self.player_attack * 0.8 * dmg_mult),
                    "color": pd["attack_color"],
                    "alive": True, "lifetime": 2.0,
                })

            elif pd["attack_type"] == "aoe_persist":
                dmg_mult = pd.get("dmg_mult", 1.0)
                self.tornadoes.append({
                    "x": nearest["x"], "y": nearest["y"],
                    "damage": int(self.player_attack * 1.2 * dmg_mult),
                    "color": pd["attack_color"],
                    "radius": pd["aoe_range"], "alive": True,
                    "lifetime": 4.0, "age": 0.0, "angle": 0.0,
                    "hit_enemies": set(),
                })

            elif pd["attack_type"] == "slash":
                dmg_mult = pd.get("dmg_mult", 1.0)
                angle_to = math.atan2(nearest["y"] - self.player_y, nearest["x"] - self.player_x)
                self.slashes.append({
                    "x": self.player_x, "y": self.player_y,
                    "angle": angle_to,
                    "damage": int(self.player_attack * 1.0 * dmg_mult),
                    "color": pd["attack_color"],
                    "radius": pd["aoe_range"], "alive": True,
                    "lifetime": 0.4, "age": 0.0, "hit_enemies": set(),
                })

            self.player_attack_timer = pd["attack_interval"]

        # 弹道更新
        for p in self.projectiles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["lifetime"] -= dt
            if p["lifetime"] <= 0 or p["x"] < 0 or p["x"] > self.arena_w or p["y"] < 0 or p["y"] > self.arena_h:
                p["alive"] = False
        self.projectiles = [p for p in self.projectiles if p["alive"]]

        # 龙卷风更新
        for t in self.tornadoes:
            t["age"] += dt
            t["angle"] += dt * 3
            t["lifetime"] -= dt
            if t["lifetime"] <= 0:
                t["alive"] = False
        self.tornadoes = [t for t in self.tornadoes if t["alive"]]

        # 斩击更新
        for s in self.slashes:
            s["lifetime"] -= dt
            if s["lifetime"] <= 0:
                s["alive"] = False
        self.slashes = [s for s in self.slashes if s["alive"]]

        # 弹道碰撞检测
        dead_ids = []
        new_damage_numbers = []
        for p in self.projectiles:
            if not p["alive"]:
                continue
            for e in self.enemies:
                if not e["alive"]:
                    continue
                if math.hypot(p["x"] - e["x"], p["y"] - e["y"]) < e["radius"] + 6:
                    dmg = p["damage"]
                    e["hp"] -= dmg
                    e["hit_flash"] = 0.1
                    new_damage_numbers.append({
                        "x": e["x"], "y": e["y"], "value": dmg,
                        "color": p["color"], "lifetime": 0.8, "age": 0.0,
                    })
                    p["alive"] = False
                    if e["hp"] <= 0:
                        e["alive"] = False
                        dead_ids.append(e["eid"])
                    break

        for t in self.tornadoes:
            if not t["alive"]:
                continue
            for e in self.enemies:
                if not e["alive"] or e["eid"] in t["hit_enemies"]:
                    continue
                if math.hypot(t["x"] - e["x"], t["y"] - e["y"]) < t["radius"] + e["radius"]:
                    t["hit_enemies"].add(e["eid"])
                    dmg = t["damage"]
                    e["hp"] -= dmg
                    e["hit_flash"] = 0.1
                    new_damage_numbers.append({
                        "x": e["x"], "y": e["y"], "value": dmg,
                        "color": t["color"], "lifetime": 0.8, "age": 0.0,
                    })
                    if e["hp"] <= 0:
                        e["alive"] = False
                        dead_ids.append(e["eid"])

        for s in self.slashes:
            if not s["alive"]:
                continue
            for e in self.enemies:
                if not e["alive"] or e["eid"] in s["hit_enemies"]:
                    continue
                dist = math.hypot(s["x"] - e["x"], s["y"] - e["y"])
                if dist < s["radius"] + e["radius"]:
                    angle_to_enemy = math.atan2(e["y"] - s["y"], e["x"] - s["x"])
                    angle_diff = abs(angle_to_enemy - s["angle"])
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    if angle_diff < math.pi / 3:
                        s["hit_enemies"].add(e["eid"])
                        dmg = s["damage"]
                        e["hp"] -= dmg
                        e["hit_flash"] = 0.1
                        new_damage_numbers.append({
                            "x": e["x"], "y": e["y"], "value": dmg,
                            "color": s["color"], "lifetime": 0.8, "age": 0.0,
                        })
                        if e["hp"] <= 0:
                            e["alive"] = False
                            dead_ids.append(e["eid"])

        # 去重后处理死亡敌人（同一敌人可能被多个攻击源标记死亡）
        dead_ids = list(set(dead_ids))
        for eid in dead_ids:
            for e in self.enemies:
                if e["eid"] == eid:
                    self.kill_count += 1
                    drops = roll_drop(is_boss=(e["type"] == "boss"), realm_bonus=self.realm_index)
                    if e["type"] == "boss":
                        process_drops(drops, self.ling_shi_wallet)
                        self.boss_defeated = True
                        self.end_reason = "victory"
                    else:
                        process_drops(drops, self.ling_shi_wallet)
                    self.total_drops.extend(drops)
                    break
        self.enemies = [e for e in self.enemies if e["alive"]]

        # Boss解锁（击杀≥200且Boss未激活）
        if self.kill_count >= 200 and not self.boss_unlocked and not self.boss_active:
            self.boss_unlocked = True

        # 敌人生成（Boss战期间不刷新小怪）
        if not self.boss_active and not self.boss_defeated:
            self.spawn_timer -= dt
            alive_count = len([e for e in self.enemies if e["alive"]])
            if self.spawn_timer <= 0 and alive_count < self.max_enemies:
                side = random.randint(0, 3)
                if side == 0:
                    ex, ey = random.uniform(0, self.arena_w), -20
                elif side == 1:
                    ex, ey = random.uniform(0, self.arena_w), self.arena_h + 20
                elif side == 2:
                    ex, ey = -20, random.uniform(0, self.arena_h)
                else:
                    ex, ey = self.arena_w + 20, random.uniform(0, self.arena_h)

                is_elite = (self.kill_count > 0
                           and (self.kill_count + alive_count) % self.elite_threshold == 0
                           and self.elite_count < self.kill_count // self.elite_threshold + 1)

                etype = "elite" if is_elite else "mob"
                enemy = self._create_enemy(ex, ey, etype)
                if is_elite:
                    self.elite_count += 1
                self.enemies.append(enemy)

                self.spawn_interval = max(0.3, 0.8 - self.realm_index * 0.05)
                self.spawn_timer = self.spawn_interval

        # 敌人移动
        for e in self.enemies:
            if not e["alive"]:
                continue
            dx = self.player_x - e["x"]
            dy = self.player_y - e["y"]
            dist = math.hypot(dx, dy)
            if dist > 0:
                e["x"] += (dx / dist) * e["speed"] * 60 * dt
                e["y"] += (dy / dist) * e["speed"] * 60 * dt
            # 朝向：面朝主角
            e["facing_left"] = dx < 0
            if e["hit_flash"] > 0:
                e["hit_flash"] -= dt

        # 敌人碰撞玩家
        for e in self.enemies:
            if not e["alive"]:
                continue
            if math.hypot(self.player_x - e["x"], self.player_y - e["y"]) < self.player_radius + e["radius"]:
                if self.player_invincible <= 0:
                    self.player_hp -= e["damage"]
                    self.player_invincible = 0.3
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.player_alive = False
                        self.end_reason = "defeat"

        # Boss击败检查
        if self.boss_active and not self.boss_defeated:
            boss_alive = any(e["type"] == "boss" and e["alive"] for e in self.enemies)
            if not boss_alive:
                self.boss_defeated = True
                self.end_reason = "victory"

        # 伤害数字更新
        for dn in self.damage_numbers:
            dn["age"] += dt
            dn["y"] -= 30 * dt
        self.damage_numbers = [dn for dn in self.damage_numbers if dn["age"] < dn["lifetime"]]
        self.damage_numbers.extend(new_damage_numbers)

        if self.shake_timer > 0:
            self.shake_timer -= dt
            intensity = self.shake_timer * 12
            self.shake_x = random.uniform(-intensity, intensity)
            self.shake_y = random.uniform(-intensity, intensity)
        else:
            self.shake_x = self.shake_y = 0

    def activate_boss(self):
        """激活Boss：Boss刷新在屏幕正中，玩家刷新在Boss旁边中等距离"""
        with self._lock:
            if self.boss_active or not self.boss_unlocked or self.boss_defeated:
                return False
            self.boss_active = True
            self.shake_timer = 0.6
            # Boss在屏幕正中间
            bx, by = self.arena_w / 2, self.arena_h / 2 - 50
            boss = self._create_enemy(bx, by, "boss")
            self.enemies.append(boss)
            # 玩家刷新在Boss旁边（中等距离，右侧200px处）
            self.player_x = bx + 200
            self.player_y = by
            # 清除已有敌人（除Boss外）
            self.enemies = [boss]
            return True

    def _sim_loop(self):
        tick = 1.0 / 60.0
        start_time = self._start_time
        while True:
            if not self._running:
                break
            if start_time and time.time() - start_time > self._max_duration:
                with self._lock:
                    self._running = False
                    self.end_reason = "timeout"
                break
            try:
                # 在锁内更新游戏状态，然后构建快照
                with self._lock:
                    if not self._running or self.end_reason is not None:
                        break
                    self._update(tick)
                    snapshot_data = self._build_snapshot()

                # 在锁外更新快照缓存（减少锁持有时间）
                with self._snapshot_lock:
                    self._snapshot_cache = snapshot_data
            except Exception as e:
                print(f"❌ 后台战斗线程异常: {e}")
                import traceback
                traceback.print_exc()
                with self._lock:
                    self._running = False
                    self.end_reason = "error"
                break
            time.sleep(tick)

    def start(self):
        self._start_time = time.time()
        with self._lock:
            self._running = True
        self._thread = threading.Thread(target=self._sim_loop, daemon=True)
        self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False

    def wait_for_end(self, timeout=None):
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        return self.end_reason or "quit", self.total_drops


# ===== 生成艾瑞凯+普吉华 =====
def generate_linked_products():
    BASE = r'C:\Users\22522\Desktop\新建文件夹 (7)'
    DB = f'{BASE}\\每月流向制作\\门店+连锁进销存数据库'
    
    # This function will be called separately
    pass