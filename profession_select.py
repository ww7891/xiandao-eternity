"""
职业选择界面
灵根抽取后，选择剑修 / 法修 / 刀修
"""

import pygame
import sys
import os
import json
import random

from profession_data import PROFESSIONS, current_profession

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_profession_select(screen, spiritual_root_data, ling_shi_amount=0):
    """职业选择界面，返回选择的职业ID"""
    config = load_config()
    width = screen.get_width()
    height = screen.get_height()
    clock = pygame.time.Clock()

    font_path = config["font"]["primary"]
    root_type = spiritual_root_data["root_type"]
    elements = spiritual_root_data["elements"]

    # 水墨背景
    bg = pygame.Surface((width, height))
    bg.fill((235, 230, 220))

    # 墨点
    particles = []
    for _ in range(40):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.randint(1, 4),
            "alpha": random.randint(10, 40),
            "speed": random.uniform(0.3, 1.0),
        })

    # 职业卡片
    prof_list = list(PROFESSIONS.values())
    card_w, card_h = 280, 420
    gap = 50
    total_w = card_w * 3 + gap * 2
    start_x = (width - total_w) // 2
    card_y = 160

    # 卡片的屏幕矩形
    card_rects = []
    for i, prof in enumerate(prof_list):
        cx = start_x + i * (card_w + gap)
        card_rects.append({
            "rect": pygame.Rect(cx, card_y, card_w, card_h),
            "prof": prof,
            "hovered": False,
        })

    # 选中状态
    selected_prof = None
    confirm_rect = None
    fade_alpha = 0

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
                # 检测卡片点击
                for cr in card_rects:
                    if cr["rect"].collidepoint(mouse_pos):
                        selected_prof = cr["prof"]
                        break
                # 检测确认按钮
                if confirm_rect and selected_prof and confirm_rect.collidepoint(mouse_pos):
                    import profession_data
                    profession_data.current_profession = selected_prof["id"]
                    return selected_prof["id"]

        # 更新墨点
        for p in particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = height + 10
                p["x"] = random.randint(0, width)

        # 更新hover状态
        for cr in card_rects:
            cr["hovered"] = cr["rect"].collidepoint(mouse_pos)

        # 确认按钮
        if selected_prof:
            fade_alpha = min(255, fade_alpha + 10)
            confirm_w, confirm_h = 200, 50
            confirm_rect = pygame.Rect((width - confirm_w) // 2, card_y + card_h + 40, confirm_w, confirm_h)
        else:
            fade_alpha = max(0, fade_alpha - 10)

        # ========== 绘制 ==========
        screen.blit(bg, (0, 0))

        for p in particles:
            pygame.draw.circle(screen, (70, 65, 55, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 标题
        title_font = pygame.font.Font(font_path, 42)
        title = title_font.render("选择修道之路", True, (50, 40, 25))
        screen.blit(title, ((width - title.get_width()) // 2, 30))

        # 灵根信息
        info_font = pygame.font.Font(font_path, 22)
        info = info_font.render(f"灵根: {root_type}（{'·'.join(elements)}）", True, (100, 90, 75))
        screen.blit(info, ((width - info.get_width()) // 2, 85))

        # 分隔线
        lx = (width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 120), (lx + 400, 120), 1)

        # 绘制职业卡片
        for cr in card_rects:
            prof = cr["prof"]
            r = cr["rect"]
            hovered = cr["hovered"]
            is_selected = selected_prof and selected_prof["id"] == prof["id"]

            card = pygame.Surface((r.width, r.height), pygame.SRCALPHA)

            # 底色
            if is_selected:
                bg_color = (80, 65, 45, 230)
                border_color = (180, 160, 100, 255)
                border_width = 3
            elif hovered:
                bg_color = (232, 227, 214, 220)
                border_color = (120, 100, 70, 200)
                border_width = 2
            else:
                bg_color = (232, 227, 214, 180)
                border_color = (80, 70, 55, 150)
                border_width = 1

            pygame.draw.rect(card, bg_color, (0, 0, r.width, r.height), border_radius=12)
            pygame.draw.rect(card, border_color, (0, 0, r.width, r.height), width=border_width, border_radius=12)

            # 职业名
            name_font = pygame.font.Font(font_path, 34)
            name_surf = name_font.render(prof["name"], True, (50, 40, 25))
            card.blit(name_surf, ((r.width - name_surf.get_width()) // 2, 25))

            # 副标题
            sub_font = pygame.font.Font(font_path, 18)
            sub_surf = sub_font.render(prof["subtitle"], True, (100, 90, 75))
            card.blit(sub_surf, ((r.width - sub_surf.get_width()) // 2, 72))

            # 分隔
            pygame.draw.line(card, (120, 110, 95, 60), (20, 102), (r.width - 20, 102), 1)

            # 攻击名
            atk_font = pygame.font.Font(font_path, 20)
            atk_surf = atk_font.render(f"「{prof['attack_name']}」", True, (80, 60, 40))
            card.blit(atk_surf, ((r.width - atk_surf.get_width()) // 2, 118))

            # 描述
            desc_font = pygame.font.Font(font_path, 15)
            desc_lines = prof["description"].split("\n")
            for li, line in enumerate(desc_lines):
                ds = desc_font.render(line, True, (100, 90, 75))
                card.blit(ds, ((r.width - ds.get_width()) // 2, 155 + li * 22))

            # 属性
            attr_font = pygame.font.Font(font_path, 13)
            attrs = [
                f"攻击间隔: {prof['attack_interval']}秒",
                f"基础伤害: {prof['attack_damage']}",
            ]
            for ai, a in enumerate(attrs):
                as_ = attr_font.render(a, True, (120, 110, 95))
                card.blit(as_, (20, 280 + ai * 20))

            screen.blit(card, (r.x, r.y))

            # 选中标记
            if is_selected:
                mark_font = pygame.font.Font(font_path, 14)
                mark = mark_font.render("已选择", True, (200, 180, 100))
                screen.blit(mark, (r.x + (r.width - mark.get_width()) // 2, r.y + r.height - 40))

        # 确认按钮
        if confirm_rect and selected_prof:
            btn_surf = pygame.Surface((confirm_rect.width, confirm_rect.height), pygame.SRCALPHA)
            btn_hover = confirm_rect.collidepoint(mouse_pos)
            if btn_hover:
                pygame.draw.rect(btn_surf, (80, 60, 40, 230), (0, 0, confirm_rect.width, confirm_rect.height), border_radius=8)
                btn_txt_color = (250, 240, 210)
            else:
                pygame.draw.rect(btn_surf, (60, 45, 30, 200), (0, 0, confirm_rect.width, confirm_rect.height), border_radius=8)
                btn_txt_color = (220, 200, 170)

            btn_font = pygame.font.Font(font_path, 26)
            btn_text = btn_font.render(f"踏入{selected_prof['name']}之路", True, btn_txt_color)
            btn_surf.blit(btn_text, ((confirm_rect.width - btn_text.get_width()) // 2,
                                      (confirm_rect.height - btn_text.get_height()) // 2))
            screen.blit(btn_surf, (confirm_rect.x, confirm_rect.y))

        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()

    return None