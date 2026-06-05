#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙道永恒 - 标题界面
水墨风格启动画面，包含游戏标题和开始按钮
"""

import pygame
import math
import random
from font_utils import FontManager

CONFIG_PATH = "config.json"


class TitleScreen:
    """标题启动界面"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)

        import json
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.colors = self.config.get("colors", {})

        self.running = True
        self.next_state = None
        self.start_alpha = 0
        self.start_phase = 0

        # 画按钮
        btn_w, btn_h = 220, 60
        self.start_button = pygame.Rect(
            (screen_width - btn_w) // 2,
            screen_height - 220,
            btn_w, btn_h
        )
        self.btn_hovered = False
        
        # 读取存档按钮
        self.load_button = pygame.Rect(
            (screen_width - btn_w) // 2,
            screen_height - 145,
            btn_w, btn_h
        )
        self.load_hovered = False

        # 水墨粒子（墨点）
        self.ink_particles = []
        for _ in range(20):
            self.ink_particles.append({
                "x": random.randint(0, screen_width),
                "y": random.randint(screen_height // 2, screen_height),
                "size": random.randint(2, 6),
                "speed": random.uniform(0.3, 1.2),
                "alpha": random.randint(30, 80)
            })

        # 云层粒子
        self.clouds = []
        for _ in range(6):
            self.clouds.append({
                "x": random.randint(-200, screen_width + 200),
                "y": random.randint(50, 250),
                "speed": random.uniform(0.2, 0.6),
                "scale": random.uniform(0.6, 1.5),
                "alpha": random.randint(20, 60)
            })

        self.background_cache = None

        print("水墨标题界面初始化完成")

    def create_landscape_background(self):
        """创建山水画背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # 底色 - 宣纸米白
        bg.fill((245, 240, 228))

        # 天空渐变（淡墨色）
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            if ratio < 0.5:
                r = int(220 + 25 * ratio)
                g = int(215 + 30 * ratio)
                b = int(205 + 40 * ratio)
            else:
                r = int(232 - 30 * (ratio - 0.5))
                g = int(230 - 25 * (ratio - 0.5))
                b = int(225 - 15 * (ratio - 0.5))
            pygame.draw.line(bg, (r, g, b), (0, y), (self.screen_width, y))

        # 远山（淡墨）
        self._draw_mountain(bg, 0.55, 0.60, (140, 135, 120), 1.8, 0)
        self._draw_mountain(bg, 0.48, 0.55, (120, 115, 100), 2.0, 0)
        self._draw_mountain(bg, 0.42, 0.52, (90, 85, 70), 2.2, 100)
        self._draw_mountain(bg, 0.38, 0.48, (70, 65, 50), 2.5, 250)

        # 水面/雾气
        for y in range(int(self.screen_height * 0.70), self.screen_height):
            ratio = (y - self.screen_height * 0.70) / (self.screen_height * 0.30)
            alpha = int(60 + 40 * ratio)
            pygame.draw.line(bg, (180, 175, 160, alpha), (0, y), (self.screen_width, y))

        # 近岸
        shore_y = int(self.screen_height * 0.85)
        points = []
        for x in range(0, self.screen_width + 10, 5):
            y_off = math.sin(x * 0.003) * 15 + math.sin(x * 0.008) * 8
            points.append((x, shore_y + y_off))
        points.append((self.screen_width, self.screen_height))
        points.append((0, self.screen_height))
        if len(points) > 2:
            surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (100, 95, 80, 200), points)
            bg.blit(surf, (0, 0))

        self.background_cache = bg

    def _draw_mountain(self, bg, y_start, y_end, color, amplitude, offset_x):
        """画一座山"""
        points = []
        sx = int(y_start * self.screen_height)
        ex = int(y_end * self.screen_height)
        steps = 40
        for i in range(steps + 1):
            t = i / steps
            x = t * self.screen_width
            h = sx + (ex - sx) * t
            peak = math.sin(t * math.pi) ** amplitude
            y = (self.screen_height * y_start + (self.screen_height * y_end - self.screen_height * y_start) * t
                 - peak * self.screen_height * 0.25)
            y += math.sin(t * 3 + offset_x * 0.01) * 30
            y += math.sin(t * 7 + offset_x * 0.02) * 15
            points.append((x, y))

        points.append((self.screen_width, self.screen_height))
        points.append((0, self.screen_height))
        pygame.draw.polygon(bg, (*color, 230), points)

    def draw_cloud(self, screen, cloud):
        """画一朵水墨云"""
        x = int(cloud["x"])
        y = int(cloud["y"])
        s = cloud["scale"]
        a = cloud["alpha"]

        cloud_surf = pygame.Surface((int(200 * s), int(80 * s)), pygame.SRCALPHA)
        color = (120, 115, 100, a)

        # 多个椭圆组成云朵
        centers = [
            (100 * s, 40 * s, 40 * s, 25 * s),
            (70 * s, 45 * s, 30 * s, 20 * s),
            (130 * s, 45 * s, 35 * s, 22 * s),
            (85 * s, 35 * s, 28 * s, 18 * s),
            (115 * s, 35 * s, 32 * s, 20 * s),
        ]
        for cx, cy, rx, ry in centers:
            pygame.draw.ellipse(cloud_surf, color,
                               (cx - rx, cy - ry, rx * 2, ry * 2))

        screen.blit(cloud_surf, (x - 100 * s, y - 40 * s))

    def draw_ink_title(self, screen):
        """用水墨风格绘制标题"""
        title = "仙道永恒"
        t = pygame.time.get_ticks() * 0.001

        # 标题光晕 - 模拟墨迹晕染
        glow_surfaces = []
        for layer in range(5):
            size = 84 - layer * 6
            alpha = max(0, 12 - layer * 3)
            color = (40 + layer * 10, 35 + layer * 10, 25 + layer * 10)
            surf = self.font_manager.render_text(title, "title", color, size)
            glow_surfaces.append((surf, alpha))

        base_y = self.screen_height * 0.22
        float_y = math.sin(t * 0.8) * 8

        for surf, alpha in glow_surfaces:
            if alpha <= 0:
                continue
            s = surf.copy()
            s.set_alpha(alpha)
            x = (self.screen_width - surf.get_width()) // 2
            screen.blit(s, (x, base_y + float_y))

        # 主体标题 - 深墨色
        title_surf = self.font_manager.render_text(title, "title", (30, 25, 15), 84)
        tx = (self.screen_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (tx, base_y + float_y))

        # 印章效果 - 红色小印
        seal_y = base_y + float_y + 110
        seal_x = tx + title_surf.get_width() + 30
        seal_size = 55
        seal_surf = pygame.Surface((seal_size, seal_size), pygame.SRCALPHA)
        pygame.draw.rect(seal_surf, (180, 50, 40, 200),
                         (0, 0, seal_size, seal_size), border_radius=4)
        seal_text = self.font_manager.render_text("仙", "small", (240, 230, 210), 28)
        stw, sth = seal_text.get_size()
        seal_surf.blit(seal_text, ((seal_size - stw) // 2, (seal_size - sth) // 2 - 2))
        screen.blit(seal_surf, (seal_x, seal_y))

    def draw_start_button(self, screen):
        """绘制开始按钮（水墨风格）"""
        self._draw_button(screen, self.start_button, "开始游戏", self.btn_hovered)
    
    def draw_load_button(self, screen):
        """绘制读取存档按钮（水墨风格）"""
        self._draw_button(screen, self.load_button, "读取存档", self.load_hovered)
    
    def _draw_button(self, screen, rect, text, hovered):
        """绘制通用按钮"""
        # 按钮墨色底
        if hovered:
            btn_color = (60, 50, 35)
            border_color = (30, 20, 10)
            scale = 1.04
        else:
            btn_color = (45, 38, 28)
            border_color = (40, 35, 25)
            scale = 1.0

        # 计算缩放
        sw = int(rect.width * scale)
        sh = int(rect.height * scale)
        sx = rect.centerx - sw // 2
        sy = rect.centery - sh // 2

        # 按钮背景（宣纸质感）
        btn_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*btn_color, 220), (0, 0, sw, sh), border_radius=6)
        pygame.draw.rect(btn_surf, (*border_color, 255), (0, 0, sw, sh), width=2, border_radius=6)

        # 按钮文字
        t = pygame.time.get_ticks() * 0.001
        pulse = math.sin(t * 2.0) * 0.5 + 0.5
        text_color = (240, 230, 210) if hovered else (210, 200, 180)
        text_surf = self.font_manager.render_text(text, "large", text_color, 36)
        tw, th = text_surf.get_size()
        btn_surf.blit(text_surf, ((sw - tw) // 2, (sh - th) // 2))

        screen.blit(btn_surf, (sx, sy))

        # 闪烁指示箭头（仅开始按钮）
        if text == "开始游戏" and self.start_phase >= 1:
            arrow_alpha = int(100 + 100 * pulse)
            arrow = self.font_manager.render_text("▶", "medium", (200, 190, 170), 24)
            aw = arrow.get_width()
            screen.blit(arrow, (rect.centerx + sw // 2 + 15, sy + sh // 2 - 12))

    def update(self, dt):
        """更新"""
        # 淡入
        if self.start_alpha < 1.0:
            self.start_alpha = min(1.0, self.start_alpha + dt * 1.5)

        # 阶段切换
        if self.start_alpha >= 0.9 and self.start_phase == 0:
            self.start_phase = 1

        # 云移动
        for c in self.clouds:
            c["x"] += c["speed"]
            if c["x"] > self.screen_width + 300:
                c["x"] = -300

        # 墨点上升
        for p in self.ink_particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = self.screen_height + 10
                p["x"] = random.randint(0, self.screen_width)

    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        self.btn_hovered = self.start_button.collidepoint(mouse_pos)
        self.load_hovered = self.load_button.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_hovered:
                    return "start_game"
                if self.load_hovered:
                    return "load_game"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "quit"
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return "start_game"

        return None

    def draw(self, screen):
        """绘制"""
        # 背景
        if self.background_cache is None:
            self.create_landscape_background()
        screen.blit(self.background_cache, (0, 0))

        # 云
        for c in self.clouds:
            self.draw_cloud(screen, c)

        # 墨点
        for p in self.ink_particles:
            pygame.draw.circle(screen, (80, 75, 65, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 标题
        self.draw_ink_title(screen)

        # 副标题
        t = pygame.time.get_ticks() * 0.001
        sub = "修仙肉鸽 · 弹幕射击"
        sub_surf = self.font_manager.render_text(sub, "medium", (100, 90, 75), 28)
        sw = sub_surf.get_width()
        base_y = self.screen_height * 0.22
        screen.blit(sub_surf,
                    ((self.screen_width - sw) // 2, base_y + 105))

        # 装饰墨线
        line_y = base_y + 145
        line_w = 300
        line_x = (self.screen_width - line_w) // 2
        for i in range(2):
            pygame.draw.line(screen, (80, 75, 65, 60 - i * 20),
                           (line_x, line_y + i * 4),
                           (line_x + line_w, line_y + i * 4), 1)

        # 开始按钮
        self.draw_start_button(screen)
        
        # 读取存档按钮
        self.draw_load_button(screen)

        # 底部提示
        hint = "点击按钮 或 按空格键 开始"
        hint_surf = self.font_manager.render_text(hint, "small", (150, 145, 130), 20)
        hw = hint_surf.get_width()
        screen.blit(hint_surf, ((self.screen_width - hw) // 2, self.screen_height - 40))


def run_title_screen(screen, ling_shi_amount=0):
    """运行标题界面，返回 'start_game' 或 'quit'"""
    ts = TitleScreen(screen.get_width(), screen.get_height())
    clock = pygame.time.Clock()

    while ts.running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        result = ts.handle_events(events)
        ts.update(dt)
        ts.draw(screen)
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        
        pygame.display.flip()

        if result:
            return result

    return "quit"
