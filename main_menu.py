"""
仙道永恒 - 主菜单界面
第二屏：底部4个标签按钮 + 上方内容区域
"""

import pygame
import sys
import os
import math
import random
import time
from font_utils import FontManager
from alchemy_data import (
    PILL_TYPE_ORDER, PILL_TYPES, QUALITIES, REALM_NAMES, REALM_MATERIALS,
    QUALITY_DISPLAY_COLORS, QUALITY_MULTIPLIER, ALCHEMIST_MAX_LEVEL,
    player_alchemy, craft_pill, get_quality_probs, get_exp_for_level,
)
import realm_data
import gongfa_data
import sect_data
import forge_data
from forge_data import (
    player_forge, get_enhance_cap, get_enhance_success_rate,
    get_enhance_bonus_per_level, apply_enhance_stats,
    roll_forge_quality, forge_equipment, get_exp_for_level as forge_get_exp,
    REALM_ENHANCE_MATERIALS, REALM_FORGE_MATERIALS,
    EQUIP_QUALITIES, EQUIP_QUALITY_COLORS, QUALITY_MULTIPLIER as FORGE_QUALITY_MULT,
    EQUIP_SLOT_CN, FORGER_MAX_LEVEL, REALM_NAMES as FORGE_REALM_NAMES,
    seed_test_materials,
)
import cave_data
import treasure_data
from debug_panel import DebugPanel

# 配置路径
CONFIG_PATH = "config.json"

# 主菜单角色图片缓存
_char_img_cache = None


def _load_main_menu_char():
    global _char_img_cache
    if _char_img_cache is not None:
        return _char_img_cache
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "character_meditate.png")
    try:
        img = pygame.image.load(path).convert_alpha()
        _char_img_cache = img
        return img
    except:
        _char_img_cache = None
        return None


