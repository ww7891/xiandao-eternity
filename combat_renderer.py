"""
战斗场景渲染器 - 精灵图版
从 BackgroundCombat.snapshot() 数据渲染战斗画面
"""

import pygame
import math
import random
import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 预加载精灵（模块级缓存）
_sprite_cache = {}


def _load_sprite(path):
    if path in _sprite_cache:
        return _sprite_cache[path]
    try:
        img = pygame.image.load(path).convert_alpha()
        _sprite_cache[path] = img
        return img
    except:
        return None


class CombatRenderer:
    """战斗渲染器，从快照数据绘制战斗画面"""

    def __init__(self, screen, font_path):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.small_font = pygame.font.Font(font_path, 16)
        self.mid_font = pygame.font.Font(font_path, 22)
        self.big_font = pygame.font.Font(font_path, 28)

        self.prev_enemy_positions = {}
        self.render_particles = []
        self.render_damage_numbers = []

        # 背景缓存
        self._bg_cache = None
        self._bg_cache_key = None

        # 精灵预加载
        self.bg_bamboo = _load_sprite(os.path.join(ASSETS_DIR, "bg_bamboo.png"))
        self.sprite_player = _load_sprite(os.path.join(ASSETS_DIR, "sprites", "player_sprite.png"))
        self.sprite_wolf = _load_sprite(os.path.join(ASSETS_DIR, "sprites", "enemy_normal.png"))
        self.sprite_wolf_elite = _load_sprite(os.path.join(ASSETS_DIR, "sprites", "enemy_elite.png"))
        self.sprite_sword_fly = _load_sprite(os.path.join(ASSETS_DIR, "sword_fly.png"))
        self.sprite_tornado = _load_sprite(os.path.join(ASSETS_DIR, "tornado.png"))
        self.sprite_sword_blade = _load_sprite(os.path.join(ASSETS_DIR, "sword_blade.png"))

        # 动画计数器
        self._anim_tick = 0

    def _get_bg_surface(self, arena_w, arena_h, bg_color):
        cache_key = (arena_w, arena_h)
        if self._bg_cache is not None and self._bg_cache_key == cache_key:
            return self._bg_cache

        canvas = pygame.Surface((arena_w, arena_h))

        if self.bg_bamboo:
            # 缩放背景图填满整个区域
            scaled = pygame.transform.scale(self.bg_bamboo, (arena_w, arena_h))
            canvas.blit(scaled, (0, 0))
        else:
            # 降级：渐变背景
            dark = (max(0, bg_color[0] - 20), max(0, bg_color[1] - 15), max(0, bg_color[2] - 10))
            for i in range(0, arena_h, 3):
                ratio = i / arena_h
                r = int(bg_color[0] + (dark[0] - bg_color[0]) * ratio)
                g = int(bg_color[1] + (dark[1] - bg_color[1]) * ratio)
                b = int(bg_color[2] + (dark[2] - bg_color[2]) * ratio)
                pygame.draw.line(canvas, (r, g, b), (0, i), (arena_w, i + 3))

        self._bg_cache = canvas
        self._bg_cache_key = cache_key
        return canvas

    def render(self, snapshot):
        self._anim_tick += 1
        arena_w = snapshot["arena_w"]
        arena_h = snapshot["arena_h"]
        bg_color = snapshot["map_data"]["bg_color"]

        canvas = self._get_bg_surface(arena_w, arena_h, bg_color).copy()

        # --- 绘制顺序：弹道 → 龙卷风/斩击 → 敌人 → 玩家 → 伤害数字 → HUD ---
        for p in snapshot["projectiles"]:
            self._draw_projectile(canvas, p)

        for t in snapshot["tornadoes"]:
            self._draw_tornado(canvas, t)

        for s in snapshot["slashes"]:
            self._draw_slash(canvas, s)

        for e in snapshot["enemies"]:
            self._draw_enemy(canvas, e)

        pdata = snapshot["player"]
        if pdata["alive"]:
            if not (pdata["invincible"] > 0 and int(pdata["invincible"] * 10) % 2 == 0):
                self._draw_player(canvas, pdata, snapshot)

        for dn in snapshot.get("damage_numbers", []):
            self._draw_damage_number(canvas, dn)

        self._draw_hud(canvas, snapshot)

        shake_x = snapshot["shake_x"]
        shake_y = snapshot["shake_y"]
        self.screen.blit(canvas, (shake_x, shake_y))

    def _draw_player(self, canvas, pdata, snapshot):
        """绘制玩家角色 - 使用图片资源，御剑飞行动画"""
        x, y = pdata["x"], pdata["y"]
        prof = pdata["prof"]

        # 查找最近敌人以确定朝向
        nearest_enemy = None
        min_dist = float("inf")
        for e in snapshot.get("enemies", []):
            dx = e["x"] - x
            dy = e["y"] - y
            dist = dx * dx + dy * dy
            if dist < min_dist:
                min_dist = dist
                nearest_enemy = (dx, dy)

        # 朝向：有敌人时面对最近敌人，否则默认向右
        facing_right = True
        if nearest_enemy and nearest_enemy[0] > 0:
            facing_right = False

        # 御剑飞行上下摇晃动画
        bob_offset = int(3 * math.sin(self._anim_tick * 0.08))
        draw_y = int(y) + bob_offset

        if self.sprite_player:
            # 使用角色精灵图
            pw = int(self.sprite_player.get_width())
            ph = int(self.sprite_player.get_height())
            scaled = pygame.transform.scale(self.sprite_player, (pw, ph))

            if not facing_right:
                scaled = pygame.transform.flip(scaled, True, False)

            rr = scaled.get_rect(center=(int(x), draw_y))
            canvas.blit(scaled, rr)

            # HP条放在角色脚下（不挡住头部）
            bar_w = pw
            bar_h = 4
            bx = x - bar_w / 2
            by = draw_y + ph // 2 + 4
            ratio = max(0, pdata["hp"] / pdata["max_hp"])
            pygame.draw.rect(canvas, (30, 10, 10), (bx, by, bar_w, bar_h))
            pygame.draw.rect(canvas, (50, 200, 50), (bx, by, bar_w * ratio, bar_h))
            return

        # 降级：纯色圆形
        radius = pdata["radius"]
        base_color = (100, 180, 255)
        pygame.draw.circle(canvas, base_color, (int(x), int(y)), radius)
        pygame.draw.circle(canvas, (240, 230, 210), (int(x), int(y)), radius, 2)

        # HP条
        bar_w = radius * 2 + 6
        bar_h = 4
        bx = x - bar_w / 2
        by = y + radius + 6
        ratio = max(0, pdata["hp"] / pdata["max_hp"])
        pygame.draw.rect(canvas, (30, 10, 10), (bx, by, bar_w, bar_h))
        pygame.draw.rect(canvas, (50, 200, 50), (bx, by, bar_w * ratio, bar_h))

    def _draw_enemy(self, canvas, e):
        x, y = e["x"], e["y"]
        flash = e["hit_flash"] > 0

        if e["type"] == "boss":
            # Boss - 使用精英怪图片并放大
            if self.sprite_wolf_elite:
                bw = 120
                bh = int(bw * self.sprite_wolf_elite.get_height() / self.sprite_wolf_elite.get_width())
                sprite = pygame.transform.scale(self.sprite_wolf_elite, (bw, bh))
                if flash:
                    sprite = sprite.copy()
                    sprite.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
                if e.get("facing_left", False):
                    sprite = pygame.transform.flip(sprite, True, False)
                rr = sprite.get_rect(center=(int(x), int(y)))
                canvas.blit(sprite, rr)

                bar_w = bw
                bar_h = 8
                bx = x - bar_w / 2
                by = y - bh // 2 - 16
                ratio = max(0, e["hp"] / e["max_hp"])
                pygame.draw.rect(canvas, (30, 10, 10), (bx - 2, by - 2, bar_w + 4, bar_h + 4))
                pygame.draw.rect(canvas, (220, 50, 50), (bx, by, bar_w * ratio, bar_h))
                return

            # 降级
            r = e["radius"]
            pts = []
            for i in range(6):
                angle = math.pi / 6 + i * math.pi / 3
                px = x + math.cos(angle) * r * 0.85
                py = y + math.sin(angle) * r * 0.85
                pts.append((px, py))
            pygame.draw.polygon(canvas, (200, 100, 50), pts)
            pygame.draw.polygon(canvas, (120, 50, 20), pts, 3)

        elif e["type"] == "elite":
            # 精英怪 - 使用狼王图片
            if self.sprite_wolf_elite:
                bw = 80
                bh = int(bw * self.sprite_wolf_elite.get_height() / self.sprite_wolf_elite.get_width())
                sprite = pygame.transform.scale(self.sprite_wolf_elite, (bw, bh))
                if flash:
                    sprite = sprite.copy()
                    sprite.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
                if e.get("facing_left", False):
                    sprite = pygame.transform.flip(sprite, True, False)
                rr = sprite.get_rect(center=(int(x), int(y)))
                canvas.blit(sprite, rr)

                bar_w = bw
                bar_h = 5
                bx = x - bar_w / 2
                by = y - bh // 2 - 12
                ratio = max(0, e["hp"] / e["max_hp"])
                pygame.draw.rect(canvas, (30, 10, 10), (bx, by, bar_w, bar_h))
                pygame.draw.rect(canvas, (200, 180, 50), (bx, by, bar_w * ratio, bar_h))
                return

            # 降级
            r = e["radius"]
            glow = int(30 + 10 * math.sin(self._anim_tick * 0.06))
            base_color = (200, 100, 50)
            pygame.draw.circle(canvas, (*base_color, glow), (int(x), int(y)), r + 6, 2)
            pygame.draw.circle(canvas, base_color, (int(x), int(y)), r)

        else:
            # 普通小怪 - 使用像素狼
            if self.sprite_wolf:
                bw = 60
                bh = int(bw * self.sprite_wolf.get_height() / self.sprite_wolf.get_width())
                sprite = pygame.transform.scale(self.sprite_wolf, (bw, bh))
                if flash:
                    sprite = sprite.copy()
                    sprite.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)

                # 朝向玩家
                if e.get("facing_left", False):
                    sprite = pygame.transform.flip(sprite, True, False)

                rr = sprite.get_rect(center=(int(x), int(y)))
                canvas.blit(sprite, rr)

                bar_w = bw
                bar_h = 4
                bx = x - bar_w / 2
                by = y - bh // 2 - 10
                ratio = max(0, e["hp"] / e["max_hp"])
                pygame.draw.rect(canvas, (30, 10, 10), (bx, by, bar_w, bar_h))
                pygame.draw.rect(canvas, (50, 180, 50), (bx, by, bar_w * ratio, bar_h))
                return

            # 降级
            r = e["radius"]
            base_color = (150, 100, 180)
            pygame.draw.circle(canvas, base_color, (int(x), int(y)), r)
            pygame.draw.circle(canvas, (100, 60, 130), (int(x), int(y)), r, 2)

    def _draw_projectile(self, canvas, p):
        """简化弹道 - 使用飞剑精灵"""
        px, py = p["x"], p["y"]
        vx, vy = p["vx"], p["vy"]
        color = p.get("color", (200, 200, 100))
        angle = math.atan2(vy, vx)

        if self.sprite_sword_fly:
            # 使用飞剑精灵
            sw = 70
            sh = int(sw * self.sprite_sword_fly.get_height() / self.sprite_sword_fly.get_width())
            scaled = pygame.transform.scale(self.sprite_sword_fly, (sw, sh))
            # 旋转270度 + 剑尖朝向弹道方向
            rotated = pygame.transform.rotate(scaled, -math.degrees(angle) + 315)
            rr = rotated.get_rect(center=(int(px), int(py)))
            canvas.blit(rotated, rr)
            return

        # 降级：能量弹效果
        length = 18
        tip_x = px + math.cos(angle) * length
        tip_y = py + math.sin(angle) * length
        tail_x = px - math.cos(angle) * 6
        tail_y = py - math.sin(angle) * 6

        pygame.draw.line(canvas, (255, 255, 200), (int(tail_x), int(tail_y)),
                        (int(tip_x), int(tip_y)), 3)
        for i in range(3):
            mid_x = px + math.cos(angle) * (3 + i * 5)
            mid_y = py + math.sin(angle) * (3 + i * 5)
            alpha = 80 - i * 20
            pygame.draw.circle(canvas, (*color[:3], alpha), (int(mid_x), int(mid_y)), 4 - i)

    def _draw_tornado(self, canvas, t):
        tx, ty = t["x"], t["y"]
        color = t["color"]
        radius = t["radius"]
        angle = t["angle"]
        alpha = int(150 * min(1.0, t["lifetime"] / 2.0))

        if self.sprite_tornado:
            # 使用龙卷风精灵（不旋转）
            tw = int(radius * 3.0)
            th = int(tw * self.sprite_tornado.get_height() / self.sprite_tornado.get_width())
            scaled = pygame.transform.scale(self.sprite_tornado, (tw, th))
            scaled.set_alpha(alpha)
            rr = scaled.get_rect(center=(int(tx), int(ty)))
            canvas.blit(scaled, rr)
            return

        # 降级：环形特效
        for ring in range(3):
            ring_r = radius * (0.5 + ring * 0.3)
            for i in range(8):
                a = angle + i * math.pi * 2 / 8 + ring * 0.3
                ox = tx + math.cos(a) * ring_r
                oy = ty + math.sin(a) * ring_r
                r = radius * (0.2 + 0.1 * math.sin(t["age"] * 6 + i * 0.5 + ring))
                pygame.draw.circle(canvas, (*color[:3], alpha // (ring + 2)),
                                 (int(ox), int(oy)), int(r), 2)
        pygame.draw.circle(canvas, (*color[:3], alpha), (int(tx), int(ty)), 10)

    def _draw_slash(self, canvas, s):
        sx, sy = s["x"], s["y"]
        color = s["color"]
        radius = s["radius"]
        angle = s["angle"]
        alpha = int(180 * min(1.0, s["lifetime"] / 0.4))

        if self.sprite_sword_blade:
            # 扇形区域半透明指示（先绘制，刀在上面）
            start_angle = angle - math.pi / 3
            end_angle = angle + math.pi / 3
            fan_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            fan_points = [(radius, radius)]
            for i in range(17):
                a = start_angle + (end_angle - start_angle) * i / 16
                fan_points.append((radius + math.cos(a) * radius, radius + math.sin(a) * radius))
            pygame.draw.polygon(fan_surf, (*color[:3], alpha // 3), fan_points)
            canvas.blit(fan_surf, (int(sx - radius), int(sy - radius)))

            # 刀精灵：从右侧远处进入，沿弧形路径向左挥砍
            progress = max(0.0, min(1.0, s.get("age", 0) / max(s.get("lifetime", 0.4), 0.01)))
            
            # 弧形挥砍轨迹：从右侧远处开始，向左前方弧形挥砍
            # 初始位置在右侧远处，然后向扇形区域弧形移动
            start_angle = angle + math.pi / 2  # 右侧90度方向
            end_angle = angle - math.pi / 3    # 扇形左侧
            
            # 使用缓动函数让动画更流畅（先快后慢）
            eased_progress = 1 - (1 - progress) ** 3
            
            # 当前挥砍角度（从右向左）
            sweep_angle = start_angle - eased_progress * (start_angle - end_angle)
            
            # 刀的位置：沿着弧形轨迹移动
            # 初始距离远，逐渐靠近玩家
            start_dist = radius * 2.0  # 初始距离
            end_dist = radius * 0.6    # 最终距离
            blade_dist = start_dist - eased_progress * (start_dist - end_dist)
            
            blade_x = sx + math.cos(sweep_angle) * blade_dist
            blade_y = sy + math.sin(sweep_angle) * blade_dist
            
            bw = int(radius * 1.5)
            bh = int(bw * self.sprite_sword_blade.get_height() / self.sprite_sword_blade.get_width())
            scaled = pygame.transform.scale(self.sprite_sword_blade, (bw, bh))
            # 刀指向挥砍方向
            rotated = pygame.transform.rotate(scaled, -math.degrees(sweep_angle) + 45)
            rotated.set_alpha(alpha)
            rr = rotated.get_rect(center=(int(blade_x), int(blade_y)))
            canvas.blit(rotated, rr)
            return

        # 降级：几何扇形
        start_angle = angle - math.pi / 3
        end_angle = angle + math.pi / 3

        for layer in range(3):
            layer_r = radius * (0.5 + layer * 0.25)
            la = alpha // (layer * 2 + 1)
            points = [(sx, sy)]
            for i in range(17):
                a = start_angle + (end_angle - start_angle) * i / 16
                px = sx + math.cos(a) * layer_r
                py = sy + math.sin(a) * layer_r
                points.append((px, py))
            pygame.draw.polygon(canvas, (*color[:3], la), points)

    def _draw_damage_number(self, canvas, dn):
        x, y = int(dn["x"]), int(dn["y"])
        value = str(dn["value"])
        color = dn.get("color", (255, 255, 200))
        age = dn["age"]
        lifetime = dn["lifetime"]

        alpha = int(255 * (1 - age / lifetime))
        if alpha <= 0:
            return

        size = max(16, 24 - int(age * 10))
        font = pygame.font.Font(None, size)

        shadow = font.render(value, True, (0, 0, 0))
        shadow.set_alpha(alpha)
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            canvas.blit(shadow, (x + ox, y + oy))

        text = font.render(value, True, color[:3])
        text.set_alpha(alpha)
        canvas.blit(text, (x, y))

    def _draw_hud(self, canvas, snapshot):
        pdata = snapshot["player"]
        arena_w = snapshot["arena_w"]
        arena_h = snapshot["arena_h"]
        map_data = snapshot["map_data"]

        # HP条（左上角）
        bar_w, bar_h = 200, 16
        bar_x, bar_y = 15, 15
        hp_ratio = max(0, pdata["hp"] / pdata["max_hp"])
        pygame.draw.rect(canvas, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        hp_color = (50, 200, 50) if hp_ratio > 0.5 else (200, 200, 50) if hp_ratio > 0.2 else (200, 50, 50)
        pygame.draw.rect(canvas, hp_color, (bar_x, bar_y, bar_w * hp_ratio, bar_h))
        pygame.draw.rect(canvas, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
        hp_text = self.small_font.render(f"HP {int(pdata['hp'])}/{pdata['max_hp']}", True, (220, 220, 200))
        canvas.blit(hp_text, (bar_x + bar_w + 10, bar_y - 1))

        # 灵力条（左上角HP条下方）
        mp_bar_w, mp_bar_h = 200, 10
        mp_ratio = max(0, pdata.get("mp", 0) / max(pdata.get("max_mp", 100), 1))
        mp_y = bar_y + bar_h + 6
        pygame.draw.rect(canvas, (20, 20, 60), (bar_x, mp_y, mp_bar_w, mp_bar_h))
        pygame.draw.rect(canvas, (60, 100, 220), (bar_x, mp_y, mp_bar_w * mp_ratio, mp_bar_h))
        pygame.draw.rect(canvas, (180, 180, 200), (bar_x, mp_y, mp_bar_w, mp_bar_h), 1)
        mp_text = self.small_font.render(f"MP {int(pdata.get('mp',0))}/{pdata.get('max_mp',100)}", True, (180, 200, 220))
        canvas.blit(mp_text, (bar_x + mp_bar_w + 10, mp_y - 2))

        # 击杀计数
        kill_text = self.mid_font.render(f"击杀: {snapshot['kill_count']} / 200", True, (220, 200, 180))
        canvas.blit(kill_text, (bar_x, mp_y + mp_bar_h + 8))

        # Boss弹窗（击杀≥200且Boss未激活）
        if snapshot["boss_unlocked"] and not snapshot["boss_active"]:
            # 半透明遮罩
            overlay = pygame.Surface((400, 120), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            ox = (arena_w - 400) // 2
            oy = 40
            canvas.blit(overlay, (ox, oy))
            pygame.draw.rect(canvas, (255, 200, 50), (ox, oy, 400, 120), 2)

            boss_hint = self.big_font.render("击杀数已达200!", True, (255, 200, 50))
            canvas.blit(boss_hint, ((arena_w - boss_hint.get_width()) // 2, oy + 15))
            boss_hint2 = self.mid_font.render("按 B 键挑战 Boss !", True, (255, 220, 100))
            canvas.blit(boss_hint2, ((arena_w - boss_hint2.get_width()) // 2, oy + 55))
            boss_hint3 = self.small_font.render("按 ESC 返回主菜单", True, (180, 160, 140))
            canvas.blit(boss_hint3, ((arena_w - boss_hint3.get_width()) // 2, oy + 90))

        # 地图信息
        map_text = self.small_font.render(f"「{map_data['name']}」", True, (180, 170, 150))
        canvas.blit(map_text, (arena_w - map_text.get_width() - 15, 15))

        hint_text = self.small_font.render("WASD移动 | ESC退出", True, (150, 140, 130))
        canvas.blit(hint_text, (arena_w - hint_text.get_width() - 15, 38))


def draw_combat_status_indicator(screen, font_path, status, x=None, y=None):
    """非战斗界面的战斗状态指示器"""
    if status is None:
        return

    width = screen.get_width()
    indicator_w = 260
    indicator_h = 110
    if x is None:
        x = width - indicator_w - 15
    if y is None:
        y = screen.get_height() - indicator_h - 15

    panel = pygame.Surface((indicator_w, indicator_h), pygame.SRCALPHA)
    panel.fill((20, 15, 30, 200))
    pygame.draw.rect(panel, (80, 70, 100, 180), (0, 0, indicator_w, indicator_h), 2)

    small_font = pygame.font.Font(font_path, 16)
    mid_font = pygame.font.Font(font_path, 18)

    title = mid_font.render("战斗中", True, (255, 200, 100))
    panel.blit(title, (12, 8))

    hp_ratio = max(0, status["player_hp"] / status["player_max_hp"])
    hp_text = small_font.render(f"HP: {int(status['player_hp'])}/{status['player_max_hp']}", True, (200, 200, 200))
    panel.blit(hp_text, (12, 34))

    bar_w = 100
    bar_h = 6
    bx, by = 120, 38
    pygame.draw.rect(panel, (60, 20, 20), (bx, by, bar_w, bar_h))
    hp_color = (50, 200, 50) if hp_ratio > 0.5 else (200, 200, 50) if hp_ratio > 0.2 else (200, 50, 50)
    pygame.draw.rect(panel, hp_color, (bx, by, bar_w * hp_ratio, bar_h))

    info_text = small_font.render(
        f"击杀 {status['kill_count']} | 敌人 {status['enemy_count']}",
        True, (180, 170, 160))
    panel.blit(info_text, (12, 56))

    map_text = small_font.render(f"「{status['map_name']}」", True, (150, 140, 130))
    panel.blit(map_text, (12, 78))

    if status.get("boss_unlocked") and not status.get("boss_active"):
        boss_hint = small_font.render("Boss 可挑战", True, (255, 180, 50))
        panel.blit(boss_hint, (12, 98))
    elif status.get("boss_active"):
        boss_hint = small_font.render("Boss 战中", True, (255, 80, 80))
        panel.blit(boss_hint, (12, 98))

    screen.blit(panel, (x, y))