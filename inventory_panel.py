"""
仙道永恒 - 背包界面
显示物品、材料、丹药等
"""

import pygame
from font_utils import FontManager

CONFIG_PATH = "config.json"


class InventoryPanel:
    """背包界面"""
    
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
        
        # 标签页
        self.tabs = ["全部", "材料", "丹药", "符箓", "法宝"]
        self.active_tab = 0
        
        # 物品数据（初始背包为空）
        self.items = []
        
        # 分页
        self.page = 0
        self.items_per_page = 12
        
        # 选中的物品
        self.selected_item = None
        
        # 背景
        self.background = self.create_background()
        
        print("✅ 背包界面初始化完成")
    
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
    
    def get_filtered_items(self):
        """获取过滤后的物品"""
        if self.active_tab == 0:
            return self.items
        else:
            tab_name = self.tabs[self.active_tab]
            return [item for item in self.items if item["type"] == tab_name]
    
    def draw_item_slot(self, screen, x, y, width, height, item, is_selected):
        """绘制物品格子"""
        colors = self.config["colors"]
        
        # 背景颜色
        if is_selected:
            bg_color = colors["button_hover"]
            border_color = colors["accent_cyan"]
        else:
            bg_color = colors["button_normal"]
            border_color = colors["border_color"]
        
        # 物品格子
        pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(screen, border_color, (x, y, width, height), 
                        width=1, border_radius=8)
        
        if item:
            # 品质边框
            quality_color = self.get_quality_color(item["quality"])
            pygame.draw.rect(screen, quality_color, (x, y, width, height), 
                           width=2, border_radius=8)
            
            # 物品名称
            name_surf = self.font_manager.render_text(
                item["name"], "small", colors["text_primary"]
            )
            name_x = x + (width - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, y + 10))
            
            # 物品类型
            type_surf = self.font_manager.render_text(
                item["type"], "small", colors["text_secondary"]
            )
            type_x = x + (width - type_surf.get_width()) // 2
            screen.blit(type_surf, (type_x, y + height - 50))
            
            # 数量
            if item["count"] > 1:
                count_surf = self.font_manager.render_text(
                    f"x{item['count']}", "small", colors["accent_cyan"]
                )
                count_x = x + width - count_surf.get_width() - 8
                screen.blit(count_surf, (count_x, y + 8))
        else:
            # 空格子
            empty_text = self.font_manager.render_text(
                "空", "small", colors["text_secondary"]
            )
            empty_x = x + (width - empty_text.get_width()) // 2
            empty_y = y + (height - empty_text.get_height()) // 2
            screen.blit(empty_text, (empty_x, empty_y))
    
    def draw_item_detail(self, screen, x, y, width, height, item):
        """绘制物品详情"""
        colors = self.config["colors"]
        
        if not item:
            return
        
        # 详情面板
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, colors["panel_background"], 
                        (0, 0, width, height), border_radius=12)
        pygame.draw.rect(panel_surf, (*colors["border_color"], 200), 
                        (0, 0, width, height), width=2, border_radius=12)
        screen.blit(panel_surf, (x, y))
        
        # 品质颜色
        quality_color = self.get_quality_color(item["quality"])
        
        # 物品名称
        name_surf = self.font_manager.render_text(item["name"], "medium", quality_color)
        screen.blit(name_surf, (x + 20, y + 20))
        
        # 类型和品质
        type_text = f"类型：{item['type']}"
        type_surf = self.font_manager.render_text(type_text, "small", colors["text_primary"])
        screen.blit(type_surf, (x + 20, y + 70))
        
        quality_text = f"品质：{'★' * item['quality']}"
        quality_surf = self.font_manager.render_text(quality_text, "small", quality_color)
        screen.blit(quality_surf, (x + 20, y + 100))
        
        # 数量
        count_text = f"数量：{item['count']}"
        count_surf = self.font_manager.render_text(count_text, "small", colors["accent_cyan"])
        screen.blit(count_surf, (x + 20, y + 130))
        
        # 描述
        desc_y = y + 170
        desc = "这是物品的描述信息，可以在这里显示物品的详细说明和使用方法。"
        desc_lines = self.font_manager.render_multiline(
            desc, "small", colors["text_secondary"], max_width=width - 40
        )
        for i, line_surf in enumerate(desc_lines):
            screen.blit(line_surf, (x + 20, desc_y + i * 30))
        
        # 使用按钮
        use_btn = pygame.Rect(x + width - 140, y + height - 50, 120, 40)
        use_hovered = use_btn.collidepoint(pygame.mouse.get_pos())
        use_color = colors["button_hover"] if use_hovered else colors["button_normal"]
        
        pygame.draw.rect(screen, use_color, use_btn, border_radius=8)
        pygame.draw.rect(screen, colors["border_color"], use_btn, width=1, border_radius=8)
        use_text = self.font_manager.render_text("使用", "small", colors["button_text"])
        use_x = use_btn.centerx - use_text.get_width() // 2
        use_y = use_btn.centery - use_text.get_height() // 2
        screen.blit(use_text, (use_x, use_y))
    
    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新返回按钮悬停状态
        self.return_hovered = self.return_button.collidepoint(mouse_pos)
        
        # 更新标签页悬停
        tab_width = 100
        tab_start_x = (self.screen_width - len(self.tabs) * tab_width) // 2
        tab_hovered = -1
        
        for i in range(len(self.tabs)):
            tab_rect = pygame.Rect(tab_start_x + i * tab_width, 100, tab_width, 40)
            if tab_rect.collidepoint(mouse_pos):
                tab_hovered = i
                break
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 返回按钮
                    if self.return_button.collidepoint(mouse_pos):
                        return "goto_main_menu"
                    
                    # 标签页点击
                    if tab_hovered >= 0:
                        self.active_tab = tab_hovered
                        self.page = 0
                        self.selected_item = None
                    
                    # 物品格子点击
                    filtered_items = self.get_filtered_items()
                    start_x = 40
                    start_y = 160
                    slot_size = 160
                    slots_per_row = 6
                    
                    for i, item in enumerate(filtered_items):
                        if i >= self.items_per_page:
                            break
                        
                        row = i // slots_per_row
                        col = i % slots_per_row
                        
                        slot_x = start_x + col * (slot_size + 10)
                        slot_y = start_y + row * (slot_size + 10)
                        
                        slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
                        if slot_rect.collidepoint(mouse_pos):
                            self.selected_item = item
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
        title_surf = self.font_manager.render_text("背包", "large", colors["title_gold"])
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
        
        # 标签页
        tab_width = 100
        tab_start_x = (self.screen_width - len(self.tabs) * tab_width) // 2
        
        for i, tab_name in enumerate(self.tabs):
            tab_rect = pygame.Rect(tab_start_x + i * tab_width, 100, tab_width, 40)
            is_active = (i == self.active_tab)
            
            # 标签背景
            if is_active:
                tab_color = colors["accent_purple"]
                text_color = colors["button_text"]
            else:
                tab_color = colors["button_normal"]
                text_color = colors["text_primary"]
            
            pygame.draw.rect(screen, tab_color, tab_rect, border_radius=8)
            pygame.draw.rect(screen, colors["border_color"], tab_rect, 
                            width=1, border_radius=8)
            
            # 标签文字
            tab_surf = self.font_manager.render_text(tab_name, "small", text_color)
            tab_x = tab_rect.centerx - tab_surf.get_width() // 2
            tab_y = tab_rect.centery - tab_surf.get_height() // 2
            screen.blit(tab_surf, (tab_x, tab_y))
        
        # 物品格子区域标题
        area_title = "物品列表"
        if self.active_tab > 0:
            area_title = f"{self.tabs[self.active_tab]}列表"
        
        area_surf = self.font_manager.render_text(area_title, "medium", colors["accent_cyan"])
        screen.blit(area_surf, (40, 120))
        
        # 绘制物品格子
        filtered_items = self.get_filtered_items()
        start_x = 40
        start_y = 160
        slot_size = 160
        slots_per_row = 6
        
        for i, item in enumerate(filtered_items):
            if i >= self.items_per_page:
                break
            
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = start_x + col * (slot_size + 10)
            slot_y = start_y + row * (slot_size + 10)
            
            is_selected = (self.selected_item and self.selected_item["id"] == item["id"])
            self.draw_item_slot(screen, slot_x, slot_y, slot_size, slot_size, 
                               item, is_selected)
        
        # 如果物品不足一页，补全空格子
        total_slots = min(len(filtered_items), self.items_per_page)
        empty_slots = self.items_per_page - total_slots
        
        for i in range(empty_slots):
            slot_index = total_slots + i
            row = slot_index // slots_per_row
            col = slot_index % slots_per_row
            
            slot_x = start_x + col * (slot_size + 10)
            slot_y = start_y + row * (slot_size + 10)
            
            self.draw_item_slot(screen, slot_x, slot_y, slot_size, slot_size, 
                               None, False)
        
        # 物品详情面板
        if self.selected_item:
            detail_x = 40
            detail_y = 500
            detail_width = 400
            detail_height = 200
            self.draw_item_detail(screen, detail_x, detail_y, detail_width, 
                                 detail_height, self.selected_item)
        
        # 统计信息
        total_items = len(filtered_items)
        stats_text = f"共 {total_items} 件物品"
        stats_surf = self.font_manager.render_text(stats_text, "small", colors["text_secondary"])
        screen.blit(stats_surf, (self.screen_width - stats_surf.get_width() - 40, 120))
        
        # 底部提示
        hint = "点击物品查看详情，按 ESC 返回主菜单"
        hint_surf = self.font_manager.render_text(hint, "small", colors["text_secondary"])
        hint_x = (self.screen_width - hint_surf.get_width()) // 2
        screen.blit(hint_surf, (hint_x, self.screen_height - 35))


def run_inventory_panel(screen, combat_status=None, ling_shi_amount=0):
    """运行背包界面"""
    panel = InventoryPanel(screen.get_width(), screen.get_height())
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
