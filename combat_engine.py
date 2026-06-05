"""
核心战斗引擎
弹幕射击/幸存者类玩法
支持三种职业的差异化攻击
"""

import pygame
import sys
import os
import json
import math
import random
from collections import namedtuple

from profession_data import PROFESSIONS, get_profession
from enemy_data import get_realm_enemies, ENEMY_TEMPLATES
from drop_data import roll_drop, process_drops

# 导入精灵图加载器
try:
    from assets.sprites.image_loader import get_sprite_loader, SpritePaths, SpriteSizes
    SPRITE_LOADER = get_sprite_loader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sprites"))
    USE_SPRITES = True
except ImportError:
    SPRITE_LOADER = None
    USE_SPRITES = False
    print("警告: 精灵图加载器未找到，使用纯色图形绘制")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ==================== 游戏对象 ====================

class Player:
    """玩家"""
    def __init__(self, x, y, profession):
        self.x = x
        self.y = y
        self.radius = 16
        self.speed = 4.0
        self.prof = profession
        self.prof_data = PROFESSIONS[profession]

        # 从境界数据读取战斗属性
        import realm_data
        p = realm_data.player
        self.max_hp = p["hp"]
        self.hp = p["hp"]
        self.attack_power = p["attack"]
        self.defense = p["defense"]
        
        self.attack_timer = 0.0
        self.invincible = 0.0  # 受伤无敌时间

    def take_damage(self, dmg):
        if self.invincible > 0:
            return False
        self.hp -= dmg
        self.invincible = 0.3
        return self.hp <= 0

    def update(self, dt):
        if self.invincible > 0:
            self.invincible -= dt
        self.attack_timer -= dt

    def can_attack(self):
        return self.attack_timer <= 0

    def reset_attack(self):
        self.attack_timer = self.prof_data["attack_interval"]

    def draw(self, screen, facing_angle=0):
        prof = self.prof
        
        if USE_SPRITES and SPRITE_LOADER:
            # 使用精灵图绘制
            try:
                # 根据职业选择精灵图
                if prof == "sword":
                    sprite = SPRITE_LOADER.load_image(SpritePaths.PLAYER_SWORD_IDLE, SpriteSizes.PLAYER)
                elif prof == "mage":
                    sprite = SPRITE_LOADER.load_image(SpritePaths.PLAYER_MAGE_IDLE, SpriteSizes.PLAYER)
                elif prof == "blade":
                    sprite = SPRITE_LOADER.load_image(SpritePaths.PLAYER_BLADE_IDLE, SpriteSizes.PLAYER)
                else:
                    sprite = None
                    
                if sprite:
                    # 绘制精灵图
                    sprite_rect = sprite.get_rect(center=(int(self.x), int(self.y)))
                    screen.blit(sprite, sprite_rect)
                    
                    # 绘制HP条（在角色上方）
                    bar_w = self.radius * 2 + 6
                    bar_h = 4
                    bx = self.x - bar_w / 2
                    by = self.y - self.radius - 10
                    ratio = self.hp / self.max_hp
                    pygame.draw.rect(screen, (30, 10, 10), (bx, by, bar_w, bar_h))
                    pygame.draw.rect(screen, (50, 180, 50), (bx, by, bar_w * ratio, bar_h))
                    return
                    
            except Exception as e:
                print(f"精灵图绘制失败: {e}")
                # 降级到纯色绘制
        
        # 降级方案：纯色图形绘制
        # 职业特效光环
        if prof == "sword":
            t = pygame.time.get_ticks() * 0.002
            for i in range(3):
                a = t + i * math.pi * 2 / 3
                ox = self.x + math.cos(a) * (self.radius + 6)
                oy = self.y + math.sin(a) * (self.radius + 6)
                pygame.draw.circle(screen, (120, 160, 255, 50),
                                 (int(ox), int(oy)), 4)
            pygame.draw.circle(screen, (80, 120, 220, 30),
                             (int(self.x), int(self.y)), self.radius + 10, 1)
        elif prof == "mage":
            t = pygame.time.get_ticks() * 0.0015
            for i in range(4):
                a = t + i * math.pi / 2
                ox = self.x + math.cos(a) * (self.radius + 8)
                oy = self.y + math.sin(a) * (self.radius + 8)
                pygame.draw.circle(screen, (255, 100, 150, 50),
                                 (int(ox), int(oy)), 3)
            # 内圈符文
            pygame.draw.circle(screen, (200, 80, 130, 40),
                             (int(self.x), int(self.y)), self.radius + 4, 1)
        elif prof == "blade":
            t = pygame.time.get_ticks() * 0.001
            for i in range(2):
                a = t + i * math.pi
                ox = self.x + math.cos(a) * (self.radius + 10)
                oy = self.y + math.sin(a) * (self.radius + 10)
                pygame.draw.circle(screen, (255, 180, 50, 70),
                                 (int(ox), int(oy)), 5)

        # 玩家主体
        base_color = self.prof_data["color"]
        pygame.draw.circle(screen, base_color,
                         (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (240, 230, 210),
                         (int(self.x), int(self.y)), self.radius, 2)
        # 朝向指示
        fx = self.x + math.cos(facing_angle) * (self.radius + 6)
        fy = self.y + math.sin(facing_angle) * (self.radius + 6)
        pygame.draw.line(screen, (230, 210, 140),
                       (int(self.x), int(self.y)), (int(fx), int(fy)), 2)
        # HP条（在角色上方）
        bar_w = self.radius * 2 + 6
        bar_h = 4
        bx = self.x - bar_w / 2
        by = self.y - self.radius - 10
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (30, 10, 10), (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, (50, 180, 50), (bx, by, bar_w * ratio, bar_h))


class Projectile:
    """弹道（剑修的法剑）"""
    def __init__(self, x, y, target_x, target_y, damage, color, speed):
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy) or 1
        self.x = x
        self.y = y
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        self.damage = damage
        self.color = color
        self.alive = True
        self.lifetime = 2.0

    def update(self, dt, arena_w, arena_h):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        if (self.x < 0 or self.x > arena_w or
            self.y < 0 or self.y > arena_h or self.lifetime <= 0):
            self.alive = False

    def draw(self, screen):
        # 拖尾粒子
        for i in range(3):
            tx = self.x - self.vx * i * 0.5
            ty = self.y - self.vy * i * 0.5
            alpha = 60 - i * 15
            pygame.draw.circle(screen, (*self.color[:3], alpha),
                             (int(tx), int(ty)), 4 - i)
        # 飞剑主体
        angle = math.atan2(self.vy, self.vx)
        tip_x = self.x + math.cos(angle) * 14
        tip_y = self.y + math.sin(angle) * 14
        tail_x = self.x - math.cos(angle) * 8
        tail_y = self.y - math.sin(angle) * 8
        # 剑身
        pygame.draw.line(screen, (230, 230, 255),
                         (int(tail_x), int(tail_y)), (int(tip_x), int(tip_y)), 3)
        # 剑刃光
        pygame.draw.line(screen, self.color,
                         (int(self.x - math.cos(angle) * 4), int(self.y - math.sin(angle) * 4)),
                         (int(tip_x), int(tip_y)), 2)
        # 光晕
        pygame.draw.circle(screen, (*self.color[:3], 100),
                           (int(self.x), int(self.y)), 7)


