"""
炼制子模块占位界面
炼丹 / 炼器 / 绘符 共用此占位界面
"""

import pygame
import sys
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_craft_placeholder(screen, craft_type, subtitle, ling_shi_amount=0):
    """炼制子模块占位界面"""
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()

    # 水墨背景
    bg = pygame.Surface((width, height))
    bg.fill((235, 230, 220))

    # 墨点粒子
    import random
    particles = []
    for _ in range(30):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.randint(1, 4),
            "alpha": random.randint(15, 50),
            "speed": random.uniform(0.3, 1.2),
        })

    # 返回按钮
    return_rect = pygame.Rect(30, 30, 120, 40)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if return_rect.collidepoint(event.pos):
                    return "goto_main_menu"

        # 更新墨点
        for p in particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = height + 10
                p["x"] = random.randint(0, width)

        # 绘制
        screen.blit(bg, (0, 0))

        for p in particles:
            pygame.draw.circle(screen, (70, 65, 55, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 返回按钮
        mouse_pos = pygame.mouse.get_pos()
        btn_hover = return_rect.collidepoint(mouse_pos)
        btn_color = (80, 65, 45, 220) if btn_hover else (60, 48, 32, 180)
        btn_surf = pygame.Surface((return_rect.width, return_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, btn_color, (0, 0, return_rect.width, return_rect.height), border_radius=6)
        pygame.draw.rect(btn_surf, (120, 100, 70, 200), (0, 0, return_rect.width, return_rect.height), width=1, border_radius=6)

        font = pygame.font.Font(config["font"]["primary"], 22)
        btn_text = font.render("← 返回", True, (210, 200, 180))
        btn_surf.blit(btn_text, ((return_rect.width - btn_text.get_width()) // 2,
                                  (return_rect.height - btn_text.get_height()) // 2))
        screen.blit(btn_surf, (return_rect.x, return_rect.y))

        # 标题
        title_font = pygame.font.Font(config["font"]["primary"], 48)
        title_text = title_font.render(craft_type, True, (50, 40, 25))
        screen.blit(title_text, ((width - title_text.get_width()) // 2, 80))

        # 副标题
        sub_font = pygame.font.Font(config["font"]["primary"], 24)
        sub_text = sub_font.render(subtitle, True, (100, 90, 75))
        screen.blit(sub_text, ((width - sub_text.get_width()) // 2, 140))

        # 分隔线
        lx = (width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 175), (lx + 400, 175), 1)

        # 占位提示
        hint_font = pygame.font.Font(config["font"]["primary"], 20)
        hint_lines = [
            f"「{craft_type}」功能开发中",
            "",
            "此处将实现完整的炼制系统",
            "敬请期待",
        ]
        for i, line in enumerate(hint_lines):
            color = (50, 40, 25) if i == 0 else (120, 110, 95)
            hint_text = hint_font.render(line, True, color)
            screen.blit(hint_text, ((width - hint_text.get_width()) // 2, 240 + i * 35))

        # 底部装饰
        deco_font = pygame.font.Font(config["font"]["primary"], 16)
        deco_text = deco_font.render("—— 按 ESC 或点击返回按钮回到主菜单 ——", True, (140, 130, 110))
        screen.blit(deco_text, ((width - deco_text.get_width()) // 2, height - 60))

        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()

    return "quit"
