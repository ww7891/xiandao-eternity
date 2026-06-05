"""
灵石UI渲染器 - 右上角灵石图标+数量显示
水墨风格，配合作品整体美术风格
"""

import pygame
import math
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def _load_config():
    """加载配置"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def _get_font(config, size=18):
    """获取字体，优先使用配置中的主字体"""
    font_path = config.get("font", {}).get("primary", "")
    if font_path and os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    return pygame.font.SysFont("SimHei", size)


def draw_ling_shi_icon(surface, x, y, size=20):
    """
    绘制灵石图标 - 宝石/水晶形状
    返回: (图标右边界x, 图标中心y)
    """
    cx, cy = x + size // 2, y + size // 2
    r = size * 0.45  # 主体半径

    # === 光晕背景 ===
    for i in range(3, 0, -1):
        glow_r = r + i * 3
        alpha = 20 + i * 10
        glow_surf = pygame.Surface((int(glow_r * 2.5), int(glow_r * 2.5)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (100, 200, 100, alpha),
                          (glow_surf.get_width() // 2, glow_surf.get_height() // 2), int(glow_r))
        surface.blit(glow_surf, (cx - glow_surf.get_width() // 2, cy - glow_surf.get_height() // 2))

    # === 水晶主体：八边形（灵石晶块） ===
    # 灵石是菱形的，上方尖、下方钝，像一颗钻石
    top_y = cy - r * 1.3         # 顶部尖点
    bottom_y = cy + r * 0.8      # 底部钝点
    left_x = cx - r               # 左侧
    right_x = cx + r              # 右侧
    mid_top_y = cy - r * 0.3      # 上半截凹处
    mid_bot_y = cy + r * 0.2      # 下半截鼓处

    # 上锥面（亮面）
    upper_facet = [
        (cx, top_y),              # 顶部尖点
        (right_x - r * 0.3, mid_top_y),  # 右上肩
        (cx, cy),                  # 中间
        (left_x + r * 0.3, mid_top_y),   # 左上肩
    ]
    pygame.draw.polygon(surface, (120, 210, 130), upper_facet)

    # 左上切面
    left_upper = [
        (left_x + r * 0.3, mid_top_y),  # 左上肩
        (cx, cy),                         # 中间
        (left_x + r * 0.1, mid_bot_y),    # 左下腰
        (left_x, mid_top_y - r * 0.1),    # 左侧
    ]
    pygame.draw.polygon(surface, (80, 170, 90), left_upper)

    # 右上切面
    right_upper = [
        (right_x - r * 0.3, mid_top_y),   # 右上肩
        (cx, cy),                          # 中间
        (right_x - r * 0.1, mid_bot_y),    # 右下腰
        (right_x, mid_top_y - r * 0.1),    # 右侧
    ]
    pygame.draw.polygon(surface, (60, 140, 70), right_upper)

    # 下锥面（高光）
    lower_facet = [
        (cx, cy),                  # 中间
        (right_x - r * 0.1, mid_bot_y),   # 右下腰
        (cx, bottom_y),            # 底部
        (left_x + r * 0.1, mid_bot_y),    # 左下腰
    ]
    pygame.draw.polygon(surface, (180, 240, 190), lower_facet)

    # === 棱线 ===
    edge_color = (40, 100, 50)
    pygame.draw.polygon(surface, edge_color, upper_facet, 2)
    pygame.draw.polygon(surface, edge_color, lower_facet, 2)
    pygame.draw.polygon(surface, edge_color, left_upper, 1)
    pygame.draw.polygon(surface, edge_color, right_upper, 1)

    # === 中心高光点 ===
    highlight_r = r * 0.2
    for i in range(2, 0, -1):
        hr = highlight_r + i
        alpha = 100 - i * 30
        pygame.draw.circle(surface, (200, 255, 210, alpha),
                         (int(cx - r * 0.15), int(cy - r * 0.15)), int(hr))
    pygame.draw.circle(surface, (230, 255, 235, 180),
                     (int(cx - r * 0.15), int(cy - r * 0.15)), int(highlight_r))

    return (x + size, cy)


def draw_ling_shi_widget(screen, amount, x=None, y=15):
    """
    绘制灵石显示组件：灵石图标 + 数量方框

    参数:
        screen: pygame surface
        amount: 灵石数量
        x: 组件的右边界x坐标（None则右上角自动定位）
        y: 组件顶部y坐标
    """
    config = _load_config()
    width = screen.get_width()

    if x is None:
        x = width - 25  # 右边界，留25px边距

    font = _get_font(config, 22)
    bold_font = _get_font(config, 26)

    # 灵石数量文本
    amount_text = str(amount)
    text_surf = bold_font.render(amount_text, True, (230, 255, 220))
    text_w, text_h = text_surf.get_size()

    icon_size = 24
    padding_h = 12
    padding_v = 6
    box_w = icon_size + text_w + padding_h * 3
    box_h = max(icon_size + padding_v * 2, text_h + padding_v * 2 + 4)

    # 盒子左边界
    box_x = x - box_w
    box_y = y

    # === 面板背景 ===
    panel_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)

    # 半透明深色背景 + 金色边框（水墨风格）
    pygame.draw.rect(panel, (25, 20, 30, 200), (0, 0, box_w, box_h), border_radius=8)
    pygame.draw.rect(panel, (100, 90, 60, 180), (0, 0, box_w, box_h), width=2, border_radius=8)

    # 顶部金色装饰线
    deco_y = 3
    deco_x_start = box_w * 0.25
    deco_x_end = box_w * 0.75
    pygame.draw.line(panel, (160, 140, 60, 120), (deco_x_start, deco_y), (deco_x_end, deco_y), 1)

    screen.blit(panel, (box_x, box_y))

    # === 灵石图标（在盒子内部左侧） ===
    icon_x = box_x + padding_h
    icon_y = box_y + (box_h - icon_size) // 2
    draw_ling_shi_icon(screen, icon_x, icon_y, icon_size)

    # === 灵石数量文字 ===
    text_x = icon_x + icon_size + padding_h
    text_y = box_y + (box_h - text_h) // 2
    screen.blit(text_surf, (text_x, text_y))

    return pygame.Rect(box_x, box_y, box_w, box_h)


def draw_ling_shi_count(screen, amount, x=None, y=15):
    """
    简化版 - 只绘制灵石组件（无额外逻辑）
    供各面板直接调用
    """
    return draw_ling_shi_widget(screen, amount, x, y)