class MainMenu:
    """主菜单界面：底部标签栏 + 上方内容区"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)

        import json
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.colors = self.config.get("colors", {})

        self.running = True
        self.active_tab = "character"  # 当前激活的标签
        self.character_sub_tab = "角色"  # 人物子标签：角色 / 功法
        self.hovered_tab = None
        self.pressed_tab = None
        self.next_state = None  # 状态切换目标

        # 布局参数
        self.bar_height = int(screen_height * 0.15)
        self.content_top = 0
        self.content_height = screen_height - self.bar_height
        self.bar_top = self.content_height

        self.tabs = self.create_tabs()

        # 设置按钮（右上角）
        self.settings_button_rect = pygame.Rect(
            self.screen_width - 100, 15, 80, 40
        )
        self.settings_button_hovered = False

        # ====== 背包状态 ======
        self.inv_active_category = 0  # 0=全部 1=材料 2=装备 3=丹药 4=功法 5=宝箱 6=其他
        self.inv_categories = ["全部", "材料", "装备", "丹药", "功法", "宝箱", "其他"]
        self.inv_page = 0
        self.inv_items_per_page = 20  # 5列 x 4行
        self.inv_grid_cols = 5
        self.inv_grid_rows = 4
        self.inv_items = []  # 初始背包为空
        self.inv_selected_item = None
        self.inv_selected_slot = None  # 选中的装备槽位

        # 装备槽位（背包面板内）
        self.equipment_slots = {
            "weapon": None,
            "helmet": None,
            "armor": None,
            "gloves": None,
            "belt": None,
            "shoes": None,
            "accessory1": None,
            "accessory2": None,
        }

        # 战斗场景进入按钮区域（运行时填充）
        self.battle_enter_rects = []

        self.ink_particles = []
        for _ in range(20):
            self.ink_particles.append({
                "x": random.randint(0, screen_width),
                "y": random.randint(0, self.content_height),
                "size": random.randint(1, 3),
                "speed": random.uniform(0.2, 0.8),
                "alpha": random.randint(15, 45)
            })

        self.background_cache = None
        self.content_cache = {}  # 缓存各模块内容
        self.tab_transition = 0.0  # 切换动画
        
        # 宗门界面状态
        self.sect_buttons = []  # 宗门加入按钮
        self.leave_button_rect = None  # 退出宗门按钮
        self.sect_btn_hovered = None  # 悬停的宗门按钮
        self.leave_btn_hovered = False  # 退出按钮悬停
        self.sect_sub_tab = "主殿"  # 宗门内部子标签（主殿/执事殿/贡献堂/参悟堂）

        # 洞府界面状态
        self.cave_sub_tab = "灵药园"  # 灵药园/聚灵阵
        self.craft_sub_tab = None  # None=卡牌选择 / "炼丹"=炼丹界面
        self.selected_field = None  # 选中的药田
        self.selected_seed = None  # 选中的种子
        self.cave_buttons = []  # 洞府按钮

        # 藏宝阁界面状态
        self.treasure_sub_tab = "藏经阁"  # 藏经阁/法宝库/丹药房/材料仓
        self.treasure_current_floor = 0  # 当前所在楼层（0-8）
        self.treasure_buttons = []  # 藏宝阁按钮
        self.treasure_selected_item = None  # 选中的商品
        self.treasure_selected_type = None  # 商品类型

        # 炼丹界面状态
        self.alchemy_selected_type = 0  # 选中的丹药类型索引
        self.alchemy_selected_grade = 0  # 选中的品级 0-8（对应一品到九品）
        self.alchemy_selected_pill = None  # 选中的丹药（背包中）
        self.alchemy_buttons = []  # 炼丹界面按钮
        self.alchemy_pill_buttons = []  # 丹药列表按钮
        self.alchemy_craft_result = ""  # 炼制结果消息
        self.alchemy_craft_result_timer = 0

        # 炼器界面状态
        self.forge_sub_tab = None  # None=强化/锻造选择 / "强化" / "锻造"
        self.enhance_selected_slot = None  # 选中的强化槽位
        self.forge_selected_slot = None  # 选中的锻造槽位
        self.forge_selected_realm = 0  # 选中的锻造境界
        self.forge_buttons = []  # 炼器界面按钮
        self.forge_result = ""  # 炼器结果消息
        self.forge_result_timer = 0

        # 开发者调试面板
        self.debug_panel = DebugPanel(screen_width, screen_height)

        # 灵石钱包引用
        self.ling_shi_wallet = None
        self.ling_shi_amount = 0

        # 藏宝阁提示
        self.treasure_toast = ""
        self.treasure_toast_timer = 0

        print("✅ 主界面初始化完成")
    
    def _wrap_text(self, text, max_chars, max_width=None):
        """文本换行工具函数"""
        if max_width:
            # 基于宽度换行（中文按字符拆分）
            lines = []
            current_line = ""
            for ch in text:
                test_line = current_line + ch
                # 估算宽度：中文字符约14像素，英文约8像素
                test_width = sum(14 if ord(c) > 127 else 8 for c in test_line)
                if test_width > max_width and current_line:
                    lines.append(current_line)
                    current_line = ch
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            return lines
        else:
            # 基于字符数换行
            lines = []
            for i in range(0, len(text), max_chars):
                lines.append(text[i:i+max_chars])
            return lines

    def create_tabs(self):
        """创建底部七个标签"""
        gap = 20
        tab_w = (self.screen_width - gap * 8) // 7
        tab_h = self.bar_height - 10

        modules = [
            {"id": "character", "name": "人物", "icon_path": "char"},
            {"id": "inventory", "name": "背包", "icon_path": "bag"},
            {"id": "sect", "name": "宗门", "icon_path": "sect"},
            {"id": "craft", "name": "炼制", "icon_path": "craft"},
            {"id": "cave", "name": "洞府", "icon_path": "cave"},
            {"id": "treasure", "name": "藏宝阁", "icon_path": "treasure"},
            {"id": "battle", "name": "战斗", "icon_path": "battle"},
        ]

        tabs = []
        for i, mod in enumerate(modules):
            x = gap + i * (tab_w + gap)
            y = self.bar_top + 5
            tabs.append({
                "rect": pygame.Rect(x, y, tab_w, tab_h),
                "name": mod["name"],
                "id": mod["id"],
                "icon": mod["icon_path"],
            })
        return tabs

    def create_background(self):
        """水墨山水背景（仅内容区）"""
        bg = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        bg.fill((245, 240, 228))

        # 天空渐变（仅内容区）
        for y in range(self.content_height):
            ratio = y / self.content_height
            r = int(220 + 25 * min(ratio, 0.5) * 2)
            g = int(215 + 30 * min(ratio, 0.5) * 2)
            b = int(205 + 40 * min(ratio, 0.5) * 2)
            if ratio > 0.5:
                r = int(245 - 60 * (ratio - 0.5))
                g = int(245 - 55 * (ratio - 0.5))
                b = int(245 - 40 * (ratio - 0.5))
            pygame.draw.line(bg, (r, g, b), (0, y), (self.screen_width, y))

        # 远山
        for sy, color, amp in [
            (0.55, (145, 140, 125), 1.5),
            (0.48, (125, 120, 105), 1.8),
            (0.42, (95, 90, 75), 2.0),
        ]:
            pts = []
            for i in range(41):
                t = i / 40
                x = t * self.screen_width
                peak = math.sin(t * math.pi) ** amp
                y = self.content_height * sy - peak * self.content_height * 0.22
                y += math.sin(t * 4) * 18
                pts.append((x, y))
            pts.append((self.screen_width, self.content_height))
            pts.append((0, self.content_height))
            pygame.draw.polygon(bg, (*color, 170), pts)

        # 底部栏底色
        bar_bg = pygame.Surface((self.screen_width, self.bar_height), pygame.SRCALPHA)
        bar_bg.fill((55, 45, 32, 235))
        bg.blit(bar_bg, (0, self.bar_top))

        self.background_cache = bg

    def draw_content_character(self, screen):
        """人物模块 - 含角色和功法两个子标签"""
        # 子标签栏
        sub_tabs = ["角色", "功法"]
        sub_tab_w, sub_tab_h = 100, 36
        sub_tab_gap = 10
        sub_start_x = (self.screen_width - (sub_tab_w * 2 + sub_tab_gap)) // 2
        sub_tab_y = 55
        self.sub_tab_rects = {}

        for i, st in enumerate(sub_tabs):
            sx = sub_start_x + i * (sub_tab_w + sub_tab_gap)
            is_active = (st == self.character_sub_tab)
            sub_rect = pygame.Rect(sx, sub_tab_y, sub_tab_w, sub_tab_h)
            self.sub_tab_rects[st] = sub_rect

            if is_active:
                pygame.draw.rect(screen, (180, 140, 80, 220), sub_rect, border_radius=6)
                pygame.draw.rect(screen, (200, 160, 60, 240), sub_rect, width=2, border_radius=6)
                st_color = (50, 30, 10)
            else:
                pygame.draw.rect(screen, (200, 190, 170, 160), sub_rect, border_radius=6)
                pygame.draw.rect(screen, (160, 140, 110, 120), sub_rect, width=1, border_radius=6)
                st_color = (120, 100, 80)

            st_surf = self.font_manager.render_text(st, "medium", st_color, 20)
            screen.blit(st_surf, (sx + (sub_tab_w - st_surf.get_width()) // 2,
                                 sub_tab_y + (sub_tab_h - st_surf.get_height()) // 2))

        # 分割线
        pygame.draw.line(screen, (100, 90, 75, 100),
                        (sub_start_x - 40, sub_tab_y + sub_tab_h + 5),
                        (sub_start_x + sub_tab_w * 2 + sub_tab_gap + 40, sub_tab_y + sub_tab_h + 5), 1)

        if self.character_sub_tab == "角色":
            self._draw_character_stats(screen)
        else:
            self._draw_character_gongfa(screen)

    def _draw_character_stats(self, screen):
        """角色子标签：上部属性面板 + 下部HP/MP条(左) + 修炼系统(右)"""
        margin = 40
        pw = self.screen_width - margin * 2
        top_y = 100

        # ========== 上部：属性面板（横跨全宽） ==========
        attr_panel_h = 220
        attr_panel = pygame.Surface((pw, attr_panel_h), pygame.SRCALPHA)
        pygame.draw.rect(attr_panel, (232, 227, 214, 200),
                        (0, 0, pw, attr_panel_h), border_radius=8)
        pygame.draw.rect(attr_panel, (80, 70, 55, 180),
                        (0, 0, pw, attr_panel_h), width=2, border_radius=8)

        p = realm_data.player
        realm_name = realm_data.get_realm_name(p["realm_index"])
        stage, progress, stage_total, realm_total = realm_data.get_stage_info(
            p["realm_index"], p["cultivation"], p["current_stage"]
        )

        # --- 左侧头像区（使用豆包素材角色图） ---
        avatar_cx, avatar_cy = 55, attr_panel_h // 2
        avatar_r = 40
        char_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "character_portrait.png")
        if os.path.exists(char_img_path):
            char_img = pygame.image.load(char_img_path).convert_alpha()
            img_h = avatar_r * 2
            img_w = int(char_img.get_width() * (img_h / char_img.get_height()))
            char_img = pygame.transform.smoothscale(char_img, (img_w, img_h))
            attr_panel.blit(char_img, (avatar_cx - img_w // 2, avatar_cy - img_h // 2))
        else:
            pygame.draw.circle(attr_panel, (180, 170, 150, 150),
                              (avatar_cx, avatar_cy), avatar_r)
            pygame.draw.circle(attr_panel, (60, 50, 35, 200),
                              (avatar_cx, avatar_cy), avatar_r, 2)
            av_label = self.font_manager.render_text("修", "medium", (60, 50, 35), 26)
            attr_panel.blit(av_label, (avatar_cx - av_label.get_width() // 2,
                                       avatar_cy - av_label.get_height() // 2))

        # --- 中间属性区（两列） ---
        col1_x, col2_x = 120, 420
        left_attrs = [
            ("姓名", p["name"]),
            ("境界", f"{realm_name}期"),
            ("修为", f"{progress:,} / {stage_total:,}"),
            ("生命", f"{p['hp']}/{p.get('max_hp', p['hp'])}"),
        ]
        right_attrs = [
            ("等阶", f"第{stage}阶"),
            ("攻击", str(p["attack"])),
            ("灵力", f"{p.get('mp', 50)}/{p.get('max_mp', 50)}"),
            ("防御", str(p["defense"])),
        ]

        row_h = 38
        base_y = 20
        for i, (label, value) in enumerate(left_attrs):
            ly = base_y + i * row_h
            lbl = self.font_manager.render_text(f"{label}：", "medium", (100, 90, 75), 19)
            val = self.font_manager.render_text(value, "medium", (40, 30, 18), 19)
            attr_panel.blit(lbl, (col1_x, ly))
            attr_panel.blit(val, (col1_x + 80, ly))

        for i, (label, value) in enumerate(right_attrs):
            ly = base_y + i * row_h
            lbl = self.font_manager.render_text(f"{label}：", "medium", (100, 90, 75), 19)
            val = self.font_manager.render_text(value, "medium", (40, 30, 18), 19)
            attr_panel.blit(lbl, (col2_x, ly))
            attr_panel.blit(val, (col2_x + 80, ly))

        # --- 右侧灵根区 ---
        root_x = 720
        root_label_main = self.font_manager.render_text("灵根", "medium", (80, 65, 45), 20)
        attr_panel.blit(root_label_main, (root_x, 18))
        pygame.draw.line(attr_panel, (160, 150, 130, 100),
                        (root_x, 48), (pw - 30, 48), 1)

        root = gongfa_data.player_gongfa.get("spiritual_root")
        if root:
            root_type, elements, bonus = root
            rt = self.font_manager.render_text(root_type, "medium", (30, 20, 10), 22)
            attr_panel.blit(rt, (root_x, 60))

            bonus_pct = int((bonus - 1.0) * 100)
            bonus_label = self.font_manager.render_text(
                f"功法加成 +{bonus_pct}%", "medium",
                (200, 80, 30) if bonus_pct >= 60 else
                (120, 60, 180) if bonus_pct >= 40 else
                (40, 120, 40) if bonus_pct >= 20 else (100, 90, 80),
                18
            )
            attr_panel.blit(bonus_label, (root_x, 92))

            elem_label = self.font_manager.render_text("属性：", "small", (80, 65, 45), 16)
            attr_panel.blit(elem_label, (root_x, 120))
            for ei, elem in enumerate(elements):
                ec = gongfa_data.ELEMENT_COLORS[elem]
                et = self.font_manager.render_text(elem, "medium", ec, 20)
                attr_panel.blit(et, (root_x + 48 + ei * 44, 118))
        else:
            rl = self.font_manager.render_text("未觉醒", "medium", (120, 100, 80), 18)
            attr_panel.blit(rl, (root_x, 60))

        screen.blit(attr_panel, (margin, top_y))

        # ========== 下部：HP/MP条（左） + 修炼系统（右） ==========
        bottom_y = top_y + attr_panel_h + 15
        left_w = 600
        right_w = pw - left_w - 15
        bottom_h = 260

        # --- HP/MP 状态面板 ---
        bar_panel = pygame.Surface((left_w, bottom_h), pygame.SRCALPHA)
        pygame.draw.rect(bar_panel, (232, 227, 214, 200),
                        (0, 0, left_w, bottom_h), border_radius=8)
        pygame.draw.rect(bar_panel, (80, 70, 55, 180),
                        (0, 0, left_w, bottom_h), width=2, border_radius=8)

        bp_title = self.font_manager.render_text("状态", "medium", (50, 40, 25), 22)
        bar_panel.blit(bp_title, (20, 10))
        pygame.draw.line(bar_panel, (160, 150, 130, 80),
                        (20, 40), (left_w - 20, 40), 1)

        bar_w = left_w - 80
        bar_h = 30

        # 生命条
        hp_label = self.font_manager.render_text("生命值", "medium", (180, 60, 40), 18)
        bar_panel.blit(hp_label, (40, 58))
        hp_text = self.font_manager.render_text(
            f"{p['hp']} / {p.get('max_hp', p['hp'])}", "medium", (40, 30, 18), 16
        )
        bar_panel.blit(hp_text, (left_w - 40 - hp_text.get_width(), 58))

        hp_ratio = p["hp"] / p.get("max_hp", p["hp"]) if p.get("max_hp", p["hp"]) > 0 else 0
        hp_bar_y = 84
        pygame.draw.rect(bar_panel, (40, 15, 15),
                        (40, hp_bar_y, bar_w, bar_h), border_radius=8)
        fill_w = int(bar_w * hp_ratio)
        if fill_w > 0:
            for fx in range(fill_w):
                ratio = fx / bar_w
                pygame.draw.line(bar_panel,
                    (int(200 * (0.6 + ratio * 0.4)),
                     int(60 * (0.5 + ratio * 0.3)),
                     int(30 * 0.5)),
                    (40 + fx, hp_bar_y), (40 + fx, hp_bar_y + bar_h))
        pygame.draw.rect(bar_panel, (180, 40, 20, 180),
                        (40, hp_bar_y, bar_w, bar_h), width=1, border_radius=8)

        # 灵力条
        mp_label = self.font_manager.render_text("灵力值", "medium", (40, 120, 220), 18)
        bar_panel.blit(mp_label, (40, 132))
        mp_text = self.font_manager.render_text(
            f"{p.get('mp', 50)} / {p.get('max_mp', 50)}", "medium", (40, 30, 18), 16
        )
        bar_panel.blit(mp_text, (left_w - 40 - mp_text.get_width(), 132))

        mp_ratio = p.get("mp", 50) / p.get("max_mp", 50) if p.get("max_mp", 50) > 0 else 0
        mp_bar_y = 158
        pygame.draw.rect(bar_panel, (15, 20, 50),
                        (40, mp_bar_y, bar_w, bar_h), border_radius=8)
        fill_w = int(bar_w * mp_ratio)
        if fill_w > 0:
            for fx in range(fill_w):
                ratio = fx / bar_w
                pygame.draw.line(bar_panel,
                    (int(40 * (0.5 + ratio * 0.3)),
                     int(120 * (0.5 + ratio * 0.3)),
                     int(220 * (0.5 + ratio * 0.5))),
                    (40 + fx, mp_bar_y), (40 + fx, mp_bar_y + bar_h))
        pygame.draw.rect(bar_panel, (30, 100, 200, 180),
                        (40, mp_bar_y, bar_w, bar_h), width=1, border_radius=8)

        screen.blit(bar_panel, (margin, bottom_y))

        # --- 修炼系统面板 ---
        cult_x = margin + left_w + 15
        cult_panel = pygame.Surface((right_w, bottom_h), pygame.SRCALPHA)
        pygame.draw.rect(cult_panel, (232, 227, 214, 200),
                        (0, 0, right_w, bottom_h), border_radius=8)
        pygame.draw.rect(cult_panel, (80, 70, 55, 180),
                        (0, 0, right_w, bottom_h), width=2, border_radius=8)

        cp_title = self.font_manager.render_text("修炼系统", "medium", (50, 40, 25), 22)
        cult_panel.blit(cp_title, (20, 10))
        pygame.draw.line(cult_panel, (160, 150, 130, 80),
                        (20, 40), (right_w - 20, 40), 1)

        from character_panel import _get_cultivation_status_text, _get_cultivation_range, _can_breakthrough
        cultivation_status = _get_cultivation_status_text()
        progress_percent = int(progress / stage_total * 100) if stage_total > 0 else 0

        cultivation_info = [
            ("当前状态", cultivation_status, (100, 90, 75)),
            ("阶内进度", f"{progress_percent}% ({progress:,}/{stage_total:,})", (40, 30, 18)),
            ("修炼速度", f"{_get_cultivation_range()[0]}-{_get_cultivation_range()[1]}/5秒", (40, 30, 18)),
            ("自动修炼", "筑基期开启" if p["realm_index"] < 1 else "已开启", (40, 30, 18)),
        ]

        for i, (label, value, color) in enumerate(cultivation_info):
            ly = 52 + i * 32
            lbl = self.font_manager.render_text(f"{label}：", "medium", (100, 90, 75), 16)
            val = self.font_manager.render_text(value, "medium", color, 16)
            cult_panel.blit(lbl, (25, ly))
            cult_panel.blit(val, (130, ly))

        # 修炼按钮（大按钮居中）
        btn_w, btn_h = 180, 42
        btn_gap = 20
        btns_total_w = btn_w * 2 + btn_gap
        btn_start_x = (right_w - btns_total_w) // 2
        btn_y = 195

        self.cultivate_button = pygame.Rect(
            cult_x + btn_start_x, bottom_y + btn_y, btn_w, btn_h
        )
        self.breakthrough_button = pygame.Rect(
            cult_x + btn_start_x + btn_w + btn_gap, bottom_y + btn_y, btn_w, btn_h
        )
        self.cultivate_hovered = getattr(self, 'cultivate_hovered', False)
        self.breakthrough_hovered = getattr(self, 'breakthrough_hovered', False)

        state = realm_data.cultivation_state
        btn_text = "停止修炼" if state["is_cultivating"] else "开始修炼"
        can_break = _can_breakthrough()
        breakthrough_text = "突破！" if can_break else "修为不足"

        btn_color = (180, 160, 100) if self.cultivate_hovered else (150, 130, 80)
        pygame.draw.rect(cult_panel, btn_color,
                        (btn_start_x, btn_y, btn_w, btn_h), border_radius=6)
        pygame.draw.rect(cult_panel, (80, 70, 55),
                        (btn_start_x, btn_y, btn_w, btn_h), width=1, border_radius=6)
        btn_surf = self.font_manager.render_text(btn_text, "medium", (40, 30, 18), 18)
        cult_panel.blit(btn_surf, (btn_start_x + (btn_w - btn_surf.get_width()) // 2,
                                   btn_y + (btn_h - btn_surf.get_height()) // 2))

        breakthrough_color = (180, 160, 100) if self.breakthrough_hovered else (150, 130, 80)
        if not can_break:
            breakthrough_color = (120, 100, 60)
        b2_x = btn_start_x + btn_w + btn_gap
        pygame.draw.rect(cult_panel, breakthrough_color,
                        (b2_x, btn_y, btn_w, btn_h), border_radius=6)
        pygame.draw.rect(cult_panel, (80, 70, 55),
                        (b2_x, btn_y, btn_w, btn_h), width=1, border_radius=6)
        bt2 = self.font_manager.render_text(breakthrough_text, "medium",
                                           (40, 30, 18) if can_break else (100, 90, 75), 18)
        cult_panel.blit(bt2, (b2_x + (btn_w - bt2.get_width()) // 2,
                              btn_y + (btn_h - bt2.get_height()) // 2))

        screen.blit(cult_panel, (cult_x, bottom_y))

    def _draw_character_gongfa(self, screen):
        """功法子标签：已装备功法 + 已学会功法列表 + 修炼/遗忘操作"""
        # ========== 左侧：已装备功法槽位 ==========
        left_panel_w, left_panel_h = 480, 515
        left_x = 40
        left_y = 100

        left_panel = pygame.Surface((left_panel_w, left_panel_h), pygame.SRCALPHA)
        pygame.draw.rect(left_panel, (232, 227, 214, 200),
                        (0, 0, left_panel_w, left_panel_h), border_radius=8)
        pygame.draw.rect(left_panel, (80, 70, 55, 180),
                        (0, 0, left_panel_w, left_panel_h), width=2, border_radius=8)

        lp_title = self.font_manager.render_text("已装备功法", "medium", (50, 40, 25), 24)
        left_panel.blit(lp_title, (20, 10))

        slot_defs = [
            {"label": "灵技Ⅰ", "type_key": "灵技", "idx": 0, "y": 42, "color": (220, 80, 20), "h": 50},
            {"label": "灵技Ⅱ", "type_key": "灵技", "idx": 1, "y": 100, "color": (200, 60, 30), "h": 50},
            {"label": "灵技Ⅲ", "type_key": "灵技", "idx": 2, "y": 158, "color": (180, 50, 25), "h": 50},
            {"label": "内  经", "type_key": "内经", "idx": None, "y": 220, "color": (30, 160, 80), "h": 75},
            {"label": "心  法", "type_key": "心法", "idx": None, "y": 310, "color": (150, 100, 200), "h": 50},
        ]

        equipped = gongfa_data.player_gongfa.get("equipped", {})

        for sd in slot_defs:
            sy = sd["y"]
            slot_rect = pygame.Rect(15, sy, left_panel_w - 30, sd.get("h", 42))
            pygame.draw.rect(left_panel, (215, 210, 200, 120),
                           slot_rect, border_radius=4)
            pygame.draw.rect(left_panel, (*sd["color"], 100),
                           slot_rect, width=1, border_radius=4)

            slot_label = self.font_manager.render_text(sd["label"], "small", sd["color"], 16)
            left_panel.blit(slot_label, (20, sy + 2))

            # 从 equipped 获取该槽位的功法
            gongfa = None
            raw = equipped.get(sd["type_key"])
            if sd["idx"] is not None and isinstance(raw, list) and sd["idx"] < len(raw):
                gid = raw[sd["idx"]]
                if gid:
                    gongfa = gongfa_data.get_gongfa_by_id(gid)
            elif sd["idx"] is None and raw is not None:
                # 兼容旧存档：内经可能是 list 格式
                gid = raw[0] if isinstance(raw, list) and raw else raw
                if isinstance(gid, int):
                    gongfa = gongfa_data.get_gongfa_by_id(gid)

            if gongfa:
                gfx = 85
                qcolor = gongfa_data.QUALITY_DISPLAY_COLORS.get(
                    gongfa["quality"], (200, 200, 200)
                )
                gn = self.font_manager.render_text(gongfa["name"], "small", qcolor, 17)
                left_panel.blit(gn, (gfx, sy + 2))

                if gongfa["type"] == "内经":
                    # 显示侧重方向和修炼等级
                    focus = gongfa.get("focus", "气血")
                    nj_level = gongfa_data.player_gongfa.get("neijing_level", "入门")
                    focus_color = {"攻击": (220, 80, 20), "防御": (100, 160, 220),
                                   "气血": (200, 40, 30), "灵力": (40, 120, 220)}.get(focus, (150, 150, 150))
                    level_idx = gongfa_data.NEIJING_LEVELS.index(nj_level)
                    level_text = f"{'★' * (level_idx + 1)}{'☆' * (len(gongfa_data.NEIJING_LEVELS) - level_idx - 1)}"
                    focus_text = self.font_manager.render_text(
                        f"侧重：{focus}", "small", focus_color, 13)
                    level_surf = self.font_manager.render_text(
                        f"{nj_level} {level_text}", "small", (180, 160, 60), 13)
                    desc_text = f"攻+{gongfa.get('atk_bonus',0)} 防+{gongfa.get('def_bonus',0)} 血+{gongfa.get('hp_bonus',0)} 灵+{gongfa.get('mp_bonus',0)}"
                    left_panel.blit(focus_text, (gfx, sy + 22))
                    left_panel.blit(level_surf, (gfx + 120, sy + 22))
                    dt = self.font_manager.render_text(desc_text, "small", (110, 100, 85), 13)
                    left_panel.blit(dt, (gfx, sy + 38))
                else:
                    desc_text = gongfa.get("desc", "")
                    dt = self.font_manager.render_text(desc_text, "small", (110, 100, 85), 13)
                    left_panel.blit(dt, (gfx, sy + 24))
            else:
                empty_text = self.font_manager.render_text("空", "small", (160, 150, 140), 16)
                left_panel.blit(empty_text, (85, sy + 10))

        screen.blit(left_panel, (left_x, left_y))

        # ========== 右侧：已学会功法列表 + 操作 ==========
        right_x = left_x + left_panel_w + 25
        right_y = left_y
        right_panel_w = 700
        right_panel_h = 515

        right_panel = pygame.Surface((right_panel_w, right_panel_h), pygame.SRCALPHA)
        pygame.draw.rect(right_panel, (232, 227, 214, 200),
                        (0, 0, right_panel_w, right_panel_h), border_radius=8)
        pygame.draw.rect(right_panel, (80, 70, 55, 180),
                        (0, 0, right_panel_w, right_panel_h), width=2, border_radius=8)

        rp_title = self.font_manager.render_text("已学会功法", "medium", (50, 40, 25), 24)
        right_panel.blit(rp_title, (20, 10))

        # 功法类型筛选标签
        type_tabs = ["全部", "灵技", "内经", "心法"]
        self.gf_type_tab = getattr(self, 'gf_type_tab', "全部")
        self.gf_type_rects = {}
        tt_x = 140
        for tt in type_tabs:
            is_active = (tt == self.gf_type_tab)
            tt_rect = pygame.Rect(tt_x, 8, 50, 24)
            self.gf_type_rects[tt] = tt_rect
            if is_active:
                pygame.draw.rect(right_panel, (180, 140, 80, 200), tt_rect, border_radius=4)
                tt_color = (40, 30, 18)
            else:
                pygame.draw.rect(right_panel, (210, 200, 180, 140), tt_rect, border_radius=4)
                tt_color = (130, 110, 80)
            tt_surf = self.font_manager.render_text(tt, "small", tt_color, 14)
            right_panel.blit(tt_surf, (tt_x + (50 - tt_surf.get_width()) // 2, 10))
            tt_x += 58

        pygame.draw.line(right_panel, (160, 150, 130, 80), (20, 42), (right_panel_w - 20, 42), 1)

        # 已学会功法列表
        learned = gongfa_data.player_gongfa.get("learned", [])
        learned_gongfas = [gongfa_data.get_gongfa_by_id(gid) for gid in learned]
        learned_gongfas = [g for g in learned_gongfas if g is not None]

        # 类型筛选
        if self.gf_type_tab != "全部":
            learned_gongfas = [g for g in learned_gongfas if g["type"] == self.gf_type_tab]

        self.gf_buttons = []  # (rect, gongfa_dict, is_equipped)
        list_y = 52
        row_h = 34
        visible_rows = (right_panel_h - 70) // row_h
        self.gf_scroll = getattr(self, 'gf_scroll', 0)
        max_scroll = max(0, len(learned_gongfas) - visible_rows)
        self.gf_scroll = min(self.gf_scroll, max_scroll)

        start_idx = self.gf_scroll
        end_idx = min(start_idx + visible_rows, len(learned_gongfas))

        # 判断哪些功法已装备
        equipped_ids = set()
        for key, val in equipped.items():
            if val:
                if isinstance(val, dict):
                    equipped_ids.add(val["id"])
                elif isinstance(val, list):
                    equipped_ids.update(val)
                elif isinstance(val, int):
                    equipped_ids.add(val)

        for i in range(start_idx, end_idx):
            g = learned_gongfas[i]
            gy = list_y + (i - start_idx) * row_h
            is_equipped = g["id"] in equipped_ids

            # 行背景
            row_color = (180, 200, 180, 100) if is_equipped else (220, 215, 210, 120)
            pygame.draw.rect(right_panel, row_color, (15, gy, right_panel_w - 30, row_h - 2), border_radius=3)

            # 品质色标记
            qcolor = gongfa_data.QUALITY_DISPLAY_COLORS.get(g["quality"], (200, 200, 200))
            pygame.draw.rect(right_panel, qcolor, (18, gy + 4, 4, row_h - 10), border_radius=2)

            # 类型标签
            type_color = {"灵技": (220, 80, 20), "内经": (30, 140, 80), "心法": (150, 100, 200)}.get(g["type"], (150, 150, 150))
            type_surf = self.font_manager.render_text(g["type"], "small", type_color, 14)
            right_panel.blit(type_surf, (30, gy + (row_h - type_surf.get_height()) // 2))

            # 功法名
            name_surf = self.font_manager.render_text(g["name"], "small", qcolor, 14)
            right_panel.blit(name_surf, (80, gy + (row_h - name_surf.get_height()) // 2))

            # 状态文字
            status = "已装备" if is_equipped else "可修炼"
            status_color = (60, 140, 60) if is_equipped else (100, 90, 75)
            status_surf = self.font_manager.render_text(status, "small", status_color, 12)
            right_panel.blit(status_surf, (right_panel_w - 100, gy + (row_h - status_surf.get_height()) // 2))

            # 按钮
            btn_text_str = "遗忘" if is_equipped else "修炼"
            btn_color = (200, 80, 60) if is_equipped else (100, 160, 80)
            btn_rect = pygame.Rect(right_panel_w - 70, gy + 4, 48, row_h - 10)
            pygame.draw.rect(right_panel, btn_color, btn_rect, border_radius=4)
            btn_surf = self.font_manager.render_text(btn_text_str, "small", (255, 255, 255), 12)
            right_panel.blit(btn_surf, (btn_rect.x + (48 - btn_surf.get_width()) // 2,
                                       btn_rect.y + (btn_rect.h - btn_surf.get_height()) // 2))
            self.gf_buttons.append((btn_rect, g, is_equipped))

        # 滚动指示
        if max_scroll > 0:
            scroll_bar_h = int(right_panel_h * visible_rows / max(len(learned_gongfas), 1))
            scroll_bar_y = 52 + int((right_panel_h - 70 - scroll_bar_h) * self.gf_scroll / max_scroll)
            pygame.draw.rect(right_panel, (100, 90, 75, 100),
                           (right_panel_w - 12, scroll_bar_y, 6, scroll_bar_h), border_radius=3)

        screen.blit(right_panel, (right_x, right_y))

    def _learn_gongfa(self, gongfa):
        """装备（修炼）功法到对应槽位"""
        gtype = gongfa["type"]
        equipped = gongfa_data.player_gongfa.get("equipped", {})

        if gtype == "灵技":
            slots = equipped.get("灵技", [None, None, None])
            if isinstance(slots, list) and len(slots) == 3:
                for i in range(3):
                    if slots[i] is None:
                        slots[i] = gongfa["id"]
                        equipped["灵技"] = slots
                        return
                # 没空位，替换第一个
                slots[0] = gongfa["id"]
                equipped["灵技"] = slots
        elif gtype == "内经":
            # 单个内经槽位，装备后重置熟练度和等级
            equipped["内经"] = gongfa["id"]
            gongfa_data.player_gongfa["neijing_proficiency"] = 0
            gongfa_data.player_gongfa["neijing_level"] = "入门"
        elif gtype == "心法":
            equipped["心法"] = gongfa["id"]

    def _forget_gongfa(self, gongfa):
        """遗忘（卸下）功法"""
        gtype = gongfa["type"]
        equipped = gongfa_data.player_gongfa.get("equipped", {})

        if gtype == "灵技":
            slots = equipped.get("灵技", [])
            if isinstance(slots, list):
                for i in range(len(slots)):
                    if slots[i] == gongfa["id"]:
                        slots[i] = None
                        equipped["灵技"] = slots
                        return
        elif gtype == "内经":
            # 遗忘内经时重置熟练度
            equipped["内经"] = None
            gongfa_data.player_gongfa["neijing_proficiency"] = 0
            gongfa_data.player_gongfa["neijing_level"] = "入门"
        elif gtype == "心法":
            if equipped.get("心法") == gongfa["id"]:
                equipped["心法"] = None

    def _get_quality_color(self, quality):
        """根据品质获取颜色（支持字符串 "白/绿/蓝/紫/金" 或整数 1-5）"""
        color_map = {"白": (180, 180, 200), "绿": (100, 200, 100),
                     "蓝": (100, 150, 255), "紫": (200, 100, 255), "金": (255, 215, 0)}
        int_map = {1: "白", 2: "绿", 3: "蓝", 4: "紫", 5: "金"}
        if isinstance(quality, str):
            return color_map.get(quality, (255, 215, 0))
        key = int_map.get(quality, "金")
        return color_map.get(key, (255, 215, 0))

    def _get_inv_filtered_items(self):
        """获取当前分类下的物品"""
        if self.inv_active_category == 0:
            return self.inv_items
        cat_name = self.inv_categories[self.inv_active_category]
        return [item for item in self.inv_items if item.get("type") == cat_name]

    def _get_equip_slot_name_cn(self, slot_name):
        """装备槽位中文名"""
        names = {
            "weapon": "武器", "helmet": "头盔", "armor": "防具",
            "gloves": "手套", "belt": "腰带", "shoes": "鞋子",
            "accessory1": "饰品Ⅰ", "accessory2": "饰品Ⅱ",
        }
        return names.get(slot_name, slot_name)

    def draw_content_inventory(self, screen):
        """背包模块内容（含装备槽位、分类、分页）"""
        # 标题
        title = "背包 · 随身物品"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 8))

        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 52), (lx + 300, 52), 1)

        # ===== 装备槽位区（圆环环绕打坐人物） =====
        circle_cx, circle_cy = 290, 310
        equip_radius = 150
        equip_slot_w, equip_slot_h = 72, 56

        # 装备区标题
        etitle = self.font_manager.render_text("装备槽位", "medium", (180, 160, 120), 22)
        screen.blit(etitle, (circle_cx - etitle.get_width() // 2, 65))

        equip_slot_names = ["weapon", "helmet", "armor", "gloves", "belt", "shoes", "accessory1", "accessory2"]
        self.equip_slot_positions = {}

        for i, slot_name in enumerate(equip_slot_names):
            angle_deg = i * 45 - 90
            angle_rad = math.radians(angle_deg)
            sx = circle_cx + equip_radius * math.cos(angle_rad) - equip_slot_w // 2
            sy = circle_cy + equip_radius * math.sin(angle_rad) - equip_slot_h // 2
            self.equip_slot_positions[slot_name] = (sx, sy, equip_slot_w, equip_slot_h)

            eq = self.equipment_slots[slot_name]
            is_sel = (self.inv_selected_slot == slot_name)

            slot_bg = (100, 80, 180) if is_sel else (150, 130, 80)
            slot_bd = (160, 80, 255) if is_sel else (180, 160, 120)
            pygame.draw.rect(screen, (*slot_bg, 180), (sx, sy, equip_slot_w, equip_slot_h), border_radius=8)
            pygame.draw.rect(screen, (*slot_bd, 150), (sx, sy, equip_slot_w, equip_slot_h), width=1, border_radius=8)

            label_s = self.font_manager.render_text(self._get_equip_slot_name_cn(slot_name), "small", (200, 190, 160), 13)
            screen.blit(label_s, (sx + (equip_slot_w - label_s.get_width()) // 2, sy + 4))

            if eq:
                qc = self._get_quality_color(eq.get("quality", 1))
                eqs = self.font_manager.render_text(eq["name"][:4], "small", qc, 13)
            else:
                eqs = self.font_manager.render_text("空", "small", (160, 150, 140), 14)
            screen.blit(eqs, (sx + (equip_slot_w - eqs.get_width()) // 2, sy + 24))

        # ===== 角色人物图片 =====
        char_img = _load_main_menu_char()
        if char_img:
            iw, ih = char_img.get_size()
            char_x = circle_cx - iw // 2
            char_y = circle_cy - ih // 2
            screen.blit(char_img, (char_x, char_y))

        # 光环（淡色灵气圈）
        for r_offset in range(3):
            alpha = 40 - r_offset * 12
            glow_radius = equip_radius + 8 + r_offset * 5
            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (180, 160, 100, alpha), (glow_radius, glow_radius), glow_radius, width=1)
            screen.blit(glow, (circle_cx - glow_radius, circle_cy - glow_radius))

        # ===== 物品格子区域（最右边，离右边缘1个槽位） =====
        slot_w, slot_h = 80, 72
        slot_gap_x, slot_gap_y = 12, 10
        grid_cols = self.inv_grid_cols
        grid_rows = self.inv_grid_rows
        grid_total_w = grid_cols * slot_w + (grid_cols - 1) * slot_gap_x
        grid_start_x = self.screen_width - (slot_w + slot_gap_x) - grid_total_w
        grid_start_y = 105

        # 装备详情面板的参考X坐标（物品格子区域右边缘）
        equip_panel_x = grid_start_x + grid_total_w

        # 分类标签栏（放在物品格子正上方）
        cat_w, cat_h = 72, 26
        cat_gap = 5
        total_cat_w = len(self.inv_categories) * cat_w + (len(self.inv_categories) - 1) * cat_gap
        cat_start_x = grid_start_x + (grid_cols * (slot_w + slot_gap_x) - slot_gap_x - total_cat_w) // 2
        cat_y = 62

        for i, cat_name in enumerate(self.inv_categories):
            cx = cat_start_x + i * (cat_w + cat_gap)
            cat_rect = pygame.Rect(cx, cat_y, cat_w, cat_h)
            is_active = (i == self.inv_active_category)

            if is_active:
                pygame.draw.rect(screen, (160, 80, 255, 200), cat_rect, border_radius=5)
                pygame.draw.rect(screen, (200, 140, 255, 220), cat_rect, width=1, border_radius=5)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(screen, (150, 130, 80, 140), cat_rect, border_radius=5)
                pygame.draw.rect(screen, (180, 160, 120, 100), cat_rect, width=1, border_radius=5)
                text_color = (220, 210, 190)

            cs = self.font_manager.render_text(cat_name, "small", text_color, 14)
            screen.blit(cs, (cx + (cat_w - cs.get_width()) // 2, cat_y + (cat_h - cs.get_height()) // 2))

        filtered = self._get_inv_filtered_items()
        total_pages = max(1, (len(filtered) + self.inv_items_per_page - 1) // self.inv_items_per_page)
        self.inv_page = min(self.inv_page, total_pages - 1)

        start_idx = self.inv_page * self.inv_items_per_page
        page_items = filtered[start_idx:start_idx + self.inv_items_per_page]

        for i in range(self.inv_items_per_page):
            col = i % grid_cols
            row = i // grid_cols
            sx = grid_start_x + col * (slot_w + slot_gap_x)
            sy = grid_start_y + row * (slot_h + slot_gap_y)

            item = page_items[i] if i < len(page_items) else None
            is_sel = (self.inv_selected_item and item and self.inv_selected_item.get("id") == item.get("id"))

            # 格子背景
            if is_sel:
                bg_c = (100, 80, 180)
                bd_c = (160, 80, 255)
            elif item:
                bg_c = (160, 150, 140)
                bd_c = (190, 180, 160)
            else:
                bg_c = (180, 175, 165)
                bd_c = (200, 195, 185)

            pygame.draw.rect(screen, (*bg_c, 150), (sx, sy, slot_w, slot_h), border_radius=5)
            pygame.draw.rect(screen, (*bd_c, 100), (sx, sy, slot_w, slot_h), width=1, border_radius=5)

            if item:
                qc = self._get_quality_color(item.get("quality", 1))
                pygame.draw.rect(screen, qc, (sx, sy, slot_w, slot_h), width=2, border_radius=5)

                ns = self.font_manager.render_text(item["name"][:4], "small", qc, 15)
                screen.blit(ns, (sx + (slot_w - ns.get_width()) // 2, sy + 5))

                ts2 = self.font_manager.render_text(item.get("type", "")[:3], "small", (100, 90, 75), 12)
                screen.blit(ts2, (sx + (slot_w - ts2.get_width()) // 2, sy + 28))

                if item.get("count", 1) > 1:
                    cnt_s = self.font_manager.render_text(f"x{item['count']}", "small", (0, 180, 180), 13)
                    screen.blit(cnt_s, (sx + slot_w - cnt_s.get_width() - 3, sy + slot_h - cnt_s.get_height() - 2))
            else:
                empty_s = self.font_manager.render_text("空", "small", (160, 150, 140), 14)
                screen.blit(empty_s, (sx + (slot_w - empty_s.get_width()) // 2, sy + (slot_h - empty_s.get_height()) // 2))

        # ===== 分页按钮 =====
        page_btn_w, page_btn_h = 90, 32
        page_y = grid_start_y + grid_rows * (slot_h + slot_gap_y) + 12

        # 前一页按钮
        prev_rect = pygame.Rect(grid_start_x, page_y, page_btn_w, page_btn_h)
        prev_color = (160, 140, 80) if self.inv_page > 0 else (120, 110, 80)
        pygame.draw.rect(screen, (*prev_color, 180), prev_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 160, 120, 120), prev_rect, width=1, border_radius=5)
        prev_s = self.font_manager.render_text("← 前一页", "small", (200, 190, 160) if self.inv_page > 0 else (140, 130, 110), 15)
        screen.blit(prev_s, (prev_rect.x + (page_btn_w - prev_s.get_width()) // 2, prev_rect.y + 7))

        # 后一页按钮
        next_x = grid_start_x + grid_cols * (slot_w + slot_gap_x) - slot_gap_x - page_btn_w
        next_rect = pygame.Rect(next_x, page_y, page_btn_w, page_btn_h)
        next_color = (160, 140, 80) if self.inv_page < total_pages - 1 else (120, 110, 80)
        pygame.draw.rect(screen, (*next_color, 180), next_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 160, 120, 120), next_rect, width=1, border_radius=5)
        next_s = self.font_manager.render_text("后一页 →", "small", (200, 190, 160) if self.inv_page < total_pages - 1 else (140, 130, 110), 15)
        screen.blit(next_s, (next_rect.x + (page_btn_w - next_s.get_width()) // 2, next_rect.y + 7))

        # 页码指示
        page_info = f"第 {self.inv_page + 1} / {total_pages} 页"
        pi_s = self.font_manager.render_text(page_info, "small", (160, 150, 140), 15)
        screen.blit(pi_s, (prev_rect.right + 20, page_y + 8))

        # ===== 物品详情（右下） =====
        if self.inv_selected_item:
            detail_x = grid_start_x
            detail_y = page_y + page_btn_h + 10
            detail_w = 350
            detail_h = 115

            detail_surf = pygame.Surface((detail_w, detail_h), pygame.SRCALPHA)
            pygame.draw.rect(detail_surf, (232, 227, 214, 210), (0, 0, detail_w, detail_h), border_radius=8)
            pygame.draw.rect(detail_surf, (100, 90, 75, 160), (0, 0, detail_w, detail_h), width=1, border_radius=8)
            screen.blit(detail_surf, (detail_x, detail_y))

            item = self.inv_selected_item
            qc = self._get_quality_color(item.get("quality", 1))

            dn = self.font_manager.render_text(item["name"], "medium", qc, 20)
            screen.blit(dn, (detail_x + 12, detail_y + 8))

            q_str = str(item.get('quality', ''))
            q_star_count = {"白": 1, "绿": 2, "蓝": 3, "紫": 4, "金": 5}.get(q_str, 1)
            dt = self.font_manager.render_text(f"类型：{item.get('type', '未知')}  |  品质：{'★' * q_star_count}", "small", (100, 90, 75), 15)
            screen.blit(dt, (detail_x + 12, detail_y + 38))

            dc = self.font_manager.render_text(f"数量：{item.get('count', 1)}", "small", (0, 180, 180), 15)
            screen.blit(dc, (detail_x + 12, detail_y + 60))

            dd = self.font_manager.render_text(item.get("desc", "暂无描述"), "small", (120, 110, 95), 14)
            screen.blit(dd, (detail_x + 12, detail_y + 82))

            # 装备按钮（仅装备类型物品显示）
            if item.get("type") == "装备":
                eq_btn_w, eq_btn_h = 80, 28
                eq_btn_x = detail_x + detail_w - eq_btn_w - 15
                eq_btn_y = detail_y + detail_h - eq_btn_h - 8
                self.inv_equip_btn_rect = pygame.Rect(eq_btn_x, eq_btn_y, eq_btn_w, eq_btn_h)
                pygame.draw.rect(screen, (60, 140, 80, 200), self.inv_equip_btn_rect, border_radius=5)
                pygame.draw.rect(screen, (80, 180, 100, 220), self.inv_equip_btn_rect, width=1, border_radius=5)
                eq_btn_s = self.font_manager.render_text("装备", "small", (220, 240, 220), 16)
                screen.blit(eq_btn_s, (eq_btn_x + (eq_btn_w - eq_btn_s.get_width()) // 2, eq_btn_y + 5))
            else:
                self.inv_equip_btn_rect = None

        # ===== 装备详情（右下偏右） =====
        if self.inv_selected_slot and self.equipment_slots[self.inv_selected_slot]:
            ed_x = equip_panel_x - 260
            ed_y = page_y + page_btn_h + 10
            ed_w = 250
            ed_h = 115

            ed_surf = pygame.Surface((ed_w, ed_h), pygame.SRCALPHA)
            pygame.draw.rect(ed_surf, (232, 227, 214, 210), (0, 0, ed_w, ed_h), border_radius=8)
            pygame.draw.rect(ed_surf, (100, 90, 75, 160), (0, 0, ed_w, ed_h), width=1, border_radius=8)
            screen.blit(ed_surf, (ed_x, ed_y))

            eq = self.equipment_slots[self.inv_selected_slot]
            qc = self._get_quality_color(eq.get("quality", 1))
            sn_cn = self._get_equip_slot_name_cn(self.inv_selected_slot)

            en = self.font_manager.render_text(f"{sn_cn}：{eq['name']}", "medium", qc, 18)
            screen.blit(en, (ed_x + 12, ed_y + 8))

            eq_q = eq.get('quality', 1)
            eq_stars = eq_q if isinstance(eq_q, int) else {"白": 1, "绿": 2, "蓝": 3, "紫": 4, "金": 5}.get(str(eq_q), 1)
            et = self.font_manager.render_text(f"品质：{'★' * eq_stars}  |  类型：{eq.get('type', '未知')}", "small", (100, 90, 75), 14)
            screen.blit(et, (ed_x + 12, ed_y + 38))

            stats = []
            for k, v in eq.items():
                if k not in ("name", "type", "quality", "description", "id") and v:
                    stats.append(f"{k}: +{v}")
            if stats:
                st_s = self.font_manager.render_text("  ".join(stats), "small", (0, 180, 180), 14)
                screen.blit(st_s, (ed_x + 12, ed_y + 60))

            ed_desc = self.font_manager.render_text(eq.get("desc", eq.get("description", "")), "small", (120, 110, 95), 13)
            screen.blit(ed_desc, (ed_x + 12, ed_y + 82))

    def draw_content_sect(self, screen):
        """宗门模块内容"""
        import sect_data as sd

        player_realm = realm_data.player["realm_index"]
        if player_realm < 1:
            self._draw_sect_locked(screen, player_realm)
            return

        if not sd.player_sect["joined"]:
            self._draw_sect_not_joined(screen, player_realm)
        else:
            self._draw_sect_joined(screen)

    def _draw_sect_locked(self, screen, player_realm):
        """未达到筑基期 - 锁定界面"""
        title = "宗门 · 仙门世家"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))
        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)
        lines = [
            "天下修仙者，皆聚于宗门之下", "",
            "加入宗门可获修炼加成、专属功法与秘境资格",
            "宗门贡献可兑换丹药法宝", "",
            f"—— 需达到筑基期（当前：{realm_data.get_realm_name(player_realm)}期）——",
        ]
        for i, line in enumerate(lines):
            y = 140 + i * 32
            color = (50, 40, 25) if i == 0 else (100, 90, 75)
            size = 26 if i == 0 else 18
            ls = self.font_manager.render_text(line, "medium", color, size)
            screen.blit(ls, ((self.screen_width - ls.get_width()) // 2, y))

    def _draw_sect_not_joined(self, screen, player_realm):
        """已解锁但未加入宗门 - 显示宗门选择列表"""
        import sect_data as sd
        title = "宗门 · 仙门世家"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))
        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)

        # 上方提示
        hint = self.font_manager.render_text("选择一方宗门，踏上修仙之路", "medium", (80, 70, 55), 20)
        screen.blit(hint, ((self.screen_width - hint.get_width()) // 2, 90))

        # 可加入宗门网格
        available_sects = sd.get_available_sects(player_realm)
        self.sect_buttons = []

        panel_w, panel_h = 850, 370
        panel_x = (self.screen_width - panel_w) // 2
        panel_y = 125
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 200), (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (80, 70, 55, 180), (0, 0, panel_w, panel_h), width=2, border_radius=8)

        y_offset = 15
        for star in sorted(available_sects.keys()):
            star_realm = realm_data.get_realm_name(star)
            st = self.font_manager.render_text(f"{star}星宗门（{star_realm}期可加入）", "small", (80, 70, 55), 18)
            panel.blit(st, (20, y_offset))
            y_offset += 28

            sects_in_star = available_sects[star]
            col_w, col_gap = 260, 15
            card_h = 78
            cols = 3
            col = 0
            for sect_name, sect_info in sects_in_star.items():
                cx = 20 + col * (col_w + col_gap)
                cy = y_offset
                card = pygame.Surface((col_w, card_h), pygame.SRCALPHA)
                card_color = sect_info["color"]
                pygame.draw.rect(card, (*card_color, 40), (0, 0, col_w, card_h), border_radius=6)
                pygame.draw.rect(card, (*card_color, 180), (0, 0, col_w, card_h), width=2, border_radius=6)

                nt = self.font_manager.render_text(sect_name, "small", (40, 30, 20), 18)
                card.blit(nt, (10, 8))
                fl = self.font_manager.render_text(f"特性：{sect_info['feature']}", "small", (0, 120, 100), 13)
                card.blit(fl, (10, 32))

                desc_lines = self._wrap_text(sect_info["feature_desc"], 28, col_w - 80)
                for i, line in enumerate(desc_lines[:2]):
                    dl = self.font_manager.render_text(line, "small", (100, 90, 75), 11)
                    card.blit(dl, (10, 50 + i * 14))

                # 加入按钮
                btn_w, btn_h = 52, 22
                btn_x = col_w - btn_w - 8
                btn_y = card_h - btn_h - 8
                pygame.draw.rect(card, (60, 140, 80), (btn_x, btn_y, btn_w, btn_h), border_radius=4)
                jt = self.font_manager.render_text("加入", "small", (255, 255, 255), 12)
                card.blit(jt, (btn_x + (btn_w - jt.get_width()) // 2, btn_y + (btn_h - jt.get_height()) // 2))

                panel.blit(card, (cx, cy))
                self.sect_buttons.append({
                    "sect_name": sect_name,
                    "rect": pygame.Rect(panel_x + cx + btn_x, panel_y + cy + btn_y, btn_w, btn_h),
                })
                col += 1
            y_offset += card_h + 20
        screen.blit(panel, (panel_x, panel_y))

    def _draw_sect_joined(self, screen):
        """已加入宗门 - 内部界面（主殿/执事殿/贡献堂/参悟堂）"""
        import sect_data as sd
        sect = sd.player_sect
        info = sd.get_sect_info(sect["sect_name"])
        rank = sd.get_current_rank()

        # 顶部横幅
        title = f"{sect['sect_name']} · {'★' * sect['sect_star']}宗门"
        ts = self.font_manager.render_text(title, "title", info["color"], 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 20))

        # 顶部信息条
        info_y = 68
        contrib_text = f"贡献：{sect['contribution']}  |  职位：{rank['name']}"
        ct = self.font_manager.render_text(contrib_text, "medium", (160, 130, 80), 20)
        screen.blit(ct, ((self.screen_width - ct.get_width()) // 2, info_y))

        # 子标签栏
        sub_tabs = ["主殿", "执事殿", "贡献堂", "参悟堂"]
        sub_tab_w = 110
        sub_tab_h = 36
        sub_tab_gap = 8
        sub_total_w = len(sub_tabs) * sub_tab_w + (len(sub_tabs) - 1) * sub_tab_gap
        sub_tab_y = 100
        sub_tab_start_x = (self.screen_width - sub_total_w) // 2

        self.sect_sub_rects = []
        for i, name in enumerate(sub_tabs):
            tx = sub_tab_start_x + i * (sub_tab_w + sub_tab_gap)
            is_active = getattr(self, 'sect_sub_tab', 'main') == name
            tab_surf = pygame.Surface((sub_tab_w, sub_tab_h), pygame.SRCALPHA)
            c1 = (80, 65, 45, 220) if is_active else (50, 40, 28, 160)
            pygame.draw.rect(tab_surf, c1, (0, 0, sub_tab_w, sub_tab_h),
                            border_top_left_radius=6, border_top_right_radius=6)
            if is_active:
                pygame.draw.line(tab_surf, (180, 160, 100, 200), (10, 3), (sub_tab_w - 10, 3), 3)
            text_color = (220, 210, 190) if is_active else (140, 130, 110)
            tn = self.font_manager.render_text(name, "small", text_color, 20)
            tab_surf.blit(tn, ((sub_tab_w - tn.get_width()) // 2, (sub_tab_h - tn.get_height()) // 2))
            screen.blit(tab_surf, (tx, sub_tab_y))
            self.sect_sub_rects.append({
                "name": name,
                "rect": pygame.Rect(tx, sub_tab_y, sub_tab_w, sub_tab_h),
            })

        # 内容区
        sub = getattr(self, 'sect_sub_tab', 'main')
        if sub == "主殿":
            self._draw_sect_main_hall(screen, sect, info, rank)
        elif sub == "执事殿":
            self._draw_sect_task_hall(screen, sect, rank)
        elif sub == "贡献堂":
            self._draw_sect_contrib_hall(screen, sect, info)
        elif sub == "参悟堂":
            self._draw_sect_meditation(screen, sect, rank)

    def _draw_sect_main_hall(self, screen, sect, info, rank):
        """主殿：宗门信息 + 职位 + 退出"""
        import sect_data as sd
        panel_y = 148
        panel_w, panel_h = 750, 320
        panel_x = (self.screen_width - panel_w) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 200), (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (80, 70, 55, 180), (0, 0, panel_w, panel_h), width=2, border_radius=8)

        # 宗门描述
        y = 15
        ds = self.font_manager.render_text(info["desc"], "small", (100, 90, 75), 16)
        panel.blit(ds, (15, y))
        y += 28

        feature = sd.get_player_sect_feature()
        if feature:
            ft_text = f"宗门特性：【{feature['feature']}】{feature['feature_desc']}"
            ft_lines = self._wrap_text(ft_text, 50, panel_w - 30)
            for line in ft_lines:
                fl = self.font_manager.render_text(line, "small", (0, 150, 120), 15)
                panel.blit(fl, (15, y))
                y += 20

        y += 10
        pygame.draw.line(panel, (120, 110, 95, 80), (15, y), (panel_w - 15, y), 1)
        y += 15

        # 职位信息
        rank_title = self.font_manager.render_text("宗门职位", "medium", (50, 40, 25), 20)
        panel.blit(rank_title, (15, y))
        y += 28

        for rk in sd.SECT_RANKS:
            is_current = rk["id"] == sect["rank"]
            marker = "◆" if is_current else "○"
            name_color = (180, 140, 100) if is_current else (100, 90, 75)
            line = f"{marker} {rk['name']} — 需贡献 {rk['contrib_required']}  |  任务上限 Lv{rk['max_task_lv']}  |  参悟 ×{rk['meditate_bonus']:.0%}"
            rl = self.font_manager.render_text(line, "small", name_color, 14)
            panel.blit(rl, (25, y))
            y += 22

        # 晋升按钮
        next_rank = sd.get_next_rank()
        promote_btn_w, promote_btn_h = 160, 32
        promote_btn_x = 15
        promote_btn_y = panel_h - promote_btn_h - 15
        if next_rank:
            pygame.draw.rect(panel, (80, 160, 100), (promote_btn_x, promote_btn_y, promote_btn_w, promote_btn_h), border_radius=6)
            pt = self.font_manager.render_text(f"晋升 {next_rank['name']}", "small", (255, 255, 240), 14)
            panel.blit(pt, (promote_btn_x + (promote_btn_w - pt.get_width()) // 2, promote_btn_y + (promote_btn_h - pt.get_height()) // 2))
            self.promote_btn_rect = pygame.Rect(panel_x + promote_btn_x, panel_y + promote_btn_y, promote_btn_w, promote_btn_h)
        else:
            mt = self.font_manager.render_text("已达最高职位", "small", (150, 130, 100), 16)
            panel.blit(mt, (promote_btn_x + 10, promote_btn_y + 8))
            self.promote_btn_rect = None

        # 退出宗门按钮
        leave_btn_w, leave_btn_h = 120, 32
        leave_btn_x = panel_w - leave_btn_w - 15
        leave_btn_y = panel_h - leave_btn_h - 15
        pygame.draw.rect(panel, (180, 60, 60), (leave_btn_x, leave_btn_y, leave_btn_w, leave_btn_h), border_radius=6)
        lt = self.font_manager.render_text("退出宗门", "small", (255, 240, 240), 14)
        panel.blit(lt, (leave_btn_x + (leave_btn_w - lt.get_width()) // 2, leave_btn_y + (leave_btn_h - lt.get_height()) // 2))
        self.leave_button_rect = pygame.Rect(panel_x + leave_btn_x, panel_y + leave_btn_y, leave_btn_w, leave_btn_h)

        screen.blit(panel, (panel_x, panel_y))

    def _draw_sect_task_hall(self, screen, sect, rank):
        """执事殿：任务接取与管理"""
        import sect_data as sd
        import time as _time

        sd.update_tasks()  # 结算已完成任务

        panel_y = 148
        panel_w, panel_h = 750, 320
        panel_x = (self.screen_width - panel_w) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 200), (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (80, 70, 55, 180), (0, 0, panel_w, panel_h), width=2, border_radius=8)

        # 当前任务状态
        task_lv = sect["task_lv"]
        task_info = None
        for tl in sd.TASK_LEVELS:
            if tl["lv"] == task_lv:
                task_info = tl
                break

        y = 15
        title = self.font_manager.render_text("当前任务", "medium", (50, 40, 25), 20)
        panel.blit(title, (15, y))
        y += 30

        if task_info:
            line1 = f"【Lv{task_info['lv']}】{task_info['name']} — {task_info['contrib_per_min']}贡献/分钟，{task_info['time_minutes']}分钟/轮"
            l1 = self.font_manager.render_text(line1, "small", (60, 50, 40), 16)
            panel.blit(l1, (15, y))
            y += 26

            # 进度条
            prog, remain = sd.get_task_progress()
            bar_w, bar_h = panel_w - 60, 22
            bar_x, bar_y = 30, y
            pygame.draw.rect(panel, (60, 50, 35, 150), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            pygame.draw.rect(panel, (0, 180, 120), (bar_x, bar_y, int(bar_w * prog), bar_h), border_radius=4)
            rem_m = max(0, int(remain // 60))
            rem_s = max(0, int(remain % 60))
            pt = self.font_manager.render_text(f"{prog*100:.0f}%   剩余 {rem_m}:{rem_s:02d}", "small", (255, 255, 240), 14)
            panel.blit(pt, (bar_x + bar_w // 2 - pt.get_width() // 2, bar_y + 2))
            y += bar_h + 25

        # 任务等级选择
        sel_title = self.font_manager.render_text(f"更换任务等级（当前职位{rank['name']}，最高可接 Lv{rank['max_task_lv']}任务）", "small", (80, 70, 55), 15)
        panel.blit(sel_title, (15, y))
        y += 28

        self.task_lv_buttons = []
        col_w = 135
        for i, tl in enumerate(sd.TASK_LEVELS):
            cx = 15 + i * (col_w + 10)
            locked = tl["lv"] > rank["max_task_lv"]
            active = tl["lv"] == task_lv

            card = pygame.Surface((col_w, 70), pygame.SRCALPHA)
            bg = (100, 80, 60, 40) if locked else ((0, 150, 120, 50) if active else (80, 70, 55, 30))
            pygame.draw.rect(card, bg, (0, 0, col_w, 70), border_radius=6)
            border = (120, 100, 80) if locked else ((0, 200, 160) if active else (100, 90, 75))
            pygame.draw.rect(card, border, (0, 0, col_w, 70), width=1, border_radius=6)

            nm = self.font_manager.render_text(tl["name"], "small", (100, 90, 75) if locked else (50, 40, 25), 14)
            card.blit(nm, (8, 8))
            info_line = f"Lv{tl['lv']} · {tl['contrib_per_min']}贡/分 · {tl['time_minutes']}分"
            il = self.font_manager.render_text(info_line, "small", (120, 110, 95) if locked else (80, 70, 55), 10)
            card.blit(il, (8, 30))
            status_t = "已锁定" if locked else ("进行中" if active else "点击切换")
            stc = self.font_manager.render_text(status_t, "small", (180, 80, 80) if locked else ((0, 150, 120) if active else (0, 100, 180)), 11)
            card.blit(stc, (8, 48))

            panel.blit(card, (cx, y))
            if not locked and not active:
                self.task_lv_buttons.append({
                    "lv": tl["lv"],
                    "rect": pygame.Rect(panel_x + cx, panel_y + y, col_w, 70),
                })

        # 规则说明
        rule_y = panel_h - 50
        rule = self.font_manager.render_text("任务自动循环执行，完成后自动开始下一轮，无需手动接取", "small", (120, 110, 95), 12)
        panel.blit(rule, (15, rule_y))

        screen.blit(panel, (panel_x, panel_y))

    def _draw_sect_contrib_hall(self, screen, sect, info):
        """贡献堂：消耗贡献兑换物品"""
        import sect_data as sd

        panel_y = 148
        panel_w, panel_h = 750, 320
        panel_x = (self.screen_width - panel_w) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 200), (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (80, 70, 55, 180), (0, 0, panel_w, panel_h), width=2, border_radius=8)

        # 分类标签
        categories = list(sd.CONTRIB_SHOP.keys())
        if not hasattr(self, 'shop_category'):
            self.shop_category = "功法"
        cat_w = 80
        cat_h = 28
        cat_gap = 6
        cat_y = 10
        self.shop_cat_rects = []
        for i, cat in enumerate(categories):
            cx = 15 + i * (cat_w + cat_gap)
            is_active = self.shop_category == cat
            color = (80, 65, 45, 200) if is_active else (50, 40, 28, 140)
            pygame.draw.rect(panel, color, (cx, cat_y, cat_w, cat_h), border_radius=4)
            txt_color = (220, 210, 190) if is_active else (140, 130, 110)
            ct = self.font_manager.render_text(cat, "small", txt_color, 14)
            panel.blit(ct, (cx + (cat_w - ct.get_width()) // 2, cat_y + (cat_h - ct.get_height()) // 2))
            self.shop_cat_rects.append({"cat": cat, "rect": pygame.Rect(panel_x + cx, panel_y + cat_y, cat_w, cat_h)})

        # 物品列表
        items = sd.CONTRIB_SHOP.get(self.shop_category, [])
        col_w = 155
        col_gap = 12
        card_h = 72
        cols = 4
        y = cat_y + cat_h + 12

        self.shop_item_rects = []
        for i, item in enumerate(items):
            col = i % cols
            row = i // cols
            cx = 15 + col * (col_w + col_gap)
            cy = y + row * (card_h + 10)
            if cy + card_h > panel_h - 10:
                break

            card = pygame.Surface((col_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (80, 70, 55, 30), (0, 0, col_w, card_h), border_radius=6)
            pygame.draw.rect(card, (100, 90, 75, 150), (0, 0, col_w, card_h), width=1, border_radius=6)

            nm = self.font_manager.render_text(item["name"], "small", (50, 40, 25), 14)
            card.blit(nm, (8, 6))
            ds = self.font_manager.render_text(item["desc"], "small", (100, 90, 75), 11)
            card.blit(ds, (8, 28))

            cost = item["cost"]
            feature = sd.get_player_sect_feature()
            if item["type"] == "equip" and feature and feature["feature_type"] == "equip_discount":
                cost = int(cost * feature["feature_value"])

            cs = self.font_manager.render_text(f"{cost}贡献", "small", (180, 140, 100), 13)
            card.blit(cs, (col_w - cs.get_width() - 8, card_h - 20))

            panel.blit(card, (cx, cy))
            self.shop_item_rects.append({
                "cat": self.shop_category,
                "index": i,
                "rect": pygame.Rect(panel_x + cx, panel_y + cy, col_w, card_h),
            })

        screen.blit(panel, (panel_x, panel_y))

    def _draw_sect_meditation(self, screen, sect, rank):
        """参悟堂：消耗贡献提升修炼速度"""
        import sect_data as sd
        import time as _time

        panel_y = 148
        panel_w, panel_h = 750, 320
        panel_x = (self.screen_width - panel_w) // 2

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 200), (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (80, 70, 55, 180), (0, 0, panel_w, panel_h), width=2, border_radius=8)

        y = 15
        title = self.font_manager.render_text("参悟堂 · 天地灵气汇聚之地", "medium", (50, 40, 25), 22)
        panel.blit(title, (15, y))
        y += 35

        desc = self.font_manager.render_text("在此参悟天地大道，提升修炼速度（持续1小时）", "small", (100, 90, 75), 16)
        panel.blit(desc, (15, y))
        y += 30

        # 职位倍率表
        rate_title = self.font_manager.render_text("各职位参悟倍率：", "small", (80, 70, 55), 15)
        panel.blit(rate_title, (15, y))
        y += 22

        for rk in sd.SECT_RANKS:
            marker = "◆ " if rk["id"] == rank["id"] else "  "
            color = (180, 140, 100) if rk["id"] == rank["id"] else (120, 110, 95)
            line = f"{marker}{rk['name']}：×{rk['meditate_bonus']:.0%}"
            rl = self.font_manager.render_text(line, "small", color, 14)
            panel.blit(rl, (25, y))
            y += 20

        y += 10
        pygame.draw.line(panel, (120, 110, 95, 80), (15, y), (panel_w - 15, y), 1)
        y += 15

        # 当前参悟状态
        active, remain, bonus = sd.get_meditate_status()
        if active:
            rem_m = int(remain // 60)
            rem_s = int(remain % 60)
            st_line = f"参悟中 · 修炼速度 ×{bonus:.0%} · 剩余 {rem_m}:{rem_s:02d}"
            sl = self.font_manager.render_text(st_line, "medium", (0, 160, 120), 20)
            panel.blit(sl, (15, y))
            y += 28

            # 进度条
            bar_w, bar_h = panel_w - 60, 18
            bar_prog = remain / sd.player_sect["meditate_duration"]
            pygame.draw.rect(panel, (60, 50, 35, 150), (30, y, bar_w, bar_h), border_radius=4)
            pygame.draw.rect(panel, (200, 140, 40), (30, y, int(bar_w * bar_prog), bar_h), border_radius=4)
            y += bar_h + 10
        else:
            sl = self.font_manager.render_text("当前未在参悟", "small", (150, 120, 90), 16)
            panel.blit(sl, (15, y))
            y += 28

            # 开始参悟按钮
            btn_w, btn_h = 180, 40
            pygame.draw.rect(panel, (80, 160, 100), (15, y, btn_w, btn_h), border_radius=8)
            btn_t = self.font_manager.render_text(f"开始参悟（30贡献）", "small", (255, 255, 240), 16)
            panel.blit(btn_t, (15 + (btn_w - btn_t.get_width()) // 2, y + (btn_h - btn_t.get_height()) // 2))
            self.meditate_btn_rect = pygame.Rect(panel_x + 15, panel_y + y, btn_w, btn_h)

        screen.blit(panel, (panel_x, panel_y))

    def draw_content_craft(self, screen):
        """炼制模块内容 - 炼丹/炼器/绘符三个子选项"""
        # 如果进入炼丹子界面
        if self.craft_sub_tab == "炼丹":
            self.draw_content_alchemy(screen)
            return
        # 如果进入炼器子界面
        if self.craft_sub_tab == "炼器":
            self.draw_content_forge(screen)
            return

        title = "炼制 · 造化万物"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))

        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)

        sub_text = "选择炼制方向"
        st = self.font_manager.render_text(sub_text, "medium", (100, 90, 75), 24)
        screen.blit(st, ((self.screen_width - st.get_width()) // 2, 100))

        # 三个子选项卡片
        sub_options = [
            ("炼丹", "以草木金石，炼就仙丹灵药\n提升修为、恢复伤势", "丹"),
            ("炼器", "熔铸天材地宝，锻造法宝神兵\n强化战力、攻防兼备", "器"),
            ("绘符", "引天地灵气入符箓\n临敌制胜、妙用无穷", "符"),
        ]

        card_w, card_h = 300, 200
        gap = 30
        total_w = card_w * 3 + gap * 2
        start_x = (self.screen_width - total_w) // 2
        card_y = 160

        self.craft_sub_rects = []

        for i, (name, desc, icon) in enumerate(sub_options):
            cx = start_x + i * (card_w + gap)
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (232, 227, 214, 210), (0, 0, card_w, card_h), border_radius=12)
            pygame.draw.rect(card, (80, 70, 55, 180), (0, 0, card_w, card_h), width=2, border_radius=12)

            # 图标
            icon_surf = self.font_manager.render_text(icon, "large", (60, 50, 35), 48)
            card.blit(icon_surf, ((card_w - icon_surf.get_width()) // 2, 15))

            # 名称
            name_surf = self.font_manager.render_text(name, "large", (50, 40, 25), 32)
            card.blit(name_surf, ((card_w - name_surf.get_width()) // 2, 75))

            # 分隔
            pygame.draw.line(card, (120, 110, 95, 80), (30, 120), (card_w - 30, 120), 1)

            # 描述（多行）
            desc_lines = desc.split("\n")
            for li, line in enumerate(desc_lines):
                ds = self.font_manager.render_text(line, "small", (100, 90, 75), 16)
                card.blit(ds, ((card_w - ds.get_width()) // 2, 130 + li * 22))

            screen.blit(card, (cx, card_y))
            self.craft_sub_rects.append({
                "rect": pygame.Rect(cx, card_y, card_w, card_h),
                "name": name,
            })

    def draw_content_cave(self, screen):
        """洞府模块内容 - 灵药园与聚灵阵"""
        # 更新洞府状态
        cave_data.update_all()
        
        # 标题和子标签
        title = "洞府 · 清修之地"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))

        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)

        # 子标签：灵药园 / 聚灵阵
        sub_tabs = ["灵药园", "聚灵阵"]
        sub_tab_w = 200
        sub_tab_h = 40
        sub_tab_gap = 20
        sub_tab_total_w = len(sub_tabs) * sub_tab_w + (len(sub_tabs) - 1) * sub_tab_gap
        sub_tab_start_x = (self.screen_width - sub_tab_total_w) // 2
        sub_tab_y = 100
        
        self.cave_buttons = []
        for i, tab_name in enumerate(sub_tabs):
            tab_x = sub_tab_start_x + i * (sub_tab_w + sub_tab_gap)
            tab_rect = pygame.Rect(tab_x, sub_tab_y, sub_tab_w, sub_tab_h)
            self.cave_buttons.append({"rect": tab_rect, "name": tab_name})
            
            # 标签背景
            is_active = (self.cave_sub_tab == tab_name)
            bg_color = (80, 70, 55, 200) if is_active else (120, 110, 95, 150)
            border_color = (50, 40, 25, 220) if is_active else (100, 90, 75, 180)
            
            pygame.draw.rect(screen, bg_color, tab_rect, border_radius=6)
            pygame.draw.rect(screen, border_color, tab_rect, width=2, border_radius=6)
            
            # 标签文字
            tab_text = self.font_manager.render_text(tab_name, "medium", (232, 227, 214), 22)
            screen.blit(tab_text, (tab_x + (sub_tab_w - tab_text.get_width()) // 2,
                                  sub_tab_y + (sub_tab_h - tab_text.get_height()) // 2))
        
        # 根据子标签显示内容
        if self.cave_sub_tab == "灵药园":
            self._draw_herb_garden(screen)
        else:  # 聚灵阵
            self._draw_spirit_array(screen)

    def _draw_herb_garden(self, screen):
        """绘制灵药园界面"""
        y_start = 160
        
        # 灵药园等级信息
        garden = cave_data.player_cave["herb_garden"]
        level_info = cave_data.HERB_GARDEN_LEVELS[garden["level"] - 1]
        next_level_info = cave_data.HERB_GARDEN_LEVELS[garden["level"]] if garden["level"] < len(cave_data.HERB_GARDEN_LEVELS) else None
        
        # 等级显示
        level_text = f"灵药园等级：{level_info['name']} (Lv.{garden['level']})"
        lt = self.font_manager.render_text(level_text, "medium", (50, 40, 25), 24)
        screen.blit(lt, (50, y_start))
        
        # 经验进度
        exp_text = f"经验：{garden['exp']}"
        if next_level_info:
            exp_text += f" / {next_level_info['exp_required']}"
        et = self.font_manager.render_text(exp_text, "small", (80, 70, 55), 18)
        screen.blit(et, (50, y_start + 35))
        
        # 道童状态
        apprentice = cave_data.player_cave["apprentice"]
        if apprentice["active"]:
            remaining = apprentice["end_time"] - time.time()
            if remaining > 0:
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                apprentice_text = f"道童工作中：{hours}小时{minutes}分钟后结束"
            else:
                apprentice_text = "道童工作已结束"
        else:
            apprentice_text = "道童：未雇佣"
        
        at = self.font_manager.render_text(apprentice_text, "small", (30, 140, 80), 18)
        screen.blit(at, (50, y_start + 65))
        
        # 药田网格
        field_w, field_h = 180, 120
        gap = 20
        cols = 3
        fields = garden["fields"]
        
        total_w = cols * field_w + (cols - 1) * gap
        start_x = (self.screen_width - total_w) // 2
        start_y = y_start + 120
        
        for i, field in enumerate(fields):
            row = i // cols
            col = i % cols
            fx = start_x + col * (field_w + gap)
            fy = start_y + row * (field_h + gap)
            field_rect = pygame.Rect(fx, fy, field_w, field_h)
            
            # 药田背景
            field_bg = pygame.Surface((field_w, field_h), pygame.SRCALPHA)
            
            if field["seed"]:
                seed_data = cave_data.HERB_SEEDS[field["seed"]]
                # 根据生长进度显示颜色
                progress = field["growth_progress"]
                if field["harvestable"]:
                    bg_color = (200, 220, 100, 180)  # 可收获
                else:
                    # 渐变：从深绿到浅绿
                    green = 100 + int(progress * 1.2)
                    bg_color = (50, green, 30, 180)
            else:
                bg_color = (180, 170, 160, 180)  # 空药田
            
            pygame.draw.rect(field_bg, bg_color, (0, 0, field_w, field_h), border_radius=8)
            pygame.draw.rect(field_bg, (80, 70, 55, 200), (0, 0, field_w, field_h), width=2, border_radius=8)
            
            # 药田编号
            num_text = f"药田 {i+1}"
            nt = self.font_manager.render_text(num_text, "small", (50, 40, 25), 16)
            field_bg.blit(nt, (10, 8))
            
            # 药田内容
            if field["seed"]:
                seed_data = cave_data.HERB_SEEDS[field["seed"]]
                
                # 灵药名
                seed_name = seed_data["name"]
                sn = self.font_manager.render_text(seed_name, "medium", (30, 30, 30), 20)
                field_bg.blit(sn, ((field_w - sn.get_width()) // 2, 35))
                
                # 生长进度条
                progress = field["growth_progress"]
                bar_w = 140
                bar_h = 12
                bar_x = (field_w - bar_w) // 2
                bar_y = 70
                
                # 进度条背景
                pygame.draw.rect(field_bg, (100, 100, 100, 150), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                # 进度条前景
                fill_w = int(bar_w * progress / 100)
                if progress < 100:
                    bar_color = (100, 200, 100)
                else:
                    bar_color = (255, 200, 50)
                pygame.draw.rect(field_bg, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
                
                # 进度文本
                if field["harvestable"]:
                    status_text = "可收获"
                    status_color = (255, 100, 50)
                else:
                    status_text = f"{progress:.1f}%"
                    status_color = (50, 50, 50)
                
                st = self.font_manager.render_text(status_text, "small", status_color, 14)
                field_bg.blit(st, ((field_w - st.get_width()) // 2, bar_y + bar_h + 5))
            else:
                # 空药田提示
                empty_text = "点击种植"
                et = self.font_manager.render_text(empty_text, "small", (120, 110, 95), 18)
                field_bg.blit(et, ((field_w - et.get_width()) // 2, 50))
            
            screen.blit(field_bg, (fx, fy))
            
            # 记录药田位置用于点击检测
            if i == self.selected_field:
                # 绘制选中框
                pygame.draw.rect(screen, (255, 200, 50, 200), (fx-4, fy-4, field_w+8, field_h+8), width=3, border_radius=10)
        
        # 种子库存（如果选中了药田）
        if self.selected_field is not None and self.selected_field < len(fields):
            self._draw_seed_inventory(screen, start_y + (len(fields) + cols - 1) // cols * (field_h + gap) + 40)
        
        # 道童雇佣按钮
        if not cave_data.player_cave["apprentice"]["active"]:
            hire_btn_w, hire_btn_h = 200, 50
            hire_btn_x = self.screen_width - hire_btn_w - 50
            hire_btn_y = y_start + 20
            
            hire_rect = pygame.Rect(hire_btn_x, hire_btn_y, hire_btn_w, hire_btn_h)
            self.cave_buttons.append({"rect": hire_rect, "name": "hire_apprentice", "type": "button"})
            
            # 按钮背景
            pygame.draw.rect(screen, (60, 140, 80, 200), hire_rect, border_radius=8)
            pygame.draw.rect(screen, (30, 100, 60, 220), hire_rect, width=2, border_radius=8)
            
            # 按钮文字
            hire_text = "雇佣道童 (看广告)"
            ht = self.font_manager.render_text(hire_text, "medium", (232, 227, 214), 20)
            screen.blit(ht, (hire_btn_x + (hire_btn_w - ht.get_width()) // 2,
                           hire_btn_y + (hire_btn_h - ht.get_height()) // 2))

    def _draw_seed_inventory(self, screen, y_start):
        """绘制种子库存"""
        seeds = cave_data.player_cave["herb_garden"]["seeds_inventory"]
        
        if not seeds:
            # 没有种子
            no_seeds = self.font_manager.render_text("没有种子，可在宗门贡献堂兑换", "small", (140, 130, 110), 18)
            screen.blit(no_seeds, (50, y_start))
            return
        
        # 种子列表标题
        title = "选择种子："
        tt = self.font_manager.render_text(title, "medium", (50, 40, 25), 22)
        screen.blit(tt, (50, y_start))
        
        # 种子列表
        seed_w, seed_h = 180, 80
        gap = 15
        start_x = 50
        start_y = y_start + 40
        
        for i, (seed_name, quantity) in enumerate(seeds.items()):
            if seed_name not in cave_data.HERB_SEEDS:
                continue
                
            seed_data = cave_data.HERB_SEEDS[seed_name]
            sx = start_x + i * (seed_w + gap)
            sy = start_y
            
            seed_rect = pygame.Rect(sx, sy, seed_w, seed_h)
            self.cave_buttons.append({"rect": seed_rect, "name": f"seed_{seed_name}", "type": "seed"})
            
            # 种子卡片背景
            is_selected = (self.selected_seed == seed_name)
            bg_color = seed_data["color"] + (180,) if is_selected else seed_data["color"] + (120,)
            border_color = (255, 255, 200, 220) if is_selected else (80, 70, 55, 180)
            
            seed_card = pygame.Surface((seed_w, seed_h), pygame.SRCALPHA)
            pygame.draw.rect(seed_card, bg_color, (0, 0, seed_w, seed_h), border_radius=6)
            pygame.draw.rect(seed_card, border_color, (0, 0, seed_w, seed_h), width=2, border_radius=6)
            
            # 种子名称
            name_text = seed_data["name"]
            nt = self.font_manager.render_text(name_text, "small", (30, 30, 30), 18)
            seed_card.blit(nt, ((seed_w - nt.get_width()) // 2, 10))
            
            # 种子数量
            qty_text = f"数量：{quantity}"
            qt = self.font_manager.render_text(qty_text, "small", (60, 60, 60), 16)
            seed_card.blit(qt, ((seed_w - qt.get_width()) // 2, 35))
            
            # 生长时间
            hours = seed_data["growth_time"] // 3600
            time_text = f"生长：{hours}小时"
            tt = self.font_manager.render_text(time_text, "small", (80, 80, 80), 14)
            seed_card.blit(tt, ((seed_w - tt.get_width()) // 2, 55))
            
            screen.blit(seed_card, (sx, sy))
        
        # 种植按钮（如果选中了种子）
        if self.selected_seed and self.selected_field is not None:
            plant_btn_w, plant_btn_h = 150, 50
            plant_btn_x = self.screen_width - plant_btn_w - 50
            plant_btn_y = y_start + 20
            
            plant_rect = pygame.Rect(plant_btn_x, plant_btn_y, plant_btn_w, plant_btn_h)
            self.cave_buttons.append({"rect": plant_rect, "name": "plant_seed", "type": "button"})
            
            # 按钮背景
            pygame.draw.rect(screen, (60, 140, 80, 200), plant_rect, border_radius=8)
            pygame.draw.rect(screen, (30, 100, 60, 220), plant_rect, width=2, border_radius=8)
            
            # 按钮文字
            plant_text = "种植"
            pt = self.font_manager.render_text(plant_text, "medium", (232, 227, 214), 22)
            screen.blit(pt, (plant_btn_x + (plant_btn_w - pt.get_width()) // 2,
                           plant_btn_y + (plant_btn_h - pt.get_height()) // 2))

    def _draw_spirit_array(self, screen):
        """绘制聚灵阵界面"""
        y_start = 160
        
        # 聚灵阵信息
        array = cave_data.player_cave["spirit_array"]
        current_level = array["level"]
        
        # 标题
        if current_level == 0:
            title_text = "聚灵阵：未建造"
        else:
            level_info = cave_data.SPIRIT_ARRAY_LEVELS[current_level - 1]
            title_text = f"聚灵阵：{level_info['name']} (Lv.{current_level})"
        
        tt = self.font_manager.render_text(title_text, "medium", (50, 40, 25), 26)
        screen.blit(tt, (50, y_start))
        
        # 修炼加成
        boost = cave_data.get_cultivation_boost()
        boost_text = f"修炼加成：+{boost*100:.1f}%"
        bt = self.font_manager.render_text(boost_text, "small", (30, 140, 80), 22)
        screen.blit(bt, (50, y_start + 40))
        
        # 材料收集进度
        materials = array["materials_collected"]
        y_materials = y_start + 90
        
        if materials:
            materials_title = self.font_manager.render_text("已收集材料：", "small", (50, 40, 25), 20)
            screen.blit(materials_title, (50, y_materials))
            
            for i, (material, qty) in enumerate(materials.items()):
                mat_text = f"{material}：{qty}"
                mt = self.font_manager.render_text(mat_text, "small", (80, 70, 55), 18)
                screen.blit(mt, (70, y_materials + 30 + i * 25))
        else:
            no_mats = self.font_manager.render_text("尚未收集到材料", "small", (140, 130, 110), 18)
            screen.blit(no_mats, (50, y_materials))
        
        # 升级信息
        if current_level < len(cave_data.SPIRIT_ARRAY_LEVELS):
            next_level_info = cave_data.SPIRIT_ARRAY_LEVELS[current_level]
            y_upgrade = y_materials + 150
            
            upgrade_title = self.font_manager.render_text("升级所需材料：", "medium", (50, 40, 25), 22)
            screen.blit(upgrade_title, (50, y_upgrade))
            
            for i, (material, required) in enumerate(next_level_info["materials_required"].items()):
                has_qty = materials.get(material, 0)
                color = (30, 140, 80) if has_qty >= required else (200, 60, 30)
                req_text = f"{material}：{has_qty}/{required}"
                rt = self.font_manager.render_text(req_text, "small", color, 18)
                screen.blit(rt, (70, y_upgrade + 35 + i * 25))
            
            # 升级按钮
            can_upgrade = all(materials.get(m, 0) >= r for m, r in next_level_info["materials_required"].items())
            upgrade_btn_w, upgrade_btn_h = 200, 50
            upgrade_btn_x = self.screen_width - upgrade_btn_w - 50
            upgrade_btn_y = y_upgrade
            
            upgrade_rect = pygame.Rect(upgrade_btn_x, upgrade_btn_y, upgrade_btn_w, upgrade_btn_h)
            self.cave_buttons.append({"rect": upgrade_rect, "name": "upgrade_array", "type": "button"})
            
            # 按钮背景
            btn_color = (60, 140, 80, 200) if can_upgrade else (140, 130, 110, 150)
            border_color = (30, 100, 60, 220) if can_upgrade else (100, 90, 75, 180)
            
            pygame.draw.rect(screen, btn_color, upgrade_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, upgrade_rect, width=2, border_radius=8)
            
            # 按钮文字
            upgrade_text = "升级聚灵阵"
            ut = self.font_manager.render_text(upgrade_text, "medium", (232, 227, 214), 22)
            screen.blit(ut, (upgrade_btn_x + (upgrade_btn_w - ut.get_width()) // 2,
                           upgrade_btn_y + (upgrade_btn_h - ut.get_height()) // 2))
        
        # 材料来源提示
        hint_y = self.screen_height - 100
        hint_text = "材料来源：锁妖塔掉落"
        ht = self.font_manager.render_text(hint_text, "small", (140, 130, 110), 18)
        screen.blit(ht, ((self.screen_width - ht.get_width()) // 2, hint_y))

    def draw_content_treasure(self, screen):
        """藏宝阁模块内容 - 九层楼阁，四大子模块"""
        import realm_data as rd
        player_realm = rd.player["realm_index"]

        # 标题
        title = "藏宝阁 · 仙家珍藏"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))

        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)

        # ===== 楼层选择器 =====
        floor_y = 95
        floor_w, floor_h = 60, 32
        floor_gap = 6
        total_floor_w = 9 * floor_w + 8 * floor_gap
        floor_start_x = (self.screen_width - total_floor_w) // 2

        realm_short = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]

        self.treasure_floor_rects = []
        for i in range(9):
            fx = floor_start_x + i * (floor_w + floor_gap)
            fr = pygame.Rect(fx, floor_y, floor_w, floor_h)
            self.treasure_floor_rects.append(fr)

            locked = player_realm < i
            is_current = (self.treasure_current_floor == i)

            if is_current:
                bg = (80, 70, 55, 220)
                border = (200, 160, 80, 255)
            elif locked:
                bg = (60, 55, 50, 120)
                border = (80, 75, 70, 100)
            else:
                bg = (100, 90, 75, 150)
                border = (120, 110, 95, 180)

            pygame.draw.rect(screen, bg, fr, border_radius=4)
            pygame.draw.rect(screen, border, fr, width=1, border_radius=4)

            label = "🔒" if locked else realm_short[i]
            if locked:
                ls = self.font_manager.render_text("🔒", "small", (120, 110, 100), 14)
            else:
                ls = self.font_manager.render_text(label, "small",
                    (232, 227, 214) if is_current else (180, 170, 150), 16)
            screen.blit(ls, (fx + (floor_w - ls.get_width()) // 2,
                            floor_y + (floor_h - ls.get_height()) // 2))

        # ===== 子标签 =====
        sub_tabs = ["藏经阁", "法宝库", "丹药房", "材料仓"]
        sub_tab_w = 160
        sub_tab_h = 36
        sub_tab_gap = 15
        sub_tab_total_w = len(sub_tabs) * sub_tab_w + (len(sub_tabs) - 1) * sub_tab_gap
        sub_tab_start_x = (self.screen_width - sub_tab_total_w) // 2
        sub_tab_y = 140

        self.treasure_sub_rects = []
        for i, tab_name in enumerate(sub_tabs):
            tx = sub_tab_start_x + i * (sub_tab_w + sub_tab_gap)
            tr = pygame.Rect(tx, sub_tab_y, sub_tab_w, sub_tab_h)
            self.treasure_sub_rects.append({"rect": tr, "name": tab_name})

            is_active = (self.treasure_sub_tab == tab_name)
            bg_color = (80, 70, 55, 200) if is_active else (120, 110, 95, 150)
            border_color = (50, 40, 25, 220) if is_active else (100, 90, 75, 180)

            pygame.draw.rect(screen, bg_color, tr, border_radius=6)
            pygame.draw.rect(screen, border_color, tr, width=2, border_radius=6)

            tab_text = self.font_manager.render_text(tab_name, "medium", (232, 227, 214), 22)
            screen.blit(tab_text, (tx + (sub_tab_w - tab_text.get_width()) // 2,
                                  sub_tab_y + (sub_tab_h - tab_text.get_height()) // 2))

        # ===== 根据子标签绘制内容 =====
        if self.treasure_sub_tab == "藏经阁":
            self._draw_treasure_gongfa(screen)
        elif self.treasure_sub_tab == "法宝库":
            self._draw_treasure_equipment(screen)
        elif self.treasure_sub_tab == "丹药房":
            self._draw_treasure_pills(screen)
        else:
            self._draw_treasure_materials(screen)

    def _buy_treasure_item(self, btn):
        """尝试购买藏宝阁商品"""
        if self.ling_shi_wallet is None:
            self.treasure_toast = "灵石系统未初始化"
            self.treasure_toast_timer = 90
            return

        price = btn["price"]
        if not self.ling_shi_wallet.can_afford(price):
            self.treasure_toast = "灵石不足！"
            self.treasure_toast_timer = 90
            return

        self.ling_shi_wallet.spend(price)
        self.ling_shi_amount = self.ling_shi_wallet.amount

        # 将物品添加到玩家背包
        btn_type = btn["type"]
        if btn_type == "gongfa":
            gid = btn["gid"]
            if gid not in gongfa_data.player_gongfa["learned"]:
                gongfa_data.player_gongfa["learned"].append(gid)
                self.treasure_toast = f"购买成功！获得功法「{btn['gongfa']['name']}」"
            else:
                self.treasure_toast = "你已学会此功法！"
        elif btn_type == "equipment":
            equip = btn["equip"]
            equip_id = equip["id"]
            treasure_data.player_treasure["inventory"]["equipment"].append(equip_id)
            self.inv_items.append({
                "id": equip_id, "name": equip["name"],
                "type": "装备", "quality": equip["quality"],
            })
            self.treasure_toast = f"购买成功！获得法宝「{equip['name']}」"
        elif btn_type == "pill":
            pill = btn["pill"]
            pill_id = pill["id"]
            treasure_data.player_treasure["inventory"]["pills"].append(pill_id)
            self.inv_items.append({
                "id": pill_id, "name": pill["name"],
                "type": "丹药", "quality": pill["quality"],
            })
            self.treasure_toast = f"购买成功！获得丹药「{pill['name']}」"
        elif btn_type == "material":
            mat = btn["material"]
            mat_id = mat["id"]
            treasure_data.player_treasure["inventory"]["materials"].append(mat_id)
            self.inv_items.append({
                "id": mat_id, "name": mat["name"],
                "type": "材料", "quality": mat["quality"],
            })
            self.treasure_toast = f"购买成功！获得材料「{mat['name']}」"

        self.treasure_toast_timer = 90
        self.treasure_selected_item = None
        self.treasure_selected_type = None

    def _draw_treasure_info_panel(self, screen, btn):
        """绘制藏宝阁物品的信息面板（含购买按钮）"""
        panel_w = 250
        panel_h = 200
        # 面板出现在物品卡片右边
        btn_rect = btn["rect"]
        panel_x = btn_rect.right + 12
        panel_y = btn_rect.top
        if panel_x + panel_w > self.screen_width:
            panel_x = btn_rect.left - panel_w - 12

        canvas = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(canvas, (40, 35, 25, 240), (0, 0, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(canvas, (200, 160, 80, 220), (0, 0, panel_w, panel_h), width=2, border_radius=10)

        y = 12
        btn_type = btn["type"]

        if btn_type == "gongfa":
            gongfa = btn["gongfa"]
            items = [
                f"名称: {gongfa['name']}",
                f"类型: {gongfa.get('type', '未知')}",
                f"品质: {gongfa.get('quality', '未知')}",
                f"属性: {gongfa.get('element', '无')}",
                f"境界: {gongfa.get('realm_min', '无')}",
                f"价格: {btn['price']} 灵石",
            ]
        elif btn_type == "equipment":
            eq = btn["equip"]
            items = [
                f"名称: {eq['name']}",
                f"类型: {eq.get('type', '未知')}",
                f"品质: {eq.get('quality', '未知')}",
                f"属性: {eq.get('desc', '无')}",
                f"价格: {btn['price']} 灵石",
            ]
        elif btn_type == "pill":
            pill = btn["pill"]
            items = [
                f"名称: {pill['name']}",
                f"品质: {pill.get('quality', '未知')}",
                f"效果: {pill.get('desc', '无')}",
                f"价格: {btn['price']} 灵石",
            ]
        else:
            mat = btn["material"]
            items = [
                f"名称: {mat['name']}",
                f"品质: {mat.get('quality', '未知')}",
                f"描述: {mat.get('desc', '无')}",
                f"价格: {btn['price']} 灵石",
            ]

        for item in items:
            ts = self.font_manager.render_text(item, "small", (220, 210, 180), 16)
            canvas.blit(ts, (14, y))
            y += 22

        y += 10
        # 购买按钮
        buy_btn_w = 160
        buy_btn_h = 38
        buy_x = (panel_w - buy_btn_w) // 2
        buy_rect_rel = pygame.Rect(buy_x, y, buy_btn_w, buy_btn_h)
        pygame.draw.rect(canvas, (60, 100, 40, 220), buy_rect_rel, border_radius=8)
        pygame.draw.rect(canvas, (100, 200, 60, 255), buy_rect_rel, width=2, border_radius=8)
        buy_text = self.font_manager.render_text("购买", "medium", (232, 227, 214), 22)
        canvas.blit(buy_text, (buy_x + (buy_btn_w - buy_text.get_width()) // 2,
                               y + (buy_btn_h - buy_text.get_height()) // 2))

        screen.blit(canvas, (panel_x, panel_y))

        # 存储购买按钮的屏幕坐标系rect
        self.treasure_buy_rect = pygame.Rect(panel_x + buy_x, panel_y + y, buy_btn_w, buy_btn_h)

    def _draw_treasure_gongfa(self, screen):
        """绘制藏经阁 - 功法商品"""
        floor = self.treasure_current_floor
        goods = treasure_data.get_floor_goods(floor)
        gongfa_list = goods["gongfa"]

        # 标题
        realm_short = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]
        sub_title = f"藏经阁 · {realm_short[floor]}期功法"
        st = self.font_manager.render_text(sub_title, "medium", (180, 160, 130), 24)
        screen.blit(st, (50, 195))

        # 提示
        hint = "仅出售灵技与内经，品质以白绿为主，小概率蓝色"
        ht = self.font_manager.render_text(hint, "small", (120, 110, 100), 16)
        screen.blit(ht, (50, 225))

        if not gongfa_list:
            no_text = "该层暂无功法出售"
            nt = self.font_manager.render_text(no_text, "small", (140, 130, 110), 20)
            screen.blit(nt, ((self.screen_width - nt.get_width()) // 2, 300))
            return

        # 商品格子
        self.treasure_buttons = []
        cell_w, cell_h = 180, 130
        cols = 5
        gap = 15
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = (self.screen_width - total_w) // 2
        start_y = 260

        for i, (gid, price) in enumerate(gongfa_list):
            col = i % cols
            row = i // cols
            cx = start_x + col * (cell_w + gap)
            cy = start_y + row * (cell_h + gap)

            gongfa = treasure_data.get_gongfa_by_id(gid)

            if gongfa is None:
                continue

            cell_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            self.treasure_buttons.append({
                "rect": cell_rect, "type": "gongfa",
                "gid": gid, "price": price, "gongfa": gongfa
            })

            # 背景
            is_selected = (self.treasure_selected_item == gid and self.treasure_selected_type == "gongfa")
            bg_alpha = 220 if is_selected else 160
            border_color = (200, 160, 80, 255) if is_selected else (80, 70, 55, 150)

            cell = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            pygame.draw.rect(cell, (232, 227, 214, bg_alpha), (0, 0, cell_w, cell_h), border_radius=6)
            pygame.draw.rect(cell, border_color, (0, 0, cell_w, cell_h), width=1, border_radius=6)

            # 品质颜色
            q_color = treasure_data.QUALITY_DISPLAY_COLORS.get(gongfa["quality"], (200, 200, 200))

            # 功法名称
            name_text = gongfa["name"]
            ns = self.font_manager.render_text(name_text, "small", q_color, 18)
            cell.blit(ns, ((cell_w - ns.get_width()) // 2, 10))

            # 类型标签
            type_label = f"[{gongfa['type']}]"
            tl = self.font_manager.render_text(type_label, "small", (100, 90, 75), 14)
            cell.blit(tl, ((cell_w - tl.get_width()) // 2, 35))

            # 分隔线
            pygame.draw.line(cell, (150, 140, 120, 80), (15, 58), (cell_w - 15, 58), 1)

            # 描述
            desc = gongfa.get("desc", "")
            ds = self.font_manager.render_text(desc, "small", (80, 70, 55), 14)
            cell.blit(ds, ((cell_w - ds.get_width()) // 2, 65))

            # 价格
            price_text = f"灵石 ×{price}"
            ps = self.font_manager.render_text(price_text, "small", (200, 160, 40), 16)
            cell.blit(ps, ((cell_w - ps.get_width()) // 2, 90))

            screen.blit(cell, (cx, cy))

        # 显示选中物品的信息面板
        if self.treasure_selected_type == "gongfa" and self.treasure_selected_item is not None:
            for btn in self.treasure_buttons:
                if btn["type"] == "gongfa" and btn["gid"] == self.treasure_selected_item:
                    self._draw_treasure_info_panel(screen, btn)
                    break

    def _draw_treasure_equipment(self, screen):
        """绘制法宝库 - 装备商品"""
        floor = self.treasure_current_floor
        goods = treasure_data.get_floor_goods(floor)
        equip_list = goods["equipment"]

        realm_short = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]
        sub_title = f"法宝库 · {realm_short[floor]}期装备"
        st = self.font_manager.render_text(sub_title, "medium", (180, 160, 130), 24)
        screen.blit(st, (50, 195))

        hint = "品质以白绿为主，小概率蓝色"
        ht = self.font_manager.render_text(hint, "small", (120, 110, 100), 16)
        screen.blit(ht, (50, 225))

        if not equip_list:
            no_text = "该层暂无装备出售"
            nt = self.font_manager.render_text(no_text, "small", (140, 130, 110), 20)
            screen.blit(nt, ((self.screen_width - nt.get_width()) // 2, 300))
            return

        self.treasure_buttons = []
        cell_w, cell_h = 180, 130
        cols = 5
        gap = 15
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = (self.screen_width - total_w) // 2
        start_y = 260

        for i, (equip, price) in enumerate(equip_list):
            col = i % cols
            row = i // cols
            cx = start_x + col * (cell_w + gap)
            cy = start_y + row * (cell_h + gap)

            cell_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            self.treasure_buttons.append({
                "rect": cell_rect, "type": "equipment",
                "equip": equip, "price": price
            })

            is_selected = (self.treasure_selected_item == equip["id"] and self.treasure_selected_type == "equipment")
            bg_alpha = 220 if is_selected else 160
            border_color = (200, 160, 80, 255) if is_selected else (80, 70, 55, 150)

            cell = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            pygame.draw.rect(cell, (232, 227, 214, bg_alpha), (0, 0, cell_w, cell_h), border_radius=6)
            pygame.draw.rect(cell, border_color, (0, 0, cell_w, cell_h), width=1, border_radius=6)

            q_color = treasure_data.QUALITY_DISPLAY_COLORS.get(equip["quality"], (200, 200, 200))

            # 装备名称
            ns = self.font_manager.render_text(equip["name"], "small", q_color, 18)
            cell.blit(ns, ((cell_w - ns.get_width()) // 2, 10))

            # 类型
            type_label = f"[{equip['type']}]"
            tl = self.font_manager.render_text(type_label, "small", (100, 90, 75), 14)
            cell.blit(tl, ((cell_w - tl.get_width()) // 2, 35))

            pygame.draw.line(cell, (150, 140, 120, 80), (15, 58), (cell_w - 15, 58), 1)

            # 属性描述
            ds = self.font_manager.render_text(equip["desc"], "small", (80, 70, 55), 14)
            cell.blit(ds, ((cell_w - ds.get_width()) // 2, 65))

            # 价格
            price_text = f"灵石 ×{price}"
            ps = self.font_manager.render_text(price_text, "small", (200, 160, 40), 16)
            cell.blit(ps, ((cell_w - ps.get_width()) // 2, 90))

            screen.blit(cell, (cx, cy))

        # 显示选中物品的信息面板
        if self.treasure_selected_type == "equipment" and self.treasure_selected_item is not None:
            for btn in self.treasure_buttons:
                if btn["type"] == "equipment" and btn["equip"]["id"] == self.treasure_selected_item:
                    self._draw_treasure_info_panel(screen, btn)
                    break

    def _draw_treasure_pills(self, screen):
        """绘制丹药房 - 丹药商品"""
        floor = self.treasure_current_floor
        goods = treasure_data.get_floor_goods(floor)
        pill_list = goods["pills"]

        realm_short = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]
        sub_title = f"丹药房 · {realm_short[floor]}期丹药"
        st = self.font_manager.render_text(sub_title, "medium", (180, 160, 130), 24)
        screen.blit(st, (50, 195))

        if not pill_list:
            no_text = "该层暂无丹药出售"
            nt = self.font_manager.render_text(no_text, "small", (140, 130, 110), 20)
            screen.blit(nt, ((self.screen_width - nt.get_width()) // 2, 300))
            return

        self.treasure_buttons = []
        cell_w, cell_h = 180, 130
        cols = 5
        gap = 15
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = (self.screen_width - total_w) // 2
        start_y = 260

        for i, (pill, price) in enumerate(pill_list):
            col = i % cols
            row = i // cols
            cx = start_x + col * (cell_w + gap)
            cy = start_y + row * (cell_h + gap)

            cell_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            self.treasure_buttons.append({
                "rect": cell_rect, "type": "pill",
                "pill": pill, "price": price
            })

            is_selected = (self.treasure_selected_item == pill["id"] and self.treasure_selected_type == "pill")
            bg_alpha = 220 if is_selected else 160
            border_color = (200, 160, 80, 255) if is_selected else (80, 70, 55, 150)

            cell = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            pygame.draw.rect(cell, (232, 227, 214, bg_alpha), (0, 0, cell_w, cell_h), border_radius=6)
            pygame.draw.rect(cell, border_color, (0, 0, cell_w, cell_h), width=1, border_radius=6)

            q_color = treasure_data.QUALITY_DISPLAY_COLORS.get(pill["quality"], (200, 200, 200))

            # 丹药名称
            ns = self.font_manager.render_text(pill["name"], "small", q_color, 18)
            cell.blit(ns, ((cell_w - ns.get_width()) // 2, 10))

            # 品质标签
            ql = self.font_manager.render_text(f"[{pill['quality']}]", "small", (100, 90, 75), 14)
            cell.blit(ql, ((cell_w - ql.get_width()) // 2, 35))

            pygame.draw.line(cell, (150, 140, 120, 80), (15, 58), (cell_w - 15, 58), 1)

            # 效果描述
            ds = self.font_manager.render_text(pill["desc"], "small", (80, 70, 55), 14)
            cell.blit(ds, ((cell_w - ds.get_width()) // 2, 65))

            # 价格
            price_text = f"灵石 ×{price}"
            ps = self.font_manager.render_text(price_text, "small", (200, 160, 40), 16)
            cell.blit(ps, ((cell_w - ps.get_width()) // 2, 90))

            screen.blit(cell, (cx, cy))

        # 显示选中物品的信息面板
        if self.treasure_selected_type == "pill" and self.treasure_selected_item is not None:
            for btn in self.treasure_buttons:
                if btn["type"] == "pill" and btn["pill"]["id"] == self.treasure_selected_item:
                    self._draw_treasure_info_panel(screen, btn)
                    break

    def _draw_treasure_materials(self, screen):
        """绘制材料仓 - 材料商品"""
        floor = self.treasure_current_floor
        goods = treasure_data.get_floor_goods(floor)
        mat_list = goods["materials"]

        realm_short = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]
        sub_title = f"材料仓 · {realm_short[floor]}期材料"
        st = self.font_manager.render_text(sub_title, "medium", (180, 160, 130), 24)
        screen.blit(st, (50, 195))

        if not mat_list:
            no_text = "该层暂无材料出售"
            nt = self.font_manager.render_text(no_text, "small", (140, 130, 110), 20)
            screen.blit(nt, ((self.screen_width - nt.get_width()) // 2, 300))
            return

        self.treasure_buttons = []
        cell_w, cell_h = 180, 130
        cols = 5
        gap = 15
        total_w = cols * cell_w + (cols - 1) * gap
        start_x = (self.screen_width - total_w) // 2
        start_y = 260

        for i, (mat, price) in enumerate(mat_list):
            col = i % cols
            row = i // cols
            cx = start_x + col * (cell_w + gap)
            cy = start_y + row * (cell_h + gap)

            cell_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            self.treasure_buttons.append({
                "rect": cell_rect, "type": "material",
                "material": mat, "price": price
            })

            is_selected = (self.treasure_selected_item == mat["id"] and self.treasure_selected_type == "material")
            bg_alpha = 220 if is_selected else 160
            border_color = (200, 160, 80, 255) if is_selected else (80, 70, 55, 150)

            cell = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            pygame.draw.rect(cell, (232, 227, 214, bg_alpha), (0, 0, cell_w, cell_h), border_radius=6)
            pygame.draw.rect(cell, border_color, (0, 0, cell_w, cell_h), width=1, border_radius=6)

            q_color = treasure_data.QUALITY_DISPLAY_COLORS.get(mat["quality"], (200, 200, 200))

            # 材料名称
            ns = self.font_manager.render_text(mat["name"], "small", q_color, 18)
            cell.blit(ns, ((cell_w - ns.get_width()) // 2, 10))

            # 品质标签
            ql = self.font_manager.render_text(f"[{mat['quality']}]", "small", (100, 90, 75), 14)
            cell.blit(ql, ((cell_w - ql.get_width()) // 2, 35))

            pygame.draw.line(cell, (150, 140, 120, 80), (15, 58), (cell_w - 15, 58), 1)

            # 描述
            ds = self.font_manager.render_text(mat["desc"], "small", (80, 70, 55), 14)
            cell.blit(ds, ((cell_w - ds.get_width()) // 2, 65))

            # 价格
            price_text = f"灵石 ×{price}"
            ps = self.font_manager.render_text(price_text, "small", (200, 160, 40), 16)
            cell.blit(ps, ((cell_w - ps.get_width()) // 2, 90))

            screen.blit(cell, (cx, cy))

        # 显示选中物品的信息面板
        if self.treasure_selected_type == "material" and self.treasure_selected_item is not None:
            for btn in self.treasure_buttons:
                if btn["type"] == "material" and btn["material"]["id"] == self.treasure_selected_item:
                    self._draw_treasure_info_panel(screen, btn)
                    break

    def draw_content_battle(self, screen):
        """战斗模块内容 - 历练之路/锁妖塔/远古战场三个子选项"""
        title = "战斗 · 斩妖除魔"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))

        lx = (self.screen_width - 300) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 300, 72), 1)

        # 如果正在战斗中，显示返回战斗按钮
        if hasattr(self, 'in_combat') and self.in_combat:
            sub_text = "战斗中 - 按 ESC 返回"
            st = self.font_manager.render_text(sub_text, "medium", (200, 50, 50), 24)
            screen.blit(st, ((self.screen_width - st.get_width()) // 2, 100))
            
            # 返回战斗按钮
            return_btn_w = 200
            return_btn_h = 60
            return_btn_x = (self.screen_width - return_btn_w) // 2
            return_btn_y = 150
            return_btn_rect = pygame.Rect(return_btn_x, return_btn_y, return_btn_w, return_btn_h)
            
            # 按钮背景
            pygame.draw.rect(screen, (200, 50, 50, 180), return_btn_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 100, 100, 220), return_btn_rect, width=2, border_radius=10)
            
            # 按钮文字
            return_text = self.font_manager.render_text("返回战斗", "large", (255, 255, 200), 32)
            screen.blit(return_text, (return_btn_x + (return_btn_w - return_text.get_width()) // 2, 
                                     return_btn_y + (return_btn_h - return_text.get_height()) // 2))
            
            # 存储按钮矩形用于点击检测
            self.return_to_combat_rect = return_btn_rect
            return
            
        sub_text = "选择征战之地"
        st = self.font_manager.render_text(sub_text, "medium", (100, 90, 75), 24)
        screen.blit(st, ((self.screen_width - st.get_width()) // 2, 100))

        sub_options = [
            ("历练之路", "步步为营，斩妖除魔\n击败Boss解锁新地图", "历"),
            ("锁妖塔", "逐层攀登，挑战极限\n层数越高奖励越丰厚", "塔"),
            ("远古战场", "与远古英灵交锋\n获取稀世珍宝", "古"),
        ]

        card_w, card_h = 300, 200
        gap = 30
        total_w = card_w * 3 + gap * 2
        start_x = (self.screen_width - total_w) // 2
        card_y = 160

        self.battle_sub_rects = []

        for i, (name, desc, icon) in enumerate(sub_options):
            cx = start_x + i * (card_w + gap)
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (232, 227, 214, 210), (0, 0, card_w, card_h), border_radius=12)
            pygame.draw.rect(card, (80, 70, 55, 180), (0, 0, card_w, card_h), width=2, border_radius=12)

            icon_surf = self.font_manager.render_text(icon, "large", (60, 50, 35), 48)
            card.blit(icon_surf, ((card_w - icon_surf.get_width()) // 2, 15))

            name_surf = self.font_manager.render_text(name, "large", (50, 40, 25), 32)
            card.blit(name_surf, ((card_w - name_surf.get_width()) // 2, 75))

            pygame.draw.line(card, (120, 110, 95, 80), (30, 120), (card_w - 30, 120), 1)

            desc_lines = desc.split("\n")
            for li, line in enumerate(desc_lines):
                ds = self.font_manager.render_text(line, "small", (100, 90, 75), 16)
                card.blit(ds, ((card_w - ds.get_width()) // 2, 132 + li * 24))

            screen.blit(card, (cx, card_y))
            self.battle_sub_rects.append({
                "rect": pygame.Rect(cx, card_y, card_w, card_h),
                "name": name,
            })

    def draw_tab_bar(self, screen):
        """绘制底部标签栏"""
        bar_h = self.bar_height

        for tab in self.tabs:
            r = tab["rect"]
            is_active = self.active_tab == tab["id"]
            is_hovered = self.hovered_tab == tab["id"]

            # 标签底色
            tab_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            if is_active:
                pygame.draw.rect(tab_surf, (80, 65, 45, 220), (0, 0, r.width, r.height),
                                 border_top_left_radius=6, border_top_right_radius=6)
                # 激活指示条
                pygame.draw.line(tab_surf, (180, 160, 100, 220), (15, 4), (r.width - 15, 4), 3)
            elif is_hovered:
                pygame.draw.rect(tab_surf, (65, 52, 36, 160), (0, 0, r.width, r.height),
                                 border_top_left_radius=6, border_top_right_radius=6)
            else:
                pygame.draw.rect(tab_surf, (50, 40, 28, 140), (0, 0, r.width, r.height),
                                 border_top_left_radius=6, border_top_right_radius=6)

            # 标签名
            text_color = (220, 210, 190) if is_active else (160, 150, 130)
            name_surf = self.font_manager.render_text(tab["name"], "large", text_color, 28)
            tab_surf.blit(name_surf,
                         ((r.width - name_surf.get_width()) // 2,
                          (r.height - name_surf.get_height()) // 2))

            screen.blit(tab_surf, (r.x, r.y))

    def draw_settings_button(self, screen):
        """绘制设置按钮（右上角）"""
        r = self.settings_button_rect
        
        # 按钮背景
        if self.settings_button_hovered:
            pygame.draw.rect(screen, (180, 160, 100, 220), r, border_radius=6)
            pygame.draw.rect(screen, (200, 180, 120, 240), r, width=2, border_radius=6)
            text_color = (40, 30, 18)
        else:
            pygame.draw.rect(screen, (150, 130, 80, 200), r, border_radius=6)
            pygame.draw.rect(screen, (180, 160, 100, 220), r, width=1, border_radius=6)
            text_color = (40, 30, 18)
        
        # 按钮文字
        text_surf = self.font_manager.render_text("设置", "medium", text_color, 22)
        screen.blit(text_surf, 
                   (r.x + (r.width - text_surf.get_width()) // 2,
                    r.y + (r.height - text_surf.get_height()) // 2))

    def draw_content_alchemy(self, screen):
        """绘制炼丹界面"""
        self.alchemy_buttons = []
        self.alchemy_pill_buttons = []

        cw, ch = self.screen_width, self.content_height
        margin = 30
        panel_w = 500
        right_x = margin + panel_w + 20

        # === 返回按钮 ===
        back_w, back_h = 100, 32
        back_rect = pygame.Rect(margin, 8, back_w, back_h)
        hover_back = back_rect.collidepoint(pygame.mouse.get_pos())
        back_bg = (60, 60, 50) if hover_back else (40, 40, 35)
        back_border = (120, 120, 100) if hover_back else (80, 80, 70)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=4)
        pygame.draw.rect(screen, back_border, back_rect, 1, border_radius=4)
        back_txt = self.font_manager.render_text("« 返回炼制", "small", (200, 190, 150), 15)
        screen.blit(back_txt, (margin + (back_w - back_txt.get_width()) // 2,
                               8 + (back_h - back_txt.get_height()) // 2))
        self.alchemy_buttons.append({"rect": back_rect, "action": "back"})

        # === 左侧：炼制面板 ===
        y = margin + 10

        # 标题
        title = self.font_manager.render_text("丹 房", "title", (220, 200, 120), 32)
        screen.blit(title, (margin + 10, y))
        y += 45

        # 丹师等级和进度条
        level = player_alchemy["level"]
        exp = player_alchemy["exp"]
        exp_max = get_exp_for_level(level) if level < ALCHEMIST_MAX_LEVEL else exp
        if level >= ALCHEMIST_MAX_LEVEL:
            exp = exp_max  # 满级满条

        lv_text = self.font_manager.render_text(
            f"丹师等级: {level} 级", "medium", (200, 180, 100), 20
        )
        screen.blit(lv_text, (margin + 10, y))
        y += 28

        # 经验条
        bar_x, bar_y = margin + 10, y
        bar_w, bar_h = 460, 14
        pygame.draw.rect(screen, (40, 35, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        if exp_max > 0:
            fill_w = int(bar_w * exp / exp_max)
            pygame.draw.rect(screen, (120, 180, 100), (bar_x, bar_y, fill_w, bar_h), border_radius=5)
        if level < ALCHEMIST_MAX_LEVEL:
            exp_text = self.font_manager.render_text(
                f"{exp}/{exp_max}", "small", (180, 180, 160), 13
            )
            screen.blit(exp_text, (bar_x + bar_w + 8, bar_y - 1))
        y = bar_y + bar_h + 15

        # 丹药类型选择
        type_label = self.font_manager.render_text("丹方:", "medium", (200, 180, 100), 18)
        screen.blit(type_label, (margin + 10, y))
        y += 28

        btn_w, btn_h = 78, 32
        for i, ptype in enumerate(PILL_TYPE_ORDER):
            bx = margin + 10 + i * (btn_w + 8)
            by = y
            btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
            hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            selected = (i == self.alchemy_selected_type)

            bg = (60, 80, 40) if selected else ((50, 60, 40) if hover else (35, 35, 30))
            border = (180, 200, 80) if selected else ((120, 140, 80) if hover else (80, 80, 70))
            pygame.draw.rect(screen, bg, btn_rect, border_radius=4)
            pygame.draw.rect(screen, border, btn_rect, 2, border_radius=4)

            txt = self.font_manager.render_text(ptype, "small", (220, 210, 160), 14)
            screen.blit(txt, (bx + (btn_w - txt.get_width()) // 2, by + (btn_h - txt.get_height()) // 2))
            self.alchemy_buttons.append({"rect": btn_rect, "action": "select_type", "index": i})

        y += btn_h + 15

        # 品级选择
        grade_label = self.font_manager.render_text("品级:", "medium", (200, 180, 100), 18)
        screen.blit(grade_label, (margin + 10, y))
        y += 28

        grade_btn_w = 45
        for i in range(9):
            bx = margin + 10 + i * (grade_btn_w + 4)
            by = y
            btn_rect = pygame.Rect(bx, by, grade_btn_w, btn_h)
            hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            selected = (i == self.alchemy_selected_grade)

            bg = (60, 80, 40) if selected else ((50, 60, 40) if hover else (35, 35, 30))
            border = (180, 200, 80) if selected else ((120, 140, 80) if hover else (80, 80, 70))
            pygame.draw.rect(screen, bg, btn_rect, border_radius=4)
            pygame.draw.rect(screen, border, btn_rect, 2, border_radius=4)

            txt = self.font_manager.render_text(f"{i + 1}品", "small", (220, 210, 160), 13)
            screen.blit(txt, (bx + (grade_btn_w - txt.get_width()) // 2, by + (btn_h - txt.get_height()) // 2))
            self.alchemy_buttons.append({"rect": btn_rect, "action": "select_grade", "index": i})

        y += btn_h + 15

        # 材料信息
        realm_idx = self.alchemy_selected_grade
        mat_info = REALM_MATERIALS[realm_idx]
        material_cnt = player_alchemy["materials"].get(realm_idx, 0)

        material_text = self.font_manager.render_text(
            f"所需材料: {mat_info['name']}（{REALM_NAMES[realm_idx]}） 持有: {material_cnt}",
            "medium", (180, 160, 120), 17
        )
        screen.blit(material_text, (margin + 10, y))
        y += 25

        mat_desc = self.font_manager.render_text(mat_info["desc"], "small", (140, 130, 110), 14)
        screen.blit(mat_desc, (margin + 20, y))
        y += 35

        # 炼制按钮
        craft_btn_w, craft_btn_h = 160, 40
        craft_x = margin + (panel_w - craft_btn_w) // 2
        craft_btn_rect = pygame.Rect(craft_x, y, craft_btn_w, craft_btn_h)
        hover_craft = craft_btn_rect.collidepoint(pygame.mouse.get_pos())
        can_craft = material_cnt > 0
        bg = (60, 120, 40) if (can_craft and hover_craft) else (40, 80, 30)
        border = (120, 220, 80) if can_craft else (80, 80, 70)
        pygame.draw.rect(screen, bg, craft_btn_rect, border_radius=6)
        pygame.draw.rect(screen, border, craft_btn_rect, 2, border_radius=6)
        craft_txt = self.font_manager.render_text("开 炉 炼 制", "medium", (220, 220, 100), 22)
        screen.blit(craft_txt, (craft_x + (craft_btn_w - craft_txt.get_width()) // 2,
                                 y + (craft_btn_h - craft_txt.get_height()) // 2))
        if can_craft:
            self.alchemy_buttons.append({"rect": craft_btn_rect, "action": "craft"})

        # 炼制结果消息
        if self.alchemy_craft_result_timer > 0:
            self.alchemy_craft_result_timer -= 1
            res_y = y + craft_btn_h + 12
            color = (120, 220, 100) if "成功" in self.alchemy_craft_result else (220, 120, 100)
            res_txt = self.font_manager.render_text(self.alchemy_craft_result, "medium", color, 17)
            screen.blit(res_txt, (margin + 10, res_y))

        # 品质概率预览
        probs_y = y + craft_btn_h + 38
        prob_label = self.font_manager.render_text("品质概率:", "small", (160, 150, 120), 15)
        screen.blit(prob_label, (margin + 10, probs_y))
        probs = get_quality_probs(player_alchemy["level"], self.alchemy_selected_grade + 1)
        for qi, (qname, prob) in enumerate(zip(QUALITIES, probs)):
            qx = margin + 10 + qi * 75
            qc = QUALITY_DISPLAY_COLORS[qname]
            qt = self.font_manager.render_text(f"{qname}:{prob}%", "small", qc, 14)
            screen.blit(qt, (qx, probs_y + 20))

        # === 右侧：丹药背包 ===
        right_y = margin + 10
        inv_title = self.font_manager.render_text(
            f"丹药背包（{len(player_alchemy['pills'])}枚）", "title", (220, 200, 120), 24
        )
        screen.blit(inv_title, (right_x, right_y))
        right_y += 38

        # 丹药列表
        right_w = cw - right_x - margin
        list_height = ch - right_y - margin - 120
        list_rect = pygame.Rect(right_x, right_y, right_w, list_height)
        pygame.draw.rect(screen, (30, 30, 28), list_rect, border_radius=4)
        pygame.draw.rect(screen, (70, 70, 60), list_rect, 1, border_radius=4)

        pills = player_alchemy["pills"]
        pills_per_row = max(1, right_w // 260)
        pill_w = (right_w - 20) // pills_per_row - 8
        pill_h = 52
        row_gap, col_gap = 6, 6

        for pi, pill in enumerate(pills):
            row = pi // pills_per_row
            col = pi % pills_per_row
            px = right_x + 10 + col * (pill_w + col_gap)
            py = right_y + 8 + row * (pill_h + row_gap)

            if py + pill_h > right_y + list_height:
                break  # 超出可视区域

            pill_rect = pygame.Rect(px, py, pill_w, pill_h)
            selected_pill = self.alchemy_selected_pill is not None and pi == self.alchemy_selected_pill
            hover_pill = pill_rect.collidepoint(pygame.mouse.get_pos())

            bg_pill = (55, 55, 45) if selected_pill else ((45, 45, 38) if hover_pill else (33, 33, 30))
            border_pill = (200, 180, 80) if selected_pill else ((100, 100, 80) if hover_pill else (60, 60, 50))
            pygame.draw.rect(screen, bg_pill, pill_rect, border_radius=4)
            pygame.draw.rect(screen, border_pill, pill_rect, 1, border_radius=4)

            qc = QUALITY_DISPLAY_COLORS[pill["quality"]]
            name_txt = self.font_manager.render_text(pill["name"], "small", (220, 210, 180), 15)
            screen.blit(name_txt, (px + 6, py + 4))
            q_txt = self.font_manager.render_text(f"品质: {pill['quality']}", "small", qc, 13)
            screen.blit(q_txt, (px + 6, py + 26))

            self.alchemy_pill_buttons.append({"rect": pill_rect, "index": pi})

        # === 底部：选中丹药详情 ===
        detail_y = right_y + list_height + 12
        detail_h = ch - detail_y - margin
        detail_rect = pygame.Rect(right_x, detail_y, right_w, detail_h)
        pygame.draw.rect(screen, (28, 28, 26), detail_rect, border_radius=4)
        pygame.draw.rect(screen, (70, 70, 60), detail_rect, 1, border_radius=4)

        if self.alchemy_selected_pill is not None and self.alchemy_selected_pill < len(pills):
            pill = pills[self.alchemy_selected_pill]
            qc = QUALITY_DISPLAY_COLORS[pill["quality"]]
            d_y = detail_y + 12

            name_t = self.font_manager.render_text(pill["name"], "medium", qc, 22)
            screen.blit(name_t, (right_x + 16, d_y))
            d_y += 30

            quality_t = self.font_manager.render_text(
                f"品质: {pill['quality']}  |  {PILL_TYPES[pill['type']]['desc_template'].format(value=pill['effect_value'])}",
                "medium", (200, 190, 150), 17
            )
            screen.blit(quality_t, (right_x + 16, d_y))
            d_y += 28

            effect_detail = self.font_manager.render_text(
                pill["desc"], "small", (180, 220, 140), 16
            )
            screen.blit(effect_detail, (right_x + 16, d_y))

            # 服用按钮
            consume_w, consume_h = 100, 36
            consume_x = right_x + right_w - consume_w - 16
            consume_y = detail_y + detail_h - consume_h - 10
            consume_rect = pygame.Rect(consume_x, consume_y, consume_w, consume_h)
            hover_c = consume_rect.collidepoint(pygame.mouse.get_pos())
            bg_c = (80, 60, 30) if hover_c else (55, 40, 20)
            border_c = (200, 140, 60) if hover_c else (140, 100, 50)
            pygame.draw.rect(screen, bg_c, consume_rect, border_radius=5)
            pygame.draw.rect(screen, border_c, consume_rect, 2, border_radius=5)
            c_txt = self.font_manager.render_text("服 用", "medium", (230, 200, 120), 20)
            screen.blit(c_txt, (consume_x + (consume_w - c_txt.get_width()) // 2,
                                 consume_y + (consume_h - c_txt.get_height()) // 2))
            self.alchemy_buttons.append({"rect": consume_rect, "action": "consume"})
        else:
            hint = self.font_manager.render_text("选择一枚丹药查看详情", "small", (120, 120, 110), 16)
            screen.blit(hint, (right_x + (right_w - hint.get_width()) // 2,
                                detail_y + (detail_h - hint.get_height()) // 2))

    # ==================== 炼器模块 ====================

    def draw_content_forge(self, screen):
        """炼器模块入口 - 根据子标签分发"""
        self.forge_buttons = []

        # 锻造师等级显示
        level = player_forge["level"]
        exp = player_forge["exp"]
        exp_max = forge_get_exp(level) if level < FORGER_MAX_LEVEL else exp
        if level >= FORGER_MAX_LEVEL:
            exp = exp_max

        lv_text = self.font_manager.render_text(
            f"锻造师等级: {level} 级", "medium", (200, 160, 80), 18
        )
        screen.blit(lv_text, (self.screen_width - 230, 8))

        if self.forge_sub_tab == "强化":
            self._draw_enhance_panel(screen)
        elif self.forge_sub_tab == "锻造":
            self._draw_forge_craft_panel(screen)
        else:
            self._draw_forge_sub_menu(screen)

    def _draw_forge_sub_menu(self, screen):
        """炼器主界面 - 强化/锻造选择"""
        title = "炼器 · 千锤百炼"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 40)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 25))

        lx = (self.screen_width - 460) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), (lx, 72), (lx + 460, 72), 1)

        sub_text = "选择炼制方向"
        st = self.font_manager.render_text(sub_text, "medium", (100, 90, 75), 24)
        screen.blit(st, ((self.screen_width - st.get_width()) // 2, 100))

        # 返回按钮
        back_w, back_h = 110, 32
        back_rect = pygame.Rect(30, 35, back_w, back_h)
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        bg = (65, 55, 45) if hover else (45, 38, 30)
        bd = (130, 110, 80) if hover else (90, 80, 60)
        pygame.draw.rect(screen, bg, back_rect, border_radius=5)
        pygame.draw.rect(screen, bd, back_rect, 1, border_radius=5)
        bt = self.font_manager.render_text("« 返回炼制", "small", (200, 180, 140), 15)
        screen.blit(bt, (35 + (back_w - bt.get_width()) // 2, 35 + (back_h - bt.get_height()) // 2))
        self.forge_buttons.append({"rect": back_rect, "action": "back"})

        # 两张选择卡片
        options = [
            ("强化", "淬炼神兵 · 突破极限", "以强化材料淬炼装备\n提升装备属性\n不同境界强化上限不同\n强化等级可继承"),
            ("锻造", "熔铸天材 · 打造神兵", "使用锻造材料打造新装备\n品质从白到金\n锻造师等级越高\n越容易出高品质装备"),
        ]

        card_w, card_h = 360, 250
        gap = 50
        total_w = card_w * 2 + gap
        start_x = (self.screen_width - total_w) // 2
        card_y = 160

        for i, (name, subtitle, desc) in enumerate(options):
            cx = start_x + i * (card_w + gap)
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (232, 227, 214, 210), (0, 0, card_w, card_h), border_radius=12)
            pygame.draw.rect(card, (80, 70, 55, 180), (0, 0, card_w, card_h), width=2, border_radius=12)

            # 图标
            icon_char = "锻" if name == "强化" else "铸"
            icon_surf = self.font_manager.render_text(icon_char, "large", (60, 50, 35), 56)
            card.blit(icon_surf, ((card_w - icon_surf.get_width()) // 2, 18))

            name_surf = self.font_manager.render_text(name, "large", (50, 40, 25), 36)
            card.blit(name_surf, ((card_w - name_surf.get_width()) // 2, 80))

            sub_surf = self.font_manager.render_text(subtitle, "small", (100, 90, 75), 14)
            card.blit(sub_surf, ((card_w - sub_surf.get_width()) // 2, 120))

            pygame.draw.line(card, (120, 110, 95, 80), (40, 145), (card_w - 40, 145), 1)

            for li, line in enumerate(desc.split("\n")):
                ds = self.font_manager.render_text(line, "small", (100, 90, 75), 15)
                card.blit(ds, ((card_w - ds.get_width()) // 2, 155 + li * 22))

            screen.blit(card, (cx, card_y))
            self.forge_buttons.append({
                "rect": pygame.Rect(cx, card_y, card_w, card_h),
                "action": "goto_enhance" if name == "强化" else "goto_forge",
            })

    def _draw_enhance_panel(self, screen):
        """强化面板 - 展示装备槽位，点击强化"""
        margin = 30
        y = 40

        # 返回按钮
        back_w, back_h = 100, 32
        back_rect = pygame.Rect(margin, y, back_w, back_h)
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        bg = (65, 55, 45) if hover else (45, 38, 30)
        bd = (130, 110, 80) if hover else (90, 80, 60)
        pygame.draw.rect(screen, bg, back_rect, border_radius=4)
        pygame.draw.rect(screen, bd, back_rect, 1, border_radius=4)
        bt = self.font_manager.render_text("« 返回", "small", (200, 180, 140), 14)
        screen.blit(bt, (margin + (back_w - bt.get_width()) // 2, y + (back_h - bt.get_height()) // 2))
        self.forge_buttons.append({"rect": back_rect, "action": "back"})

        y += back_h + 12

        title = self.font_manager.render_text("装 备 强 化", "title", (50, 40, 25), 34)
        screen.blit(title, ((self.screen_width - title.get_width()) // 2, y))

        y += 45
        lx = (self.screen_width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 80), (lx, y - 5), (lx + 400, y - 5), 1)

        # 装备列表
        equip_slots = ["weapon", "helmet", "armor", "gloves", "belt", "shoes", "accessory1", "accessory2"]
        panel_w = 560
        panels_x = (self.screen_width - panel_w) // 2

        row_h = 52
        for i, slot_name in enumerate(equip_slots):
            ry = y + i * (row_h + 4)
            eq = self.equipment_slots.get(slot_name)
            is_sel = (self.enhance_selected_slot == slot_name)

            row_rect = pygame.Rect(panels_x, ry, panel_w, row_h)
            row_bg = (100, 80, 160, 120) if is_sel else (60, 55, 48, 140)
            row_bd = (160, 100, 240) if is_sel else (100, 90, 75)
            pygame.draw.rect(screen, row_bg, row_rect, border_radius=6)
            pygame.draw.rect(screen, row_bd, row_rect, 1, border_radius=6)

            cn = EQUIP_SLOT_CN.get(slot_name, slot_name)
            sn_txt = self.font_manager.render_text(cn, "medium", (200, 180, 140), 18)
            screen.blit(sn_txt, (panels_x + 12, ry + (row_h - sn_txt.get_height()) // 2))

            if eq:
                qc = EQUIP_QUALITY_COLORS.get(eq.get("quality", "白"), (180, 180, 180))
                eq_txt = self.font_manager.render_text(eq["name"][:10], "medium", qc, 17)
                screen.blit(eq_txt, (panels_x + 120, ry + 6))

                el = eq.get("enhance_level", 0)
                realm_idx = eq.get("realm_index", 0)
                cap = get_enhance_cap(realm_idx)
                el_txt = self.font_manager.render_text(
                    f"+{el}/{cap}", "medium",
                    (120, 220, 100) if el < cap else (255, 200, 80), 16
                )
                screen.blit(el_txt, (panels_x + 300, ry + (row_h - 16) // 2))

                rn = FORGE_REALM_NAMES[realm_idx] if realm_idx < len(FORGE_REALM_NAMES) else "未知"
                rn_txt = self.font_manager.render_text(rn, "small", (140, 130, 110), 14)
                screen.blit(rn_txt, (panels_x + 370, ry + (row_h - 14) // 2))

                # 成功率
                rate = get_enhance_success_rate(el, realm_idx)
                rate_txt = self.font_manager.render_text(
                    f"成功率:{rate*100:.0f}%",
                    "small", (180, 160, 100) if rate > 0.3 else (220, 120, 100), 13
                )
                screen.blit(rate_txt, (panels_x + 440, ry + (row_h - 13) // 2))
            else:
                empty_txt = self.font_manager.render_text("无装备", "small", (120, 110, 100), 15)
                screen.blit(empty_txt, (panels_x + 120, ry + (row_h - 15) // 2))

            self.forge_buttons.append({
                "rect": row_rect,
                "action": "select_enhance_slot",
                "slot": slot_name,
            })

        # 强化详情区域
        y_after = y + len(equip_slots) * (row_h + 4) + 20
        if self.enhance_selected_slot and self.equipment_slots.get(self.enhance_selected_slot):
            eq = self.equipment_slots[self.enhance_selected_slot]
            el = eq.get("enhance_level", 0)
            realm_idx = eq.get("realm_index", 0)
            cap = get_enhance_cap(realm_idx)

            detail_w = 500
            detail_h = 110
            detail_x = (self.screen_width - detail_w) // 2
            detail_y = y_after

            dsurf = pygame.Surface((detail_w, detail_h), pygame.SRCALPHA)
            pygame.draw.rect(dsurf, (232, 227, 214, 210), (0, 0, detail_w, detail_h), border_radius=8)
            pygame.draw.rect(dsurf, (100, 90, 75, 160), (0, 0, detail_w, detail_h), width=1, border_radius=8)
            screen.blit(dsurf, (detail_x, detail_y))

            qc = EQUIP_QUALITY_COLORS.get(eq.get("quality", "白"), (180, 180, 180))
            cn = EQUIP_SLOT_CN.get(self.enhance_selected_slot, "")
            de_name = self.font_manager.render_text(f"{cn}：{eq['name']}  [{eq.get('quality', '?')}]", "medium", qc, 18)
            screen.blit(de_name, (detail_x + 15, detail_y + 8))

            stats = self.font_manager.render_text(
                f"攻击:{eq.get('attack',0)}  血量:{eq.get('hp',0)}  防御:{eq.get('defense',0)}",
                "small", (100, 200, 200), 14
            )
            screen.blit(stats, (detail_x + 15, detail_y + 32))

            # 材料需求
            mat_info = REALM_ENHANCE_MATERIALS.get(realm_idx, {"name": "?"})
            mat_cnt = player_forge["enhance_materials"].get(realm_idx, 0)
            need = 1  # 每次强化消耗1个材料
            mat_color = (100, 200, 100) if mat_cnt >= need else (220, 100, 100)
            mat_txt = self.font_manager.render_text(
                f"材料: {mat_info['name']}（{FORGE_REALM_NAMES[realm_idx]}）持有: {mat_cnt}  消耗: {need}",
                "small", mat_color, 14
            )
            screen.blit(mat_txt, (detail_x + 15, detail_y + 54))

            rate = get_enhance_success_rate(el, realm_idx)
            rate_txt = self.font_manager.render_text(
                f"成功率: {rate*100:.0f}%  |  上限: +{cap}",
                "small", (220, 180, 80), 14
            )
            screen.blit(rate_txt, (detail_x + 15, detail_y + 74))

            # 强化按钮
            if el < cap and mat_cnt >= need:
                btn_w, btn_h = 120, 36
                btn_x = detail_x + detail_w - btn_w - 15
                btn_y = detail_y + (detail_h - btn_h) // 2
                btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                btn_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
                btn_bg = (80, 60, 40) if btn_hover else (55, 40, 25)
                btn_bd = (200, 150, 60) if btn_hover else (160, 120, 50)
                pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=6)
                pygame.draw.rect(screen, btn_bd, btn_rect, 2, border_radius=6)
                btn_txt = self.font_manager.render_text("开始强化", "medium", (255, 220, 100), 20)
                screen.blit(btn_txt, (btn_x + (btn_w - btn_txt.get_width()) // 2,
                                       btn_y + (btn_h - btn_txt.get_height()) // 2))
                self.forge_buttons.append({"rect": btn_rect, "action": "do_enhance"})
            elif el >= cap:
                cap_txt = self.font_manager.render_text("已达强化上限", "medium", (255, 200, 80), 18)
                screen.blit(cap_txt, (detail_x + detail_w - 140, detail_y + (detail_h - 18) // 2))
            else:
                lack_txt = self.font_manager.render_text("材料不足", "medium", (220, 100, 100), 18)
                screen.blit(lack_txt, (detail_x + detail_w - 140, detail_y + (detail_h - 18) // 2))
        elif self.enhance_selected_slot:
            hint = self.font_manager.render_text("该槽位暂无装备", "small", (160, 150, 130), 16)
            screen.blit(hint, ((self.screen_width - hint.get_width()) // 2, y_after + 20))

        # 结果消息
        if self.forge_result_timer > 0:
            self.forge_result_timer -= 1
            color = (120, 220, 100) if "成功" in self.forge_result else (220, 120, 100)
            rt = self.font_manager.render_text(self.forge_result, "medium", color, 18)
            screen.blit(rt, ((self.screen_width - rt.get_width()) // 2, y_after))

    def _draw_forge_craft_panel(self, screen):
        """锻造面板 - 选择槽位和境界进行锻造"""
        margin = 30
        y = 40

        # 返回按钮
        back_w, back_h = 100, 32
        back_rect = pygame.Rect(margin, y, back_w, back_h)
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        bg = (65, 55, 45) if hover else (45, 38, 30)
        bd = (130, 110, 80) if hover else (90, 80, 60)
        pygame.draw.rect(screen, bg, back_rect, border_radius=4)
        pygame.draw.rect(screen, bd, back_rect, 1, border_radius=4)
        bt = self.font_manager.render_text("« 返回", "small", (200, 180, 140), 14)
        screen.blit(bt, (margin + (back_w - bt.get_width()) // 2, y + (back_h - bt.get_height()) // 2))
        self.forge_buttons.append({"rect": back_rect, "action": "back"})

        y += back_h + 12

        title = self.font_manager.render_text("锻 造 装 备", "title", (50, 40, 25), 34)
        screen.blit(title, ((self.screen_width - title.get_width()) // 2, y))

        y += 45
        lx = (self.screen_width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 80), (lx, y - 5), (lx + 400, y - 5), 1)

        # 锻造师经验条
        bar_x = margin + 10
        bar_w = 200
        bar_h = 10
        level = player_forge["level"]
        exp = player_forge["exp"]
        exp_max = forge_get_exp(level) if level < FORGER_MAX_LEVEL else 1
        if level >= FORGER_MAX_LEVEL:
            exp = exp_max
        exp_txt = self.font_manager.render_text(
            f"锻造师 Lv.{level}（{exp}/{exp_max}）", "small", (180, 160, 120), 14
        )
        screen.blit(exp_txt, (bar_x, y + 2))
        bar_y = y + 22
        pygame.draw.rect(screen, (35, 30, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        if exp_max > 0:
            fill_w = int(bar_w * exp / exp_max)
            pygame.draw.rect(screen, (160, 120, 60), (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        y = bar_y + bar_h + 15

        # === 左侧：槽位选择 ===
        left_w = 280
        left_title = self.font_manager.render_text("选择装备槽位", "medium", (200, 180, 120), 20)
        screen.blit(left_title, (margin + 10, y))

        slots = ["weapon", "helmet", "armor", "gloves", "belt", "shoes", "accessory1", "accessory2"]
        sy = y + 30
        sbtn_w, sbtn_h = 120, 36
        scols = 2

        for i, slot_name in enumerate(slots):
            col = i % scols
            row = i // scols
            bx = margin + 10 + col * (sbtn_w + 8)
            by = sy + row * (sbtn_h + 6)
            is_sel = (self.forge_selected_slot == slot_name)

            bg_c = (80, 60, 180) if is_sel else (60, 55, 45)
            bd_c = (180, 120, 255) if is_sel else (100, 90, 75)
            btn_rect = pygame.Rect(bx, by, sbtn_w, sbtn_h)
            hov = btn_rect.collidepoint(pygame.mouse.get_pos())
            if hov and not is_sel:
                bg_c = (75, 68, 55)
                bd_c = (140, 125, 100)

            pygame.draw.rect(screen, bg_c, btn_rect, border_radius=4)
            pygame.draw.rect(screen, bd_c, btn_rect, 1, border_radius=4)

            cn = EQUIP_SLOT_CN.get(slot_name, slot_name)
            st = self.font_manager.render_text(cn, "small", (220, 210, 180), 15)
            screen.blit(st, (bx + (sbtn_w - st.get_width()) // 2, by + (sbtn_h - st.get_height()) // 2))
            self.forge_buttons.append({
                "rect": btn_rect, "action": "select_forge_slot", "slot": slot_name,
            })

        # === 右侧：境界选择 ===
        right_x = margin + left_w + 40
        realm_title = self.font_manager.render_text("选择装备境界", "medium", (200, 180, 120), 20)
        screen.blit(realm_title, (right_x, y))

        ry = y + 30
        rbtn_w, rbtn_h = 72, 36
        rcols = 5

        for ri in range(9):
            col = ri % rcols
            row = ri // rcols
            bx = right_x + col * (rbtn_w + 4)
            by = ry + row * (rbtn_h + 6)
            is_sel = (self.forge_selected_realm == ri)
            mat_cnt = player_forge["forge_materials"].get(ri, 0)
            can_forge = mat_cnt >= 1

            bg_c = (60, 90, 40) if is_sel else ((50, 60, 40) if can_forge else (40, 35, 30))
            bd_c = (120, 200, 80) if is_sel else ((90, 120, 70) if can_forge else (60, 50, 40))
            btn_rect = pygame.Rect(bx, by, rbtn_w, rbtn_h)

            pygame.draw.rect(screen, bg_c, btn_rect, border_radius=4)
            pygame.draw.rect(screen, bd_c, btn_rect, 1, border_radius=4)

            rn = FORGE_REALM_NAMES[ri]
            rt = self.font_manager.render_text(rn, "small", (220, 210, 160), 14)
            screen.blit(rt, (bx + (rbtn_w - rt.get_width()) // 2, by + 2))
            mc = self.font_manager.render_text(f"x{mat_cnt}", "small", (180, 160, 100), 12)
            screen.blit(mc, (bx + (rbtn_w - mc.get_width()) // 2, by + 20))

            self.forge_buttons.append({
                "rect": btn_rect, "action": "select_forge_realm", "realm": ri,
            })

        # === 锻造详情区域 ===
        detail_y = ry + 2 * (rbtn_h + 6) + 20

        if self.forge_selected_slot:
            realm_idx = self.forge_selected_realm
            mat_info = REALM_FORGE_MATERIALS.get(realm_idx, {"name": "?"})
            mat_cnt = player_forge["forge_materials"].get(realm_idx, 0)
            cn = EQUIP_SLOT_CN.get(self.forge_selected_slot, "")

            detail_w = 520
            detail_h = 160
            detail_x = margin + 10
            detail_y2 = detail_y

            dsurf = pygame.Surface((detail_w, detail_h), pygame.SRCALPHA)
            pygame.draw.rect(dsurf, (232, 227, 214, 200), (0, 0, detail_w, detail_h), border_radius=8)
            pygame.draw.rect(dsurf, (100, 90, 75, 160), (0, 0, detail_w, detail_h), width=1, border_radius=8)
            screen.blit(dsurf, (detail_x, detail_y2))

            dinfo = self.font_manager.render_text(
                f"锻造信息：{FORGE_REALM_NAMES[realm_idx]}·{cn}",
                "medium", (50, 40, 25), 20
            )
            screen.blit(dinfo, (detail_x + 12, detail_y2 + 8))

            mat_txt = self.font_manager.render_text(
                f"材料: {mat_info['name']}  |  持有: {mat_cnt}  |  消耗: 1",
                "small", (100, 200, 100) if mat_cnt >= 1 else (220, 100, 100), 15
            )
            screen.blit(mat_txt, (detail_x + 12, detail_y2 + 36))

            desc_txt = self.font_manager.render_text(mat_info["desc"], "small", (140, 130, 110), 14)
            screen.blit(desc_txt, (detail_x + 12, detail_y2 + 56))

            # 品质概率
            fl = player_forge["level"]
            probs = forge_data.get_forge_quality_probs(fl, realm_idx)
            prob_label = self.font_manager.render_text("品质概率:", "small", (160, 150, 120), 15)
            screen.blit(prob_label, (detail_x + 12, detail_y2 + 78))
            for qi, (qname, prob) in enumerate(zip(EQUIP_QUALITIES, probs)):
                qx = detail_x + 12 + qi * 80
                qc = EQUIP_QUALITY_COLORS[qname]
                qt = self.font_manager.render_text(f"{qname}:{prob}%", "small", qc, 15)
                screen.blit(qt, (qx, detail_y2 + 100))

            # 锻造按钮
            btn_w, btn_h = 140, 40
            btn_x = detail_x + detail_w - btn_w - 20
            btn_y = detail_y2 + (detail_h - btn_h) // 2
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            can = mat_cnt >= 1
            btn_hover = btn_rect.collidepoint(pygame.mouse.get_pos())
            btn_bg = (80, 60, 30) if (btn_hover and can) else ((60, 40, 25) if can else (45, 35, 25))
            btn_bd = (220, 150, 40) if (btn_hover and can) else ((180, 120, 30) if can else (100, 80, 50))
            pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=8)
            pygame.draw.rect(screen, btn_bd, btn_rect, 2, border_radius=8)
            btn_txt = self.font_manager.render_text("锻 造", "large", (255, 220, 100) if can else (150, 140, 120), 24)
            screen.blit(btn_txt, (btn_x + (btn_w - btn_txt.get_width()) // 2,
                                   btn_y + (btn_h - btn_txt.get_height()) // 2))
            self.forge_buttons.append({"rect": btn_rect, "action": "do_forge"})

            # 境界差异提示
            diff = player_forge["level"] - (realm_idx + 1)
            if diff > 0:
                tip = self.font_manager.render_text(
                    f"锻造师等级高于装备境界 {diff} 级，高品质概率提升",
                    "small", (120, 220, 120), 14
                )
            elif diff < 0:
                tip = self.font_manager.render_text(
                    f"锻造师等级低于装备境界 {abs(diff)} 级，低品质概率提升",
                    "small", (220, 120, 120), 14
                )
            else:
                tip = self.font_manager.render_text("锻造师等级与装备境界持平", "small", (200, 200, 100), 14)
            screen.blit(tip, (detail_x + 12, detail_y2 + 130))

        # 结果消息
        if self.forge_result_timer > 0:
            self.forge_result_timer -= 1
            color = (120, 220, 100) if "成功" in self.forge_result else (220, 120, 100)
            rt = self.font_manager.render_text(self.forge_result, "medium", color, 18)
            screen.blit(rt, ((self.screen_width - rt.get_width()) // 2, self.content_height - 60))

    def _do_enhance(self):
        """执行强化"""
        if not self.enhance_selected_slot:
            return
        eq = self.equipment_slots.get(self.enhance_selected_slot)
        if not eq:
            return

        el = eq.get("enhance_level", 0)
        realm_idx = eq.get("realm_index", 0)
        cap = get_enhance_cap(realm_idx)

        if el >= cap:
            self.forge_result = f"{eq['name']} 已达强化上限 +{cap}"
            self.forge_result_timer = 90
            return

        mat_cnt = player_forge["enhance_materials"].get(realm_idx, 0)
        if mat_cnt < 1:
            self.forge_result = "强化材料不足"
            self.forge_result_timer = 90
            return

        # 消耗材料
        player_forge["enhance_materials"][realm_idx] = mat_cnt - 1

        # 判定成功
        rate = get_enhance_success_rate(el, realm_idx)
        if random.random() < rate:
            old_attack = eq.get("attack", 0)
            old_hp = eq.get("hp", 0)
            old_def = eq.get("defense", 0)
            new_el = el + 1
            apply_enhance_stats(eq, new_el)
            # 同步玩家属性
            pdata = realm_data.player
            pdata["attack"] += eq["attack"] - old_attack
            pdata["hp"] += eq["hp"] - old_hp
            pdata["max_hp"] += eq["hp"] - old_hp
            pdata["defense"] += eq["defense"] - old_def
            self.forge_result = f"强化成功！{eq['name']} → +{new_el}"
            self.forge_result_timer = 120
        else:
            self.forge_result = f"强化失败！{eq['name']} 仍为 +{el}"
            self.forge_result_timer = 90

    def _equip_from_inventory(self, item):
        """从背包装备物品到对应槽位"""
        slot_type = item.get("slot_type")
        if not slot_type or slot_type not in self.equipment_slots:
            return

        # 卸载旧装备
        old_eq = self.equipment_slots.get(slot_type)
        if old_eq:
            pdata = realm_data.player
            pdata["attack"] -= old_eq.get("attack", 0)
            pdata["hp"] -= old_eq.get("hp", 0)
            pdata["max_hp"] -= old_eq.get("hp", 0)
            pdata["defense"] -= old_eq.get("defense", 0)
            # 旧装备放回背包
            old_eq["type"] = "装备"
            self.inv_items.append(old_eq)

        # 装备新物品
        new_eq = {
            "name": item["name"],
            "type": "equipment",
            "quality": item.get("quality", 1),
            "attack": item.get("attack", 0),
            "hp": item.get("hp", 0),
            "defense": item.get("defense", 0),
            "slot_type": slot_type,
        }
        self.equipment_slots[slot_type] = new_eq

        # 加属性
        pdata = realm_data.player
        pdata["attack"] += new_eq["attack"]
        pdata["hp"] += new_eq["hp"]
        pdata["max_hp"] += new_eq["hp"]
        pdata["defense"] += new_eq["defense"]

        # 从背包移除
        self.inv_items.remove(item)
        self.inv_selected_item = None
        print(f"[装备] {item['name']} 已装备到 {self._get_equip_slot_name_cn(slot_type)}")

    def _do_forge(self):
        """执行锻造，产出装备放入背包"""
        if not self.forge_selected_slot:
            return
        realm_idx = self.forge_selected_realm
        mat_cnt = player_forge["forge_materials"].get(realm_idx, 0)
        if mat_cnt < 1:
            self.forge_result = "锻造材料不足"
            self.forge_result_timer = 90
            return

        # 消耗材料
        player_forge["forge_materials"][realm_idx] = mat_cnt - 1

        # 判定品质
        quality = roll_forge_quality(player_forge["level"], realm_idx)

        # 检查该槽是否已有旧装备，如有则卸载其属性
        old_eq = self.equipment_slots.get(self.forge_selected_slot)
        if old_eq:
            pdata = realm_data.player
            pdata["attack"] -= old_eq.get("attack", 0)
            pdata["hp"] -= old_eq.get("hp", 0)
            pdata["max_hp"] -= old_eq.get("hp", 0)
            pdata["defense"] -= old_eq.get("defense", 0)
            self.equipment_slots[self.forge_selected_slot] = None

        # 锻造新装备，不自动装备，放入背包
        new_eq = forge_equipment(self.forge_selected_slot, realm_idx, quality)

        # 生成唯一ID
        import uuid
        equip_id = str(uuid.uuid4())[:8]

        # 存入背包物品列表
        self.inv_items.append({
            "id": equip_id,
            "name": new_eq["name"],
            "type": "装备",
            "quality": quality,
            "slot_type": self.forge_selected_slot,
            "realm_idx": realm_idx,
            "attack": new_eq.get("attack", 0),
            "hp": new_eq.get("hp", 0),
            "defense": new_eq.get("defense", 0),
            "desc": f"{new_eq['name']}，品质{quality}",
        })

        # 锻造师经验
        exp_gain = (realm_idx + 1) * 15
        player_forge["exp"] += exp_gain
        old_level = player_forge["level"]
        while player_forge["level"] < FORGER_MAX_LEVEL:
            needed = forge_get_exp(player_forge["level"])
            if player_forge["exp"] >= needed:
                player_forge["exp"] -= needed
                player_forge["level"] += 1
            else:
                break

        levelup_msg = ""
        if player_forge["level"] > old_level:
            levelup_msg = f" 锻造师升级至 Lv.{player_forge['level']}！"

        self.forge_result = f"锻造成功！获得 {quality}品 {new_eq['name']}，已放入背包{levelup_msg}"
        self.forge_result_timer = 150

    def _sync_equip_stats(self):
        """同步装备属性到玩家（重新计算所有装备的总属性）"""
        pdata = realm_data.player
        # 简单方案：直接从装备重新计算
        # 这里我们采用增量方案：强化+1增加对应属性
        # 已在 apply_enhance_stats 中处理，这里不需要额外操作
        pass

    def draw_content(self, screen):
        """根据激活标签绘制对应内容"""
        content_methods = {
            "character": self.draw_content_character,
            "inventory": self.draw_content_inventory,
            "sect": self.draw_content_sect,
            "craft": self.draw_content_craft,
            "cave": self.draw_content_cave,
            "treasure": self.draw_content_treasure,
            "battle": self.draw_content_battle,
        }
        draw_fn = content_methods.get(self.active_tab)
        if draw_fn:
            draw_fn(screen)

    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()

        self.hovered_tab = None
        for tab in self.tabs:
            if tab["rect"].collidepoint(mouse_pos):
                self.hovered_tab = tab["id"]
                break
        
        # 更新设置按钮悬停状态
        self.settings_button_hovered = self.settings_button_rect.collidepoint(mouse_pos)
        
        # 更新修炼按钮悬停状态
        if self.active_tab == "character":
            if hasattr(self, "cultivate_button"):
                self.cultivate_hovered = self.cultivate_button.collidepoint(mouse_pos)
            if hasattr(self, "breakthrough_button"):
                self.breakthrough_hovered = self.breakthrough_button.collidepoint(mouse_pos)
        
        # 更新宗门按钮悬停状态
        self.sect_btn_hovered = None
        self.leave_btn_hovered = False
        if self.active_tab == "sect":
            if hasattr(self, 'leave_button_rect') and self.leave_button_rect:
                self.leave_btn_hovered = self.leave_button_rect.collidepoint(mouse_pos)
            if hasattr(self, 'sect_buttons'):
                for btn in self.sect_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        self.sect_btn_hovered = btn["sect_name"]
                        break

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"

            # 调试面板事件优先
            panel_consumed = self.debug_panel.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for tab in self.tabs:
                    if tab["id"] == self.hovered_tab:
                        self.pressed_tab = tab["id"]
                        break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pressed_tab:
                    for tab in self.tabs:
                        if tab["id"] == self.pressed_tab and tab["rect"].collidepoint(mouse_pos):
                            self.active_tab = tab["id"]
                    self.pressed_tab = None

                # ===== 背包面板点击处理 =====
                if self.active_tab == "inventory":
                    # 装备槽位点击（圆环环绕）
                    if hasattr(self, "equip_slot_positions"):
                        for slot_name, (sx, sy, sw, sh) in self.equip_slot_positions.items():
                            if pygame.Rect(sx, sy, sw, sh).collidepoint(mouse_pos):
                                self.inv_selected_slot = slot_name
                                self.inv_selected_item = None
                                break

                    # 物品格子区域参数（最右边，离右边缘1个槽位）
                    slot_w, slot_h = 80, 72
                    slot_gap_x, slot_gap_y = 12, 10
                    grid_rows = self.inv_grid_rows
                    grid_total_w = self.inv_grid_cols * slot_w + (self.inv_grid_cols - 1) * slot_gap_x
                    grid_start_x = self.screen_width - (slot_w + slot_gap_x) - grid_total_w
                    grid_start_y = 105

                    # 分类标签点击（在格子正上方）
                    cat_w, cat_h = 72, 26
                    cat_gap = 5
                    total_cat_w = len(self.inv_categories) * cat_w + (len(self.inv_categories) - 1) * cat_gap
                    cat_start_x = grid_start_x + (self.inv_grid_cols * (slot_w + slot_gap_x) - slot_gap_x - total_cat_w) // 2
                    cat_y = 62
                    for i in range(len(self.inv_categories)):
                        cx = cat_start_x + i * (cat_w + cat_gap)
                        if pygame.Rect(cx, cat_y, cat_w, cat_h).collidepoint(mouse_pos):
                            self.inv_active_category = i
                            self.inv_page = 0
                            self.inv_selected_item = None
                            self.inv_selected_slot = None

                    # 分页按钮点击
                    page_btn_w, page_btn_h = 90, 32
                    page_y = grid_start_y + grid_rows * (slot_h + slot_gap_y) + 12

                    prev_rect = pygame.Rect(grid_start_x, page_y, page_btn_w, page_btn_h)
                    next_x = grid_start_x + self.inv_grid_cols * (slot_w + slot_gap_x) - slot_gap_x - page_btn_w
                    next_rect = pygame.Rect(next_x, page_y, page_btn_w, page_btn_h)

                    filtered = self._get_inv_filtered_items()
                    total_pages = max(1, (len(filtered) + self.inv_items_per_page - 1) // self.inv_items_per_page)

                    if prev_rect.collidepoint(mouse_pos) and self.inv_page > 0:
                        self.inv_page -= 1
                        self.inv_selected_item = None
                    if next_rect.collidepoint(mouse_pos) and self.inv_page < total_pages - 1:
                        self.inv_page += 1
                        self.inv_selected_item = None

                    # 物品格子点击
                    col_gap = slot_w + slot_gap_x
                    row_gap = slot_h + slot_gap_y
                    start_idx = self.inv_page * self.inv_items_per_page
                    page_items = filtered[start_idx:start_idx + self.inv_items_per_page]
                    for i in range(self.inv_items_per_page):
                        col = i % self.inv_grid_cols
                        row = i // self.inv_grid_cols
                        sx = grid_start_x + col * col_gap
                        sy = grid_start_y + row * row_gap
                        if pygame.Rect(sx, sy, slot_w, slot_h).collidepoint(mouse_pos):
                            if i < len(page_items):
                                self.inv_selected_item = page_items[i]
                                self.inv_selected_slot = None
                            break

                    # 装备按钮点击
                    if hasattr(self, "inv_equip_btn_rect") and self.inv_equip_btn_rect and \
                       self.inv_selected_item and self.inv_selected_item.get("type") == "装备":
                        if self.inv_equip_btn_rect.collidepoint(mouse_pos):
                            self._equip_from_inventory(self.inv_selected_item)
                            return

                # 检查战斗子选项点击
                if self.active_tab == "battle":
                    # 优先检查"返回战斗"按钮
                    if (hasattr(self, 'in_combat') and self.in_combat and 
                        hasattr(self, 'return_to_combat_rect') and
                        self.return_to_combat_rect.collidepoint(mouse_pos)):
                        print("[MainMenu] 返回战斗")
                        return "goto_combat_view"
                    
                    if hasattr(self, "battle_sub_rects"):
                        for sub in self.battle_sub_rects:
                            if sub["rect"].collidepoint(mouse_pos):
                                print(f"[MainMenu] 战斗子选项点击: {sub['name']}")
                                return f"goto_battle_{sub['name']}"

                # 检查炼制子选项点击（仅在主列表界面）
                if self.active_tab == "craft" and self.craft_sub_tab is None and hasattr(self, "craft_sub_rects"):
                    for sub in self.craft_sub_rects:
                        if sub["rect"].collidepoint(mouse_pos):
                            print(f"[MainMenu] 炼制子选项点击: {sub['name']}")
                            if sub["name"] == "炼丹":
                                self.craft_sub_tab = "炼丹"
                            elif sub["name"] == "炼器":
                                self.craft_sub_tab = "炼器"
                                seed_test_materials()
                            else:
                                return f"goto_craft_{sub['name']}"

                # 检查宗门按钮点击
                if self.active_tab == "sect":
                    # 子标签切换
                    if hasattr(self, 'sect_sub_rects'):
                        for sub in self.sect_sub_rects:
                            if sub["rect"].collidepoint(mouse_pos):
                                self.sect_sub_tab = sub["name"]
                                print(f"[MainMenu] 宗门子标签切换: {sub['name']}")

                    # 退出宗门按钮
                    if hasattr(self, 'leave_button_rect') and self.leave_button_rect and self.leave_button_rect.collidepoint(mouse_pos):
                        sect_data.leave_sect()
                        self.sect_sub_tab = "主殿"
                        print("[MainMenu] 已退出宗门")

                    # 晋升按钮
                    if hasattr(self, 'promote_btn_rect') and self.promote_btn_rect and self.promote_btn_rect.collidepoint(mouse_pos):
                        ok, msg = sect_data.promote_rank()
                        print(f"[MainMenu] 晋升: {msg}")

                    # 加入宗门按钮
                    if hasattr(self, 'sect_buttons'):
                        for btn in self.sect_buttons:
                            if btn["rect"].collidepoint(mouse_pos):
                                sect_data.join_sect(btn["sect_name"])
                                self.sect_sub_tab = "主殿"
                                print(f"[MainMenu] 已加入宗门: {btn['sect_name']}")
                                break

                    # 任务等级切换
                    if hasattr(self, 'task_lv_buttons'):
                        for btn in self.task_lv_buttons:
                            if btn["rect"].collidepoint(mouse_pos):
                                sect_data.change_task_level(btn["lv"])
                                print(f"[MainMenu] 切换任务等级: {btn['lv']}")

                    # 贡献堂分类
                    if hasattr(self, 'shop_cat_rects'):
                        for cr in self.shop_cat_rects:
                            if cr["rect"].collidepoint(mouse_pos):
                                self.shop_category = cr["cat"]
                                print(f"[MainMenu] 贡献堂分类: {cr['cat']}")

                    # 贡献堂物品兑换
                    if hasattr(self, 'shop_item_rects'):
                        for sr in self.shop_item_rects:
                            if sr["rect"].collidepoint(mouse_pos):
                                ok, msg = sect_data.buy_shop_item(sr["cat"], sr["index"])
                                print(f"[MainMenu] 兑换: {msg}")

                    # 参悟按钮
                    if hasattr(self, 'meditate_btn_rect') and self.meditate_btn_rect and self.meditate_btn_rect.collidepoint(mouse_pos):
                        ok, msg = sect_data.start_meditate()
                        print(f"[MainMenu] 参悟: {msg}")
                        if ok:
                            from character_panel import _start_cultivation
                            _start_cultivation()

                # ===== 洞府面板点击处理 =====
                if self.active_tab == "cave" and hasattr(self, 'cave_buttons'):
                    for btn in self.cave_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            btn_name = btn["name"]
                            
                            # 子标签切换
                            if btn_name in ("灵药园", "聚灵阵"):
                                self.cave_sub_tab = btn_name
                                self.selected_field = None
                                self.selected_seed = None
                                print(f"[MainMenu] 洞府子标签切换: {btn_name}")
                                break
                            
                            # 道童雇佣
                            if btn_name == "hire_apprentice":
                                ok, msg = cave_data.hire_apprentice()
                                print(f"[MainMenu] 道童雇佣: {msg}")
                                break
                            
                            # 聚灵阵升级
                            if btn_name == "upgrade_array":
                                ok, msg = cave_data.upgrade_spirit_array()
                                print(f"[MainMenu] 聚灵阵升级: {msg}")
                                break
                            
                            # 种子选择
                            if btn_name.startswith("seed_"):
                                seed_name = btn_name[5:]  # 去掉 "seed_"
                                self.selected_seed = seed_name
                                print(f"[MainMenu] 选中种子: {seed_name}")
                                break
                            
                            # 种植按钮
                            if btn_name == "plant_seed" and self.selected_seed and self.selected_field is not None:
                                ok, msg = cave_data.plant_seed(self.selected_field, self.selected_seed)
                                print(f"[MainMenu] 种植: {msg}")
                                self.selected_seed = None
                                break
                    
                    # 药田点击（在cave_buttons之外单独处理）
                    if self.cave_sub_tab == "灵药园":
                        field_w, field_h = 180, 120
                        gap = 20
                        cols = 3
                        fields = cave_data.player_cave["herb_garden"]["fields"]
                        
                        total_w = cols * field_w + (cols - 1) * gap
                        start_x = (self.screen_width - total_w) // 2
                        start_y = 280  # 与绘制时保持一致
                        
                        for i in range(len(fields)):
                            row = i // cols
                            col = i % cols
                            fx = start_x + col * (field_w + gap)
                            fy = start_y + row * (field_h + gap)
                            field_rect = pygame.Rect(fx, fy, field_w, field_h)
                            
                            if field_rect.collidepoint(mouse_pos):
                                if self.selected_field == i:
                                    # 取消选中
                                    self.selected_field = None
                                    self.selected_seed = None
                                else:
                                    self.selected_field = i
                                    self.selected_seed = None
                                print(f"[MainMenu] 选中药田: {i}")
                                break

                # ===== 藏宝阁面板点击处理 =====
                if self.active_tab == "treasure":
                    # 楼层切换
                    if hasattr(self, 'treasure_floor_rects'):
                        for i, fr in enumerate(self.treasure_floor_rects):
                            if fr.collidepoint(mouse_pos):
                                import realm_data as rd
                                if rd.player["realm_index"] >= i:
                                    self.treasure_current_floor = i
                                    self.treasure_selected_item = None
                                    self.treasure_selected_type = None
                                    print(f"[MainMenu] 藏宝阁楼层切换: {i}")
                                break

                    # 子标签切换
                    if hasattr(self, 'treasure_sub_rects'):
                        for sub in self.treasure_sub_rects:
                            if sub["rect"].collidepoint(mouse_pos):
                                self.treasure_sub_tab = sub["name"]
                                self.treasure_selected_item = None
                                self.treasure_selected_type = None
                                print(f"[MainMenu] 藏宝阁子标签切换: {sub['name']}")
                                break

                    # 商品点击
                    if hasattr(self, 'treasure_buttons'):
                        for btn in self.treasure_buttons:
                            if btn["rect"].collidepoint(mouse_pos):
                                btn_type = btn["type"]
                                if btn_type == "gongfa":
                                    self.treasure_selected_item = btn["gid"]
                                    self.treasure_selected_type = "gongfa"
                                elif btn_type == "equipment":
                                    self.treasure_selected_item = btn["equip"]["id"]
                                    self.treasure_selected_type = "equipment"
                                elif btn_type == "pill":
                                    self.treasure_selected_item = btn["pill"]["id"]
                                    self.treasure_selected_type = "pill"
                                elif btn_type == "material":
                                    self.treasure_selected_item = btn["material"]["id"]
                                    self.treasure_selected_type = "material"
                                break

                    # 信息面板购买按钮点击
                    if (self.treasure_selected_item is not None and 
                        self.treasure_selected_type is not None and
                        hasattr(self, 'treasure_buy_rect') and
                        self.treasure_buy_rect.collidepoint(mouse_pos)):
                        for btn in self.treasure_buttons:
                            match = False
                            if self.treasure_selected_type == "gongfa" and btn["type"] == "gongfa" and btn["gid"] == self.treasure_selected_item:
                                match = True
                            elif self.treasure_selected_type == "equipment" and btn["type"] == "equipment" and btn["equip"]["id"] == self.treasure_selected_item:
                                match = True
                            elif self.treasure_selected_type == "pill" and btn["type"] == "pill" and btn["pill"]["id"] == self.treasure_selected_item:
                                match = True
                            elif self.treasure_selected_type == "material" and btn["type"] == "material" and btn["material"]["id"] == self.treasure_selected_item:
                                match = True
                            if match:
                                self._buy_treasure_item(btn)
                                break

                # 检查设置按钮点击
                if self.settings_button_rect.collidepoint(mouse_pos):
                    print("[MainMenu] 进入设置界面")
                    return "goto_settings"
                
                # 检查人物子标签点击
                if self.active_tab == "character":
                    if hasattr(self, 'sub_tab_rects'):
                        for st_name, st_rect in self.sub_tab_rects.items():
                            if st_rect.collidepoint(mouse_pos):
                                self.character_sub_tab = st_name
                                print(f"[MainMenu] 人物子标签切换: {st_name}")
                                break

                    # 功法子标签内的类型筛选
                    if self.character_sub_tab == "功法" and hasattr(self, 'gf_type_rects'):
                        for tt_name, tt_rect in self.gf_type_rects.items():
                            if tt_rect.collidepoint(mouse_pos):
                                self.gf_type_tab = tt_name
                                self.gf_scroll = 0
                                print(f"[MainMenu] 功法类型筛选: {tt_name}")
                                break

                    # 功法修炼/遗忘按钮
                    if self.character_sub_tab == "功法" and hasattr(self, 'gf_buttons'):
                        for btn_rect, gongfa, is_equipped in self.gf_buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                if is_equipped:
                                    # 遗忘功法
                                    self._forget_gongfa(gongfa)
                                else:
                                    # 修炼功法（装备）
                                    self._learn_gongfa(gongfa)
                                print(f"[MainMenu] 功法操作: {'遗忘' if is_equipped else '修炼'} {gongfa['name']}")
                                break

                # 检查修炼按钮点击
                if self.active_tab == "character" and self.character_sub_tab == "角色":
                    if hasattr(self, "cultivate_button") and self.cultivate_button.collidepoint(mouse_pos):
                        from character_panel import _start_cultivation, _stop_cultivation
                        state = realm_data.cultivation_state
                        if state["is_cultivating"]:
                            _stop_cultivation()
                            print("停止修炼...")
                        else:
                            _start_cultivation()
                            print("开始修炼...")
                    if hasattr(self, "breakthrough_button") and self.breakthrough_button.collidepoint(mouse_pos):
                        from character_panel import _can_breakthrough, _try_breakthrough
                        if _can_breakthrough():
                            success, new_stage, new_realm = _try_breakthrough()
                            if success:
                                print(f"突破成功！当前境界: {new_realm} 第{new_stage}阶")

                # ===== 炼丹面板点击处理 =====
                if self.active_tab == "craft" and self.craft_sub_tab == "炼丹":
                    for btn in self.alchemy_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            action = btn["action"]
                            if action == "back":
                                self.craft_sub_tab = None
                            elif action == "select_type":
                                self.alchemy_selected_type = btn["index"]
                            elif action == "select_grade":
                                self.alchemy_selected_grade = btn["index"]
                            elif action == "craft":
                                ptype = PILL_TYPE_ORDER[self.alchemy_selected_type]
                                grade = self.alchemy_selected_grade + 1
                                pill, quality = craft_pill(ptype, grade)
                                if pill:
                                    self.alchemy_craft_result = f"炼制成功！获得 {pill['name']}（{quality}）"
                                    self.alchemy_craft_result_timer = 120
                                    self.alchemy_selected_pill = None
                                else:
                                    self.alchemy_craft_result = "材料不足，无法炼制"
                                    self.alchemy_craft_result_timer = 90
                            elif action == "consume":
                                if (self.alchemy_selected_pill is not None and
                                        self.alchemy_selected_pill < len(player_alchemy["pills"])):
                                    pill = player_alchemy["pills"].pop(self.alchemy_selected_pill)
                                    et = pill["effect_type"]
                                    ev = pill["effect_value"]
                                    pdata = realm_data.player
                                    if et == "attack":
                                        pdata["attack"] += ev
                                    elif et == "max_hp":
                                        pdata["max_hp"] += ev
                                        pdata["hp"] += ev
                                    elif et == "defense":
                                        pdata["defense"] += ev
                                    elif et == "max_mp":
                                        pdata["max_mp"] += ev
                                        pdata["mp"] += ev
                                    elif et == "cultivation":
                                        pdata["cultivation"] += ev
                                    self.alchemy_selected_pill = None
                                    print(f"[Alchemy] 服用 {pill['name']}，效果: {pill['desc']}")
                            break
                    for btn in self.alchemy_pill_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            self.alchemy_selected_pill = btn["index"]
                            break

                # ===== 炼器面板点击处理 =====
                if self.active_tab == "craft" and self.craft_sub_tab == "炼器":
                    for btn in self.forge_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            action = btn["action"]
                            if action == "back":
                                if self.forge_sub_tab is not None:
                                    self.forge_sub_tab = None
                                else:
                                    self.craft_sub_tab = None
                            elif action == "goto_enhance":
                                self.forge_sub_tab = "强化"
                                self.enhance_selected_slot = None
                            elif action == "goto_forge":
                                self.forge_sub_tab = "锻造"
                                self.forge_selected_slot = None
                                self.forge_selected_realm = 0
                            elif action == "select_enhance_slot":
                                self.enhance_selected_slot = btn["slot"]
                            elif action == "do_enhance":
                                self._do_enhance()
                            elif action == "select_forge_slot":
                                self.forge_selected_slot = btn["slot"]
                            elif action == "select_forge_realm":
                                self.forge_selected_realm = btn["realm"]
                            elif action == "do_forge":
                                self._do_forge()
                            break

            if event.type == pygame.MOUSEWHEEL:
                if self.active_tab == "character" and self.character_sub_tab == "功法":
                    self.gf_scroll = getattr(self, 'gf_scroll', 0)
                    self.gf_scroll = max(0, self.gf_scroll - event.y)

            if event.type == pygame.KEYDOWN:
                # 调试面板消费了事件则跳过
                if panel_consumed:
                    pass
                # F2 切换调试面板
                elif event.key == pygame.K_F2:
                    self.debug_panel.toggle()
                elif event.key == pygame.K_ESCAPE:
                    # 调试面板打开时，ESC 交给面板自己处理，不退出游戏
                    if not self.debug_panel.visible:
                        if self.craft_sub_tab == "炼丹":
                            self.craft_sub_tab = None
                        elif self.craft_sub_tab == "炼器":
                            if self.forge_sub_tab is not None:
                                self.forge_sub_tab = None
                            else:
                                self.craft_sub_tab = None
                        else:
                            self.running = False
                            return "quit"
                elif event.key == pygame.K_1:
                    self.active_tab = "character"
                elif event.key == pygame.K_2:
                    self.active_tab = "inventory"
                elif event.key == pygame.K_3:
                    self.active_tab = "sect"
                elif event.key == pygame.K_4:
                    self.active_tab = "craft"
                elif event.key == pygame.K_5:
                    self.active_tab = "cave"
                elif event.key == pygame.K_6:
                    self.active_tab = "treasure"
                elif event.key == pygame.K_7:
                    self.active_tab = "battle"

        return None

    def update(self):
        """更新"""
        import sect_data as sd
        sd.update_tasks()  # 自动结算宗门任务
        import cave_data as cd
        cd.update_growth()  # 自动更新药田生长状态
        cd.auto_manage_garden()  # 道童自动管理
        # 同步灵石数量
        if self.ling_shi_wallet:
            self.ling_shi_amount = self.ling_shi_wallet.amount
        for p in self.ink_particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = self.content_height + 10
                p["x"] = random.randint(0, self.screen_width)

    def draw(self, screen):
        """绘制"""
        if self.background_cache is None:
            self.create_background()
        screen.blit(self.background_cache, (0, 0))

        # 墨点
        for p in self.ink_particles:
            pygame.draw.circle(screen, (70, 65, 55, p["alpha"]),
                             (int(p["x"]), int(p["y"])), p["size"])

        # 上方内容
        self.draw_content(screen)

        # 底部栏
        self.draw_tab_bar(screen)

        # 藏宝阁提示
        if self.treasure_toast_timer > 0:
            self.treasure_toast_timer -= 1
            tt = self.font_manager.render_text(self.treasure_toast, "medium", (0, 255, 180), 18)
            screen.blit(tt, ((self.screen_width - tt.get_width()) // 2, self.content_height - 50))

        # 设置按钮（右上角）
        self.draw_settings_button(screen)

        # 调试面板
        self.debug_panel.draw(screen)
    
def run_main_menu(screen, combat_status=None, in_combat=False, ling_shi_amount=0, ling_shi_wallet=None):
    """运行主菜单界面，返回下一个要进入的界面名称"""
    menu = MainMenu(screen.get_width(), screen.get_height())
    menu.in_combat = in_combat
    menu.ling_shi_wallet = ling_shi_wallet
    menu.ling_shi_amount = ling_shi_amount
    if ling_shi_wallet:
        menu.debug_panel.set_ling_shi_wallet(ling_shi_wallet)
    clock = pygame.time.Clock()

    from character_panel import _update_cultivation

    while menu.running:
        try:
            _update_cultivation()
            events = pygame.event.get()
            result = menu.handle_events(events)
            menu.update()
            menu.draw(screen)
            
            # 绘制战斗状态指示器
            if combat_status:
                from combat_renderer import draw_combat_status_indicator
                font_path = menu.font_manager.config["font"]["primary"]
                draw_combat_status_indicator(screen, font_path, combat_status)
            
            # 绘制灵石 - 放在设置按钮左边
            from ling_shi_renderer import draw_ling_shi_count
            draw_ling_shi_count(screen, menu.ling_shi_amount, x=menu.settings_button_rect.left - 15)
            
            pygame.display.flip()
            clock.tick(60)

            if result:
                print(f"[DEBUG] run_main_menu returning: {result}")
                return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[ERROR] 主菜单循环异常: {e}")

    return "quit"
