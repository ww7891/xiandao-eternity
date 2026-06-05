"""
仙道永恒 - 装备界面
显示当前装备、装备槽位
"""

import pygame
from font_utils import FontManager

CONFIG_PATH = "config.json"


class EquipmentPanel:
    """装备界面"""
    
    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)
        
        # 加载配置
        self.load_config()
        
        # 界面状态
        self.running = True
        self.next_state = None
        
        # 返回按钮
        self.return_button = pygame.Rect(30, 30, 120, 40)
        self.return_hovered = False
        
        # 装备数据（初始全部为空槽位）
        self.equipment_slots = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "accessory1": None,
            "accessory2": None,
            "shoes": None,
            "gloves": None,
            "belt": None,
        }
        
        # 背包中的装备（初始为空）
        self.backpack_equipment = []
        
        # 选中的装备
        self.selected_slot = None
        self.selected_backpack_item = None
        
        # 背景
        self.background = self.create_background()
        
        print("✅ 装备界面初始化完成")
    
    def load_config(self):
        """加载配置"""
        import json
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "colors": {
                    "background": [20, 20, 40],
                    "panel_background": [30, 30, 60, 220],
                    "title_gold": [255, 215, 0],
                    "text_primary": [240, 240, 240],
                    "text_secondary": [180, 180, 200],
                    "button_normal": [60, 60, 120],
                    "button_hover": [100, 80, 180],
                    "button_text": [255, 255, 255],
                    "accent_cyan": [0, 200, 200],
                    "accent_purple": [160, 80, 255],
                    "border_color": [100, 100, 160]
                }
            }
    
    def create_background(self):
        """创建背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        colors = self.config["colors"]
        
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(colors["background"][0] * (1 - ratio * 0.3))
            g = int(colors["background"][1] * (1 - ratio * 0.2))
            b = int(colors["background"][2] * (1 + ratio * 0.3))
            pygame.draw.line(bg, (max(r, 0), max(g, 0), min(b, 255)), 
                           (0, y), (self.screen_width, y))
        
        return bg
    
    def get_quality_color(self, quality):
        """根据品质获取颜色"""
        colors = self.config["colors"]
        if quality == 1:
            return colors["text_secondary"]  # 普通
        elif quality == 2:
            return (100, 200, 100)  # 绿色
        elif quality == 3:
            return (100, 150, 255)  # 蓝色
        elif quality == 4:
            return (200, 100, 255)  # 紫色
        else:
            return colors["title_gold"]  # 金色
    
    def get_slot_position(self, slot_name):
        """获取装备槽位位置"""
        positions = {
            "weapon": (self.screen_width // 2 - 200, 150),
            "helmet": (self.screen_width // 2, 100),
            "armor": (self.screen_width // 2, 200),
            "gloves": (self.screen_width // 2 - 100, 300),
            "belt": (self.screen_width // 2, 300),
            "shoes": (self.screen_width // 2 + 100, 300),
            "accessory1": (self.screen_width // 2 - 150, 400),
            "accessory2": (self.screen_width // 2 + 150, 400),
        }
        return positions.get(slot_name, (0, 0))
    
    def get_slot_name_cn(self, slot_name):
        """获取槽位中文名称"""
        names = {
            "weapon": "武器",
            "armor": "防具",
            "helmet": "头盔",
            "gloves": "手套",
            "belt": "腰带",
            "shoes": "鞋子",
            "accessory1": "饰品1",
            "accessory2": "饰品2",
        }
        return names.get(slot_name, slot_name)
    
    def draw_equipment_slot(self, screen, x, y, slot_name, equipment, is_selected):
        """绘制装备槽位"""
        colors = self.config["colors"]
        slot_size = 100
        
        # 槽位背景
        if is_selected:
            bg_color = colors["button_hover"]
            border_color = colors["accent_cyan"]
        else:
            bg_color = colors["button_normal"]
            border_color = colors["border_color"]
        
        pygame.draw.rect(screen, bg_color, (x, y, slot_size, slot_size), border_radius=12)
        pygame.draw.rect(screen, border_color, (x, y, slot_size, slot_size), 
                        width=2, border_radius=12)
        
        # 槽位名称
        slot_cn = self.get_slot_name_cn(slot_name)
        name_surf = self.font_manager.render_text(slot_cn, "small", colors["text_secondary"])
        name_x = x + (slot_size - name_surf.get_width()) // 2
        screen.blit(name_surf, (name_x, y - 25))
        
        if equipment:
            # 品质边框
            quality_color = self.get_quality_color(equipment["quality"])
            pygame.draw.rect(screen, quality_color, (x, y, slot_size, slot_size), 
                           width=3, border_radius=12)
            
            # 装备图标（用文字代替）
            icon_text = equipment["type"][0]  # 取第一个字
            icon_surf = self.font_manager.render_text(icon_text, "medium", quality_color)
            icon_x = x + (slot_size - icon_surf.get_width()) // 2
            icon_y = y + (slot_size - icon_surf.get_height()) // 2
            screen.blit(icon_surf, (icon_x, icon_y))
        else:
            # 空槽位
            empty_text = self.font_manager.render_text("空", "medium", colors["text_secondary"])
            empty_x = x + (slot_size - empty_text.get_width()) // 2
            empty_y = y + (slot_size - empty_text.get_height()) // 2
            screen.blit(empty_text, (empty_x, empty_y))
    
    def draw_equipment_detail(self, screen, x, y, width, height, equipment, slot_name=None):
        """绘制装备详情"""
        colors = self.config["colors"]
        
        if not equipment:
            return
        
        # 详情面板
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, colors["panel_background"], 
                        (0, 0, width, height), border_radius=12)
        pygame.draw.rect(panel_surf, (*colors["border_color"], 200), 
                        (0, 0, width, height), width=2, border_radius=12)
        screen.blit(panel_surf, (x, y))
        
        # 品质颜色
        quality_color = self.get_quality_color(equipment["quality"])
        
        # 装备名称
        name_surf = self.font_manager.render_text(equipment["name"], "medium", quality_color)
        screen.blit(name_surf, (x + 20, y + 20))
        
        # 类型和槽位
        type_text = f"类型：{equipment['type']}"
        if slot_name:
            type_text += f"（{self.get_slot_name_cn(slot_name)}）"
        
        type_surf = self.font_manager.render_text(type_text, "small", colors["text_primary"])
        screen.blit(type_surf, (x + 20, y + 70))
        
        # 品质
        quality_text = f"品质：{'★' * equipment['quality']}"
        quality_surf = self.font_manager.render_text(quality_text, "small", quality_color)
        screen.blit(quality_surf, (x + 20, y + 100))
        
        # 属性
        attr_y = y + 130
        for key, value in equipment.items():
            if key not in ["name", "type", "quality", "description", "id"]:
                attr_name = {
                    "attack": "攻击力",
                    "defense": "防御力",
                    "speed": "速度",
                    "hp_bonus": "生命加成",
                    "mp_bonus": "法力加成",
                    "spirit": "灵力"
                }.get(key, key)
                
                attr_text = f"{attr_name}: +{value}"
                attr_color = colors["accent_cyan"] if value > 0 else colors["text_secondary"]
                attr_surf = self.font_manager.render_text(attr_text, "small", attr_color)
                screen.blit(attr_surf, (x + 20, attr_y))
                attr_y += 30
        
        # 描述
        if "description" in equipment:
            desc_y = attr_y + 10
            desc_lines = self.font_manager.render_multiline(
                equipment["description"], "small", colors["text_secondary"], 
                max_width=width - 40
            )
            for i, line_surf in enumerate(desc_lines):
                screen.blit(line_surf, (x + 20, desc_y + i * 30))
        
        # 操作按钮
        if slot_name:
            unequip_btn = pygame.Rect(x + width - 140, y + height - 50, 120, 40)
            unequip_hovered = unequip_btn.collidepoint(pygame.mouse.get_pos())
            unequip_color = colors["button_hover"] if unequip_hovered else colors["button_normal"]
            
            pygame.draw.rect(screen, unequip_color, unequip_btn, border_radius=8)
            pygame.draw.rect(screen, colors["border_color"], unequip_btn, width=1, border_radius=8)
            unequip_text = self.font_manager.render_text("卸下", "small", colors["button_text"])
            unequip_x = unequip_btn.centerx - unequip_text.get_width() // 2
            unequip_y = unequip_btn.centery - unequip_text.get_height() // 2
            screen.blit(unequip_text, (unequip_x, unequip_y))
    
    def draw_backpack_item(self, screen, x, y, width, height, item, is_selected):
        """绘制背包中的装备"""
        colors = self.config["colors"]
        
        # 物品背景
        if is_selected:
            bg_color = colors["button_hover"]
            border_color = colors["accent_cyan"]
        else:
            bg_color = colors["button_normal"]
            border_color = colors["border_color"]
        
        pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(screen, border_color, (x, y, width, height), 
                        width=1, border_radius=8)
        
        if item:
            # 品质边框
            quality_color = self.get_quality_color(item["quality"])
            pygame.draw.rect(screen, quality_color, (x, y, width, height), 
                           width=2, border_radius=8)
            
            # 装备名称
            name_surf = self.font_manager.render_text(item["name"], "small", colors["text_primary"])
            name_x = x + (width - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, y + 10))
            
            # 装备类型
            type_surf = self.font_manager.render_text(item["type"], "small", colors["text_secondary"])
            type_x = x + (width - type_surf.get_width()) // 2
            screen.blit(type_surf, (type_x, y + height - 30))
        else:
            # 空位
            empty_text = self.font_manager.render_text("空", "small", colors["text_secondary"])
            empty_x = x + (width - empty_text.get_width()) // 2
            empty_y = y + (height - empty_text.get_height()) // 2
            screen.blit(empty_text, (empty_x, empty_y))
    
    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新返回按钮悬停状态
        self.return_hovered = self.return_button.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 返回按钮
                    if self.return_button.collidepoint(mouse_pos):
                        return "goto_main_menu"
                    
                    # 装备槽位点击
                    for slot_name, equipment in self.equipment_slots.items():
                        x, y = self.get_slot_position(slot_name)
                        slot_rect = pygame.Rect(x, y, 100, 100)
                        if slot_rect.collidepoint(mouse_pos):
                            self.selected_slot = slot_name
                            self.selected_backpack_item = None
                            break
                    
                    # 背包装备点击
                    start_x = 40
                    start_y = 500
                    item_width = 120
                    item_height = 60
                    items_per_row = 8
                    
                    for i, item in enumerate(self.backpack_equipment):
                        row = i // items_per_row
                        col = i % items_per_row
                        
                        item_x = start_x + col * (item_width + 10)
                        item_y = start_y + row * (item_height + 10)
                        
                        item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
                        if item_rect.collidepoint(mouse_pos):
                            self.selected_backpack_item = item
                            self.selected_slot = None
                            break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
        
        return None
    
    def update(self):
        """更新界面"""
        pass
    
    def draw(self, screen):
        """绘制界面"""
        colors = self.config["colors"]
        
        # 背景
        screen.blit(self.background, (0, 0))
        
        # 页面标题
        title_surf = self.font_manager.render_text("装备", "large", colors["title_gold"])
        title_x = (self.screen_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, 30))
        
        # 返回按钮
        btn_color = colors["button_hover"] if self.return_hovered else colors["button_normal"]
        pygame.draw.rect(screen, btn_color, self.return_button, border_radius=8)
        pygame.draw.rect(screen, colors["border_color"], self.return_button, 
                        width=1, border_radius=8)
        return_text = self.font_manager.render_text("← 返回", "small", colors["button_text"])
        return_x = self.return_button.centerx - return_text.get_width() // 2
        return_y = self.return_button.centery - return_text.get_height() // 2
        screen.blit(return_text, (return_x, return_y))
        
        # 角色形象区域标题
        char_title = self.font_manager.render_text("装备槽位", "medium", colors["accent_cyan"])
        screen.blit(char_title, (self.screen_width // 2 - char_title.get_width() // 2, 60))
        
        # 绘制装备槽位
        for slot_name, equipment in self.equipment_slots.items():
            x, y = self.get_slot_position(slot_name)
            is_selected = (self.selected_slot == slot_name)
            self.draw_equipment_slot(screen, x, y, slot_name, equipment, is_selected)
        
        # 绘制角色形象（简单表示）
        center_x = self.screen_width // 2
        center_y = 250
        pygame.draw.circle(screen, colors["text_primary"], (center_x, center_y), 30, 2)
        
        # 装备详情
        if self.selected_slot and self.equipment_slots[self.selected_slot]:
            detail_x = 40
            detail_y = 120
            detail_width = 400
            detail_height = 200
            self.draw_equipment_detail(screen, detail_x, detail_y, detail_width, 
                                     detail_height, self.equipment_slots[self.selected_slot],
                                     self.selected_slot)
        
        # 背包装备详情
        if self.selected_backpack_item:
            detail_x = 40
            detail_y = 120
            detail_width = 400
            detail_height = 200
            self.draw_equipment_detail(screen, detail_x, detail_y, detail_width, 
                                     detail_height, self.selected_backpack_item)
        
        # 背包区域标题
        backpack_title = self.font_manager.render_text("背包装备", "medium", colors["accent_purple"])
        screen.blit(backpack_title, (40, 460))
        
        # 绘制背包中的装备
        start_x = 40
        start_y = 500
        item_width = 120
        item_height = 60
        items_per_row = 8
        
        for i, item in enumerate(self.backpack_equipment):
            row = i // items_per_row
            col = i % items_per_row
            
            item_x = start_x + col * (item_width + 10)
            item_y = start_y + row * (item_height + 10)
            
            is_selected = (self.selected_backpack_item and 
                          self.selected_backpack_item["id"] == item["id"])
            self.draw_backpack_item(screen, item_x, item_y, item_width, item_height, 
                                   item, is_selected)
        
        # 属性统计
        total_attack = 0
        total_defense = 0
        total_speed = 0
        total_hp_bonus = 0
        total_mp_bonus = 0
        
        for equipment in self.equipment_slots.values():
            if equipment:
                total_attack += equipment.get("attack", 0)
                total_defense += equipment.get("defense", 0)
                total_speed += equipment.get("speed", 0)
                total_hp_bonus += equipment.get("hp_bonus", 0)
                total_mp_bonus += equipment.get("mp_bonus", 0)
        
        # 属性统计面板
        stats_x = self.screen_width - 300
        stats_y = 120
        stats_width = 260
        stats_height = 200
        
        stats_surf = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        pygame.draw.rect(stats_surf, colors["panel_background"], 
                        (0, 0, stats_width, stats_height), border_radius=12)
        pygame.draw.rect(stats_surf, (*colors["border_color"], 200), 
                        (0, 0, stats_width, stats_height), width=2, border_radius=12)
        screen.blit(stats_surf, (stats_x, stats_y))
        
        stats_title = self.font_manager.render_text("装备加成", "medium", colors["accent_cyan"])
        screen.blit(stats_title, (stats_x + 20, stats_y + 20))
        
        stats_lines = [
            f"攻击力: +{total_attack}",
            f"防御力: +{total_defense}",
            f"速度: +{total_speed}",
            f"生命加成: +{total_hp_bonus}",
            f"法力加成: +{total_mp_bonus}",
        ]
        
        for i, line in enumerate(stats_lines):
            line_surf = self.font_manager.render_text(line, "small", colors["text_primary"])
            screen.blit(line_surf, (stats_x + 20, stats_y + 60 + i * 30))
        
        # 底部提示
        hint = "点击装备查看详情，按 ESC 返回主菜单"
        hint_surf = self.font_manager.render_text(hint, "small", colors["text_secondary"])
        hint_x = (self.screen_width - hint_surf.get_width()) // 2
        screen.blit(hint_surf, (hint_x, self.screen_height - 35))


def run_equipment_panel(screen, combat_status=None, ling_shi_amount=0):
    """运行装备界面"""
    panel = EquipmentPanel(screen.get_width(), screen.get_height())
    clock = pygame.time.Clock()
    
    while panel.running:
        events = pygame.event.get()
        result = panel.handle_events(events)
        panel.update()
        panel.draw(screen)
        
        # 绘制战斗状态指示器
        if combat_status:
            from combat_renderer import draw_combat_status_indicator
            font_path = panel.font_manager.config["font"]["primary"]
            draw_combat_status_indicator(screen, font_path, combat_status)
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        
        pygame.display.flip()
        clock.tick(60)
        
        if result:
            return result
    
    return "quit"
