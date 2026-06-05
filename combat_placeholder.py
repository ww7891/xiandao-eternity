"""
战斗子模块占位界面（锁妖塔 / 远古战场）
"""

import pygame
import sys
import os
import json
import random

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_combat_placeholder(screen, title_text, subtitle, ling_shi_amount=0):
    """占位界面"""
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()
    font_path = config["font"]["primary"]

    bg = pygame.Surface((width, height))
    bg.fill((235, 230, 220))

    particles = []
    for _ in range(25):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.randint(1, 4),
            "alpha": random.randint(10, 40),
            "speed": random.uniform(0.3, 1.0),
        })

    return_rect = pygame.Rect(30, 30, 120, 40)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if return_rect.collidepoint(mouse_pos):
                    return "goto_main_menu"

        for p in particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = height + 10
                p["x"] = random.randint(0, width)

        screen.blit(bg, (0, 0))

        for p in particles:
            pygame.draw.circle(screen, (70, 65, 55, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 返回按钮
        btn_hover = return_rect.collidepoint(mouse_pos)
        btn_color = (80, 65, 45, 220) if btn_hover else (60, 48, 32, 180)
        btn_surf = pygame.Surface((return_rect.width, return_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, btn_color, (0, 0, return_rect.width, return_rect.height), border_radius=6)
        pygame.draw.rect(btn_surf, (120, 100, 70, 200), (0, 0, return_rect.width, return_rect.height), width=1, border_radius=6)
        btn_font = pygame.font.Font(font_path, 22)
        btn_text = btn_font.render("← 返回", True, (210, 200, 180))
        btn_surf.blit(btn_text, ((return_rect.width - btn_text.get_width()) // 2,
                                  (return_rect.height - btn_text.get_height()) // 2))
        screen.blit(btn_surf, (return_rect.x, return_rect.y))

        # 标题
        title_font = pygame.font.Font(font_path, 48)
        title = title_font.render(title_text, True, (50, 40, 25))
        screen.blit(title, ((width - title.get_width()) // 2, 100))

        sub_font = pygame.font.Font(font_path, 22)
        sub = sub_font.render(subtitle, True, (100, 90, 75))
        screen.blit(sub, ((width - sub.get_width()) // 2, 165))

        lx = (width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 200), (lx + 400, 200), 1)

        hint_font = pygame.font.Font(font_path, 20)
        hint = hint_font.render("功能开发中，敬请期待", True, (140, 130, 110))
        screen.blit(hint, ((width - hint.get_width()) // 2, 280))

        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()

    return "quit"