class Tornado:
    """龙卷风（法修的AOE）"""
    def __init__(self, x, y, damage, color, radius):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.radius = radius
        self.alive = True
        self.lifetime = 4.0
        self.age = 0.0
        self.angle = 0.0
        self.hit_enemies = set()  # 已伤害的敌人ID，避免重复伤害

    def update(self, dt):
        self.age += dt
        self.angle += dt * 3
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        alpha = int(180 * min(1.0, self.lifetime / 2.0))
        # 多层旋转环
        for ring in range(3):
            ring_r = self.radius * (0.5 + ring * 0.3)
            for i in range(8):
                offset_angle = self.angle + i * math.pi * 2 / 8 + ring * 0.3
                ox = self.x + math.cos(offset_angle) * ring_r
                oy = self.y + math.sin(offset_angle) * ring_r
                r = self.radius * (0.2 + 0.1 * math.sin(self.age * 6 + i * 0.5 + ring))
                pygame.draw.circle(screen, (*self.color[:3], alpha // (ring + 2)),
                                 (int(ox), int(oy)), int(r), 2)
        # 中心漩涡
        swirl_r = self.radius * 0.4
        for i in range(4):
            a = self.angle + i * math.pi / 2
            sx = self.x + math.cos(a) * swirl_r
            sy = self.y + math.sin(a) * swirl_r
            pygame.draw.circle(screen, (*self.color[:3], alpha // 2),
                             (int(sx), int(sy)), int(swirl_r * 0.3))
        # 核心
        pygame.draw.circle(screen, (*self.color[:3], alpha),
                         (int(self.x), int(self.y)), 10)


class SlashEffect:
    """刀修的斩击特效"""
    def __init__(self, x, y, angle, damage, color, radius):
        self.x = x
        self.y = y
        self.angle = angle  # 朝向
        self.damage = damage
        self.color = color
        self.radius = radius
        self.alive = True
        self.lifetime = 0.4
        self.hit_enemies = set()

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        alpha = int(200 * min(1.0, self.lifetime / 0.4))
        start_angle = self.angle - math.pi / 3
        end_angle = self.angle + math.pi / 3
        # 扇形填充 - 多层
        for layer in range(3):
            layer_r = self.radius * (0.5 + layer * 0.25)
            la = alpha // (layer * 2 + 1)
            points = [(self.x, self.y)]
            steps = 16
            for i in range(steps + 1):
                a = start_angle + (end_angle - start_angle) * i / steps
                px = self.x + math.cos(a) * layer_r
                py = self.y + math.sin(a) * layer_r
                points.append((px, py))
            clr = (*self.color[:3], la)
            pygame.draw.polygon(screen, clr, points)
        # 弧线光刃
        for i in range(20):
            a = start_angle + (end_angle - start_angle) * i / 19
            x1 = self.x + math.cos(a) * self.radius * 0.4
            y1 = self.y + math.sin(a) * self.radius * 0.4
            x2 = self.x + math.cos(a) * self.radius
            y2 = self.y + math.sin(a) * self.radius
            line_a = int(alpha * (0.5 + 0.5 * math.sin(i / 19 * math.pi)))
            pygame.draw.line(screen, (*self.color[:3], line_a),
                           (int(x1), int(y1)), (int(x2), int(y2)), 3)
        # 边缘闪光
        for _ in range(6):
            a = random.uniform(start_angle, end_angle)
            r = random.uniform(self.radius * 0.6, self.radius)
            sx = self.x + math.cos(a) * r
            sy = self.y + math.sin(a) * r
            pygame.draw.circle(screen, (255, 255, 200, min(255, alpha + 40)),
                             (int(sx), int(sy)), 2)


class Enemy:
    """敌人"""
    _id_counter = 0

    def __init__(self, x, y, enemy_type, template):
        Enemy._id_counter += 1
        self.eid = Enemy._id_counter
        self.x = x
        self.y = y
        self.type = enemy_type  # "mob", "elite", "boss"
        self.name = random.choice(template["mob_names"])

        if enemy_type == "boss":
            b = template["boss"]
            self.hp = b["hp"]
            self.max_hp = b["hp"]
            self.damage = b["dmg"]
            self.speed = b["speed"]
            self.radius = b["size"]
            self.color = b["color"]
            self.name = b["name"]
        elif enemy_type == "elite":
            mult = template["elite_mult"]
            self.hp = template["mob_hp"] * mult
            self.max_hp = self.hp
            self.damage = template["mob_dmg"] * mult
            self.speed = template["mob_speed"] * 0.8
            self.radius = 18
            self.color = template["elite_color"]
            self.name = random.choice(template["elite_names"])
        else:
            self.hp = template["mob_hp"]
            self.max_hp = template["mob_hp"]
            self.damage = template["mob_dmg"]
            self.speed = template["mob_speed"]
            self.radius = 10
            self.color = template["mob_color"]

        self.alive = True
        self.hit_flash = 0.0

    def move_toward(self, target_x, target_y, dt):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed * 60 * dt
            self.y += (dy / dist) * self.speed * 60 * dt

    def take_damage(self, dmg):
        self.hp -= dmg
        self.hit_flash = 0.1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def update(self, dt):
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def draw(self, screen):
        if not self.alive:
            return

        flash = self.hit_flash > 0
        base_color = (255, 255, 255) if flash else self.color
        dark = tuple(max(0, c - 60) for c in base_color)

        # 尝试使用精灵图绘制
        if USE_SPRITES and SPRITE_LOADER:
            try:
                if self.type == "boss":
                    sprite = SPRITE_LOADER.load_image(SpritePaths.ENEMY_BOSS, SpriteSizes.ENEMY_BOSS)
                elif self.type == "elite":
                    sprite = SPRITE_LOADER.load_image(SpritePaths.ENEMY_ELITE, SpriteSizes.ENEMY_ELITE)
                else:
                    sprite = SPRITE_LOADER.load_image(SpritePaths.ENEMY_MOB, SpriteSizes.ENEMY_MOB)
                    
                if sprite:
                    sprite_rect = sprite.get_rect(center=(int(self.x), int(self.y)))
                    screen.blit(sprite, sprite_rect)
                    
                    # HP条
                    bar_w = self.radius * 2 + 4
                    bar_h = 4
                    bx = self.x - bar_w / 2
                    by = self.y - self.radius - 10
                    ratio = max(0, self.hp / self.max_hp)
                    pygame.draw.rect(screen, (30, 10, 10), (bx, by, bar_w, bar_h))
                    pygame.draw.rect(screen, (200, 180, 50), (bx, by, bar_w * ratio, bar_h))
                    return
                    
            except Exception as e:
                print(f"敌人精灵图绘制失败: {e}")
                # 降级到纯色绘制

        if self.type == "boss":
            # Boss: 大型六边形 + 内圈 + 外发光
            r = self.radius
            # 外发光
            glow_surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
            for i in range(6, 1, -1):
                alpha = 20 // i
                pygame.draw.circle(glow_surf, (*base_color, alpha), (r * 3 // 2, r * 3 // 2), r + i * 3)
            screen.blit(glow_surf, (int(self.x - r * 3 // 2), int(self.y - r * 3 // 2)))

            # 主体 - 六边形
            pts = []
            for i in range(6):
                angle = math.pi / 6 + i * math.pi / 3
                px = self.x + math.cos(angle) * r * 0.85
                py = self.y + math.sin(angle) * r * 0.85
                pts.append((px, py))
            pygame.draw.polygon(screen, base_color, pts)
            pygame.draw.polygon(screen, dark, pts, 3)
            # 内核
            pygame.draw.circle(screen, dark, (int(self.x), int(self.y)), int(r * 0.4))
            pygame.draw.circle(screen, (80, 20, 20), (int(self.x), int(self.y)), int(r * 0.2))

            # HP条 - 粗大带装饰
            bar_w = self.radius * 3
            bar_h = 8
            bx = self.x - bar_w / 2
            by = self.y - self.radius - 18
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, (30, 10, 10), (bx - 2, by - 2, bar_w + 4, bar_h + 4))
            hp_color = (220, 50, 50) if ratio < 0.3 else (220, 160, 30) if ratio < 0.6 else (180, 50, 50)
            pygame.draw.rect(screen, hp_color, (bx, by, bar_w * ratio, bar_h))
            pygame.draw.rect(screen, (180, 150, 100), (bx, by, bar_w, bar_h), 1)

        elif self.type == "elite":
            # 精英: 带刺圆形 + 光环旋转
            r = self.radius
            # 外光环
            glow_a = int(30 + 10 * math.sin(pygame.time.get_ticks() * 0.004))
            pygame.draw.circle(screen, (*base_color, glow_a),
                             (int(self.x), int(self.y)), r + 6, 2)
            # 主体
            pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), r)
            # 刺
            for i in range(5):
                angle = math.pi * i * 2 / 5 + pygame.time.get_ticks() * 0.001
                tx = self.x + math.cos(angle) * r * 0.9
                ty = self.y + math.sin(angle) * r * 0.9
                ex = self.x + math.cos(angle) * (r + 4)
                ey = self.y + math.sin(angle) * (r + 4)
                pygame.draw.line(screen, dark, (tx, ty), (ex, ey), 2)
            pygame.draw.circle(screen, dark, (int(self.x), int(self.y)), r, 2)

            # HP条
            bar_w = self.radius * 2 + 4
            bar_h = 4
            bx = self.x - bar_w / 2
            by = self.y - self.radius - 10
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, (30, 10, 10), (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, (200, 180, 50), (bx, by, bar_w * ratio, bar_h))

        else:
            # 小怪: 带眼珠的圆形
            r = self.radius
            pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), r)
            pygame.draw.circle(screen, dark, (int(self.x), int(self.y)), r, 2)
            # 眼睛方向（朝向玩家 - 通过简单偏移模拟）
            eye_off_x = math.cos(pygame.time.get_ticks() * 0.002) * 2
            eye_off_y = math.sin(pygame.time.get_ticks() * 0.002) * 2
            eye_x = int(self.x + eye_off_x)
            eye_y = int(self.y - r * 0.15 + eye_off_y)
            pygame.draw.circle(screen, (255, 255, 255), (eye_x - 2, eye_y - 1), 3)
            pygame.draw.circle(screen, (255, 255, 255), (eye_x + 2, eye_y - 1), 3)
            pygame.draw.circle(screen, (20, 15, 10), (eye_x - 2, eye_y - 1), 1.5)
            pygame.draw.circle(screen, (20, 15, 10), (eye_x + 2, eye_y - 1), 1.5)


class DamageNumber:
    """伤害数字"""
    def __init__(self, x, y, value, color=(255, 200, 100)):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.lifetime = 0.8
        self.age = 0.0
        self.base_x = x  # 初始x，用于飘浮摆动

    def update(self, dt):
        self.age += dt
        self.y -= 40 * dt
        # 左右微摆
        self.x = self.base_x + math.sin(self.age * 4) * 8

    @property
    def alive(self):
        return self.age < self.lifetime

    def draw(self, screen, font):
        alpha = int(255 * (1 - self.age / self.lifetime))
        scale = 1.0 + self.age * 0.3  # 逐渐放大
        # 描边阴影
        shadow = font.render(str(self.value), True, (20, 15, 10))
        text = font.render(str(self.value), True, (*self.color[:3], min(255, alpha)))
        sw, sh = shadow.get_size()
        sx = int(self.x - sw * scale / 2)
        sy = int(self.y - sh * scale / 2)
        s = pygame.transform.scale(shadow, (int(sw * scale), int(sh * scale)))
        t = pygame.transform.scale(text, (int(sw * scale), int(sh * scale)))
        screen.blit(s, (sx + 2, sy + 2))
        screen.blit(t, (sx, sy))


class Particle:
    """通用粒子特效"""
    def __init__(self, x, y, vx, vy, lifetime, color, size=3, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.size = size
        self.shrink = shrink

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.96
        self.vy *= 0.96

    @property
    def alive(self):
        return self.age < self.lifetime

    def draw(self, screen):
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))
        size = self.size * (1 - progress * 0.7) if self.shrink else self.size
        if size < 0.5:
            return
        pygame.draw.circle(screen, (*self.color[:3], alpha),
                         (int(self.x), int(self.y)), max(1, int(size)))


def spawn_death_particles(x, y, color, count=12):
    """生成死亡粒子"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 220)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(0.3, 0.8)
        size = random.uniform(2, 5)
        particles.append(Particle(x, y, vx, vy, lifetime, color, size))
    return particles


def spawn_spark_particles(x, y, color, count=8):
    """生成火花粒子"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(40, 120)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(0.15, 0.4)
        particles.append(Particle(x, y, vx, vy, lifetime, color, random.uniform(1.5, 3.5)))
    return particles


# ==================== 战斗场景 ====================

def run_combat(screen, map_id):
    """运行战斗，返回 (result, drops_summary)
    result: "victory" / "defeat" / "quit"
    """
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()
    font_path = config["font"]["primary"]

    from adventure_data import get_map
    map_data = get_map(map_id)
    if map_data is None:
        return "quit", []

    realm_index = map_data["realm"]
    template = get_realm_enemies(realm_index)
    arena_w, arena_h = width, height

    # 创建玩家
    prof = get_profession()
    if prof is None:
        return "quit", []
    player = Player(arena_w // 2, arena_h // 2, prof["id"])

    # 游戏对象列表
    enemies = []
    projectiles = []
    tornadoes = []
    slashes = []
    damage_numbers = []
    particles = []

    # 追踪数据
    kill_count = 0
    elite_count = 0
    boss_unlocked = False
    boss_active = False
    boss_defeated = False
    total_drops = []
    spawn_timer = 0.0
    spawn_interval = 0.8
    max_enemies = 20
    elite_threshold = 10  # 每10个怪出1个精英

    # 朝向（用于刀修）
    facing_angle = 0.0
    # 屏幕震动
    shake_x = 0
    shake_y = 0
    shake_timer = 0.0

    # 字体
    small_font = pygame.font.Font(font_path, 16)
    mid_font = pygame.font.Font(font_path, 22)
    big_font = pygame.font.Font(font_path, 28)
    damage_font = pygame.font.Font(font_path, 24)  # 伤害数字专用字体

    # 地图背景色
    bg_color = map_data["bg_color"]

    result = None
    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)

        # ===== 输入处理 =====
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # 归一化斜向移动
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        player.x = max(player.radius, min(arena_w - player.radius, player.x + dx * player.speed * 60 * dt))
        player.y = max(player.radius, min(arena_h - player.radius, player.y + dy * player.speed * 60 * dt))

        # 更新朝向
        if dx != 0 or dy != 0:
            facing_angle = math.atan2(dy, dx)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", total_drops
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit", total_drops
                # Boss挑战快捷键
                if event.key == pygame.K_b and boss_unlocked and not boss_active:
                    boss_active = True
                    shake_timer = 0.6  # Boss登场震动
                    # 生成Boss
                    side = random.randint(0, 3)
                    if side == 0:
                        bx, by = arena_w // 2, -30
                    elif side == 1:
                        bx, by = arena_w // 2, arena_h + 30
                    elif side == 2:
                        bx, by = -30, arena_h // 2
                    else:
                        bx, by = arena_w + 30, arena_h // 2
                    boss = Enemy(bx, by, "boss", template)
                    enemies.append(boss)
                    print("[Combat] Boss挑战开始!")

        # ===== 玩家更新 =====
        player.update(dt)

        # 自动攻击
        if player.can_attack() and enemies:
            # 找最近敌人
            nearest = min(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            prof_data = player.prof_data
            
            # 计算实际伤害：攻击力 × 职业系数
            if prof_data["id"] == "sword":
                damage = int(player.attack_power * 0.8)  # 剑修：80%攻击力
            elif prof_data["id"] == "mage":
                damage = int(player.attack_power * 1.2)  # 法修：120%攻击力
            elif prof_data["id"] == "blade":
                damage = int(player.attack_power * 1.0)  # 刀修：100%攻击力
            else:
                damage = player.attack_power

            if prof_data["attack_type"] == "projectile":
                # 剑修：射法剑
                proj = Projectile(
                    player.x, player.y,
                    nearest.x, nearest.y,
                    damage,
                    prof_data["attack_color"],
                    prof_data["attack_speed"] * 60
                )
                projectiles.append(proj)

            elif prof_data["attack_type"] == "aoe_persist":
                # 法修：释放龙卷风在最近敌人位置
                t = Tornado(
                    nearest.x, nearest.y,
                    damage,
                    prof_data["attack_color"],
                    prof_data["aoe_range"]
                )
                tornadoes.append(t)

            elif prof_data["attack_type"] == "slash":
                # 刀修：扇形斩击
                s = SlashEffect(
                    player.x, player.y,
                    facing_angle,
                    damage,
                    prof_data["attack_color"],
                    prof_data["aoe_range"]
                )
                slashes.append(s)

            player.reset_attack()

        # ===== 敌人生成 =====
        if not boss_active:
            spawn_timer -= dt
            if spawn_timer <= 0 and len(enemies) < max_enemies:
                # 生成位置：屏幕边缘
                side = random.randint(0, 3)
                if side == 0:  # 上
                    ex, ey = random.uniform(0, arena_w), -20
                elif side == 1:  # 下
                    ex, ey = random.uniform(0, arena_w), arena_h + 20
                elif side == 2:  # 左
                    ex, ey = -20, random.uniform(0, arena_h)
                else:  # 右
                    ex, ey = arena_w + 20, random.uniform(0, arena_h)

                # 精英怪逻辑：每10个普通怪出1个精英
                is_elite = (kill_count > 0 and (kill_count + len(enemies)) % elite_threshold == 0
                           and elite_count < kill_count // elite_threshold + 1)

                etype = "elite" if is_elite else "mob"
                enemy = Enemy(ex, ey, etype, template)
                if is_elite:
                    elite_count += 1
                enemies.append(enemy)

                spawn_interval = max(0.3, 0.8 - realm_index * 0.05)
                spawn_timer = spawn_interval

        # ===== 弹道更新 =====
        for p in projectiles:
            p.update(dt, arena_w, arena_h)
        projectiles = [p for p in projectiles if p.alive]

        # ===== 龙卷风更新 =====
        for t in tornadoes:
            t.update(dt)
        tornadoes = [t for t in tornadoes if t.alive]

        # ===== 斩击更新 =====
        for s in slashes:
            s.update(dt)
        slashes = [s for s in slashes if s.alive]

        # ===== 弹道碰撞检测 =====
        dead_enemies = []
        for p in projectiles:
            if not p.alive:
                continue
            for e in enemies:
                if not e.alive:
                    continue
                if math.hypot(p.x - e.x, p.y - e.y) < e.radius + 6:
                    # 命中火花
                    particles.extend(spawn_spark_particles(e.x, e.y, p.color, 6))
                    killed = e.take_damage(p.damage)
                    dn = DamageNumber(e.x, e.y, p.damage)
                    damage_numbers.append(dn)
                    p.alive = False
                    if killed:
                        dead_enemies.append(e)
                    break

        # ===== 龙卷风碰撞检测 =====
        for t in tornadoes:
            if not t.alive:
                continue
            for e in enemies:
                if not e.alive or e.eid in t.hit_enemies:
                    continue
                if math.hypot(t.x - e.x, t.y - e.y) < t.radius + e.radius:
                    # 龙卷风命中火花
                    particles.extend(spawn_spark_particles(e.x, e.y, (180, 220, 255), 4))
                    t.hit_enemies.add(e.eid)
                    killed = e.take_damage(t.damage)
                    dn = DamageNumber(e.x, e.y, t.damage, (180, 220, 255))
                    damage_numbers.append(dn)
                    if killed:
                        dead_enemies.append(e)

        # ===== 斩击碰撞检测 =====
        for s in slashes:
            if not s.alive:
                continue
            for e in enemies:
                if not e.alive or e.eid in s.hit_enemies:
                    continue
                dist = math.hypot(s.x - e.x, s.y - e.y)
                if dist < s.radius + e.radius:
                    # 检查角度
                    angle_to_enemy = math.atan2(e.y - s.y, e.x - s.x)
                    angle_diff = abs(angle_to_enemy - s.angle)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    if angle_diff < math.pi / 3:
                        # 斩击命中火花
                        particles.extend(spawn_spark_particles(e.x, e.y, (255, 200, 100), 5))
                        s.hit_enemies.add(e.eid)
                        killed = e.take_damage(s.damage)
                        dn = DamageNumber(e.x, e.y, s.damage, (255, 200, 100))
                        damage_numbers.append(dn)
                        if killed:
                            dead_enemies.append(e)

        # ===== 处理死亡敌人 =====
        for e in dead_enemies:
            # 死亡粒子
            particles.extend(spawn_death_particles(e.x, e.y, e.color, 15 if e.type == "boss" else 8))
            enemies.remove(e)
            kill_count += 1
            # 掉落
            is_boss_kill = e.type == "boss"
            drops = roll_drop(is_boss=is_boss_kill, realm_bonus=realm_index)
            if is_boss_kill:
                process_drops(drops)
            total_drops.extend(drops)

        # ===== Boss解锁检查 =====
        if kill_count >= 200 and not boss_unlocked and not boss_active:
            boss_unlocked = True

        # ===== 敌人移动 =====
        for e in enemies:
            e.move_toward(player.x, player.y, dt)
            e.update(dt)

        # ===== 敌人碰撞玩家 =====
        for e in enemies:
            if not e.alive:
                continue
            if math.hypot(player.x - e.x, player.y - e.y) < player.radius + e.radius:
                dead = player.take_damage(e.damage)
                if dead:
                    result = "defeat"
                    running = False

        # ===== Boss击败检查 =====
        if boss_active and not boss_defeated:
            boss_alive = any(e.type == "boss" and e.alive for e in enemies)
            if not boss_alive:
                boss_defeated = True
                result = "victory"
                running = False

        # ===== 震动更新 =====
        if shake_timer > 0:
            shake_timer -= dt
            intensity = shake_timer * 12
            shake_x = random.uniform(-intensity, intensity)
            shake_y = random.uniform(-intensity, intensity)
        else:
            shake_x = shake_y = 0

        # ===== 粒子更新 =====
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.alive]

        # ===== 伤害数字更新 =====
        for dn in damage_numbers:
            dn.update(dt)
        damage_numbers = [dn for dn in damage_numbers if dn.alive]

        # ===== HP检测 =====
        if player.hp <= 0:
            result = "defeat"
            running = False

        # ===== 绘制 =====
        # 临时画布（便于震动效果）
        canvas = pygame.Surface((arena_w, arena_h))
        # 背景渐变
        dark = (max(0, bg_color[0] - 20), max(0, bg_color[1] - 15), max(0, bg_color[2] - 10))
        for i in range(0, arena_h, 3):
            ratio = i / arena_h
            r = int(bg_color[0] + (dark[0] - bg_color[0]) * ratio)
            g = int(bg_color[1] + (dark[1] - bg_color[1]) * ratio)
            b = int(bg_color[2] + (dark[2] - bg_color[2]) * ratio)
            pygame.draw.line(canvas, (r, g, b), (0, i), (arena_w, i))
            if i + 1 < arena_h:
                pygame.draw.line(canvas, (r, g, b), (0, i+1), (arena_w, i+1))
            if i + 2 < arena_h:
                pygame.draw.line(canvas, (r, g, b), (0, i+2), (arena_w, i+2))

        # 水墨网格
        grid_color = (bg_color[0] + 15, bg_color[1] + 12, bg_color[2] + 10)
        for gx in range(0, arena_w, 60):
            alpha = 40 + int(15 * math.sin(gx * 0.01))
            pygame.draw.line(canvas, (*grid_color, alpha), (gx, 0), (gx, arena_h), 1)
        for gy in range(0, arena_h, 60):
            alpha = 40 + int(15 * math.sin(gy * 0.01))
            pygame.draw.line(canvas, (*grid_color, alpha), (0, gy), (arena_w, gy), 1)

        # 粒子
        for p in particles:
            p.draw(canvas)

        # 龙卷风
        for t in tornadoes:
            t.draw(canvas)

        # 斩击
        for s in slashes:
            s.draw(canvas)

        # 弹道
        for p in projectiles:
            p.draw(canvas)

        # 敌人
        for e in enemies:
            e.draw(canvas)

        # 玩家
        if player.invincible > 0 and int(player.invincible * 10) % 2 == 0:
            pass
        else:
            player.draw(canvas, facing_angle)

        # 伤害数字
        for dn in damage_numbers:
            dn.draw(canvas, damage_font)

        # 震动偏移
        screen.blit(canvas, (shake_x, shake_y))

        # ===== HUD =====
        # HP条
        bar_w, bar_h = 200, 16
        bar_x, bar_y = 15, 15
        hp_ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(canvas, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        hp_color = (50, 200, 50) if hp_ratio > 0.5 else (200, 200, 50) if hp_ratio > 0.2 else (200, 50, 50)
        pygame.draw.rect(canvas, hp_color, (bar_x, bar_y, bar_w * hp_ratio, bar_h))
        pygame.draw.rect(canvas, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
        hp_text = small_font.render(f"HP {player.hp}/{player.max_hp}", True, (220, 220, 200))
        canvas.blit(hp_text, (bar_x + bar_w + 10, bar_y - 1))

        # 击杀计数
        kill_text = mid_font.render(f"击杀: {kill_count} / 200", True, (220, 200, 180))
        canvas.blit(kill_text, (bar_x, bar_y + bar_h + 8))

        # Boss状态
        if boss_unlocked and not boss_active:
            boss_hint = mid_font.render("按 B 键 挑战 Boss !", True, (255, 200, 50))
            canvas.blit(boss_hint, ((arena_w - boss_hint.get_width()) // 2, 80))

        # 地图信息
        map_text = small_font.render(f"「{map_data['name']}」", True, (180, 170, 150))
        canvas.blit(map_text, (arena_w - map_text.get_width() - 15, 15))

        # 操作提示
        hint_text = small_font.render("WASD移动 | ESC退出", True, (150, 140, 130))
        canvas.blit(hint_text, (arena_w - hint_text.get_width() - 15, 38))

        pygame.display.flip()

    # ===== 战斗结束 =====
    if result == "victory":
        # 解锁下一张地图
        from adventure_data import unlock_map
        next_map_id = map_id + 1
        if next_map_id < len(MAPS):
            unlock_map(next_map_id)
        # 处理Boss掉落
        boss_drops = roll_drop(is_boss=True, realm_bonus=realm_index)
        process_drops(boss_drops)
        total_drops.extend(boss_drops)

    return result, total_drops