"""
历练之路 - 地图选择界面
18张地图，每张卡片显示状态（已解锁/未解锁/已通关）
"""

import pygame
import sys
import os
import json
import random

from adventure_data import MAPS, unlocked_maps, get_map

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_adventure_select(screen, ling_shi_amount=0):
    """地图选择界面，返回选中的地图ID或None"""
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()
    font_path = config["font"]["primary"]

    # 水墨背景
    bg = pygame.Surface((width, height))
    bg.fill((235, 230, 220))

    particles = []
    for _ in range(25):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.randint(1, 3),
            "alpha": random.randint(10, 35),
            "speed": random.uniform(0.2, 0.8),
        })

    # 返回按钮
    return_rect = pygame.Rect(30, 30, 120, 40)

    # 地图卡片布局
    card_w, card_h = 170, 130
    cols = 6
    rows = 3
    gap_x = 15
    gap_y = 15
    total_w = cols * card_w + (cols - 1) * gap_x
    start_x = (width - total_w) // 2
    start_y = 130

    # 构建卡片数据
    cards = []
    for i, m in enumerate(MAPS):
        col = i % cols
        row = i // cols
        cx = start_x + col * (card_w + gap_x)
        cy = start_y + row * (card_h + gap_y)
        cards.append({
            "rect": pygame.Rect(cx, cy, card_w, card_h),
            "map": m,
            "unlocked": m["id"] in unlocked_maps,
        })

    # 境界标签
    realm_labels = []
    realm_names = ["练气", "筑基", "金丹", "元婴", "化神", "炼虚", "合体", "大乘", "渡劫"]
    for ri, rname in enumerate(realm_names):
        col = ri
        cx = start_x + col * (card_w + gap_x) + card_w // 2
        cy = start_y - 25
        realm_labels.append({"x": cx, "y": cy, "name": rname})

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if return_rect.collidepoint(mouse_pos):
                    return None
                for c in cards:
                    if c["rect"].collidepoint(mouse_pos) and c["unlocked"]:
                        return c["map"]["id"]

        for p in particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = height + 10
                p["x"] = random.randint(0, width)

        # ========== 绘制 ==========
        screen.blit(bg, (0, 0))

        for p in particles:
            pygame.draw.circle(screen, (70, 65, 55, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 标题
        title_font = pygame.font.Font(font_path, 40)
        title = title_font.render("历练之路", True, (50, 40, 25))
        screen.blit(title, ((width - title.get_width()) // 2, 25))

        subtitle_font = pygame.font.Font(font_path, 20)
        subtitle = subtitle_font.render("斩妖除魔，步步登仙", True, (100, 90, 75))
        screen.blit(subtitle, ((width - subtitle.get_width()) // 2, 75))

        # 分隔线
        lx = (width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 105), (lx + 400, 105), 1)

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

        # 境界标签
        realm_font = pygame.font.Font(font_path, 16)
        for rl in realm_labels:
            rt = realm_font.render(rl["name"], True, (80, 70, 55))
            screen.blit(rt, (rl["x"] - rt.get_width() // 2, rl["y"]))

        # 地图卡片
        for c in cards:
            m = c["map"]
            r = c["rect"]
            unlocked = c["unlocked"]
            hovered = r.collidepoint(mouse_pos) and unlocked

            card = pygame.Surface((r.width, r.height), pygame.SRCALPHA)

            if not unlocked:
                # 锁定状态
                pygame.draw.rect(card, (200, 195, 185, 150), (0, 0, r.width, r.height), border_radius=8)
                lock_font = pygame.font.Font(font_path, 24)
                lock = lock_font.render("🔒", True, (140, 130, 120))
                card.blit(lock, ((r.width - lock.get_width()) // 2, (r.height - lock.get_height()) // 2))
            elif hovered:
                pygame.draw.rect(card, m["bg_color"] + (220,), (0, 0, r.width, r.height), border_radius=8)
                pygame.draw.rect(card, (80, 60, 40, 240), (0, 0, r.width, r.height), width=2, border_radius=8)
            else:
                pygame.draw.rect(card, m["bg_color"] + (160,), (0, 0, r.width, r.height), border_radius=8)
                pygame.draw.rect(card, (60, 50, 35, 150), (0, 0, r.width, r.height), width=1, border_radius=8)

            if unlocked:
                # 地图名
                name_font = pygame.font.Font(font_path, 20)
                ns = name_font.render(m["name"], True, (40, 30, 20))
                card.blit(ns, ((r.width - ns.get_width()) // 2, 15))

                # 分隔
                pygame.draw.line(card, (100, 90, 75, 60), (10, 48), (r.width - 10, 48), 1)

                # 描述
                desc_font = pygame.font.Font(font_path, 13)
                desc_lines = [m["desc"][i:i+8] for i in range(0, len(m["desc"]), 8)]
                if len(desc_lines) > 2:
                    desc_lines = desc_lines[:2]
                for li, line in enumerate(desc_lines):
                    ds = desc_font.render(line, True, (70, 60, 45))
                    card.blit(ds, ((r.width - ds.get_width()) // 2, 58 + li * 20))

                # 地图编号
                idx_font = pygame.font.Font(font_path, 11)
                idx = idx_font.render(f"第{m['id']+1}关", True, (120, 110, 95))
                card.blit(idx, (r.width - idx.get_width() - 8, r.height - 20))

            screen.blit(card, (r.x, r.y))

        # 底部提示
        hint_font = pygame.font.Font(font_path, 16)
        hint = hint_font.render("击败当前地图Boss后自动解锁下一张地图", True, (140, 130, 110))
        screen.blit(hint, ((width - hint.get_width()) // 2, height - 45))

        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()

    return None