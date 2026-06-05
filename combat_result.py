"""
战斗结果界面
显示胜利/失败，掉落物
"""

import pygame
import sys
import os
import json
import random

from adventure_data import get_map

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_combat_result(screen, result_type, drops, map_id, ling_shi_amount=0):
    """战斗结果界面
    result_type: "victory" / "defeat"
    drops: [(物品名, 数量, 品质), ...]
    返回 "retry" 或 "goto_main_menu"
    """
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()
    font_path = config["font"]["primary"]

    map_data = get_map(map_id)
    map_name = map_data["name"] if map_data else "未知地图"

    # 水墨背景
    bg = pygame.Surface((width, height))
    bg.fill((235, 230, 220))

    particles = []
    for _ in range(20):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.randint(1, 3),
            "alpha": random.randint(10, 35),
            "speed": random.uniform(0.2, 0.6),
        })

    # 按钮
    btn_w, btn_h = 180, 50
    if result_type == "victory":
        btn1 = pygame.Rect((width // 2 - btn_w - 30, height - 120, btn_w, btn_h))
        btn2 = pygame.Rect((width // 2 + 30, height - 120, btn_w, btn_h))
        btn1_label = "再战一次"
        btn2_label = "返回主菜单"
    else:
        btn1 = pygame.Rect((width // 2 - btn_w - 30, height - 120, btn_w, btn_h))
        btn2 = pygame.Rect((width // 2 + 30, height - 120, btn_w, btn_h))
        btn1_label = "重新挑战"
        btn2_label = "返回主菜单"

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
                if btn1.collidepoint(mouse_pos):
                    return "retry"
                if btn2.collidepoint(mouse_pos):
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

        # 结果标题
        if result_type == "victory":
            title_color = (180, 140, 40)
            title_text = "胜 利"
            subtitle = f"「{map_name}」讨伐成功！"
        else:
            title_color = (160, 60, 50)
            title_text = "败 北"
            subtitle = f"「{map_name}」挑战失败"

        title_font = pygame.font.Font(font_path, 56)
        ts = title_font.render(title_text, True, title_color)
        screen.blit(ts, ((width - ts.get_width()) // 2, 40))

        sub_font = pygame.font.Font(font_path, 24)
        ss = sub_font.render(subtitle, True, (100, 90, 75))
        screen.blit(ss, ((width - ss.get_width()) // 2, 110))

        pygame.draw.line(screen, (100, 90, 75, 100), (width // 2 - 200, 150), (width // 2 + 200, 150), 1)

        # 掉落物
        if result_type == "victory":
            drop_title = sub_font.render("战利品", True, (80, 60, 40))
            screen.blit(drop_title, ((width - drop_title.get_width()) // 2, 175))

            if drops:
                drop_font = pygame.font.Font(font_path, 18)
                # 合并相同物品
                merged = {}
                for name, qty, quality in drops:
                    key = name
                    if key not in merged:
                        merged[key] = {"qty": 0, "quality": quality}
                    merged[key]["qty"] += qty

                y_offset = 220
                for name, data in merged.items():
                    quality_colors = {
                        1: (140, 150, 140),
                        2: (100, 180, 100),
                        3: (100, 150, 220),
                        4: (180, 100, 220),
                    }
                    qc = quality_colors.get(data["quality"], (200, 200, 200))
                    drop_text = drop_font.render(f"{name} × {data['qty']}", True, qc)
                    screen.blit(drop_text, ((width - drop_text.get_width()) // 2, y_offset))
                    y_offset += 28
            else:
                drop_font = pygame.font.Font(font_path, 16)
                no_drop = drop_font.render("（无掉落）", True, (140, 130, 110))
                screen.blit(no_drop, ((width - no_drop.get_width()) // 2, 220))
        else:
            hint_font = pygame.font.Font(font_path, 20)
            hint = hint_font.render("击杀进度已重置，请重新挑战", True, (160, 120, 100))
            screen.blit(hint, ((width - hint.get_width()) // 2, 230))

        # 按钮
        for btn, label, color_offset in [
            (btn1, btn1_label, 0),
            (btn2, btn2_label, 1),
        ]:
            btn_hover = btn.collidepoint(mouse_pos)
            btn_surf = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            if btn_hover:
                pygame.draw.rect(btn_surf, (80, 60, 40, 230), (0, 0, btn.width, btn.height), border_radius=8)
                tc = (250, 240, 210)
            else:
                pygame.draw.rect(btn_surf, (60, 45, 30, 190), (0, 0, btn.width, btn.height), border_radius=8)
                tc = (220, 200, 170)
            pygame.draw.rect(btn_surf, (120, 100, 70, 180), (0, 0, btn.width, btn.height), width=1, border_radius=8)
            btn_font = pygame.font.Font(font_path, 24)
            bt = btn_font.render(label, True, tc)
            btn_surf.blit(bt, ((btn.width - bt.get_width()) // 2, (btn.height - bt.get_height()) // 2))
            screen.blit(btn_surf, (btn.x, btn.y))

        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()

    return "quit"