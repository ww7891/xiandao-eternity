"""
仙道永恒 - 战斗界面
进入战斗界面（当前为空框架，后续实现战斗逻辑）
"""

import pygame
from font_utils import FontManager

CONFIG_PATH = "config.json"


class BattlePanel:
    """战斗界面"""
    
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
        
        # 战斗场景选择按钮
        self.scene_buttons = []
        self.create_scene_buttons()
        
        # 场景按钮悬停
        self.hovered_scene = None
        
        # 背景
        self.background = self.create_background()
        
        # 粒子效果
        self.particles = []
        self.init_particles()
        
        print("✅ 战斗界面初始化完成")
    
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
    
    def init_particles(self):
        """初始化战斗粒子"""
        import random
        for _ in range(30):
            self.particles.append({
                "x": random.randint(0, self.screen_width),
                "y": random.randint(0, self.screen_height),
                "size": random.randint(1, 4),
                "speed_x": random.uniform(-1, 1),
                "speed_y": random.uniform(-2, -0.5),
                "alpha": random.randint(50, 150),
                "color": random.choice([(255, 200, 100), (200, 150, 255), (100, 200, 255)])
            })
    
    def create_scene_buttons(self):
        """创建战斗场景选择按钮"""
        scenes = [
            {"id": "forest", "name": "灵兽森林", "desc": "适合初入修仙的修士", "level": "1-5级"},
            {"id": "cave", "name": "妖兽洞穴", "desc": "有一定实力的修士可挑战", "level": "5-10级"},
            {"id": "ruins", "name": "远古遗迹", "desc": "危机与机遇并存", "level": "10-15级"},
            {"id": "peak", "name": "仙山绝顶", "desc": "高手云集的战场", "level": "15-20级"},
        ]
        
        button_width = 250
        button_height = 160
        total_width = len(scenes) * button_width + (len(scenes) - 1) * 20
        start_x = (self.screen_width - total_width) // 2
        start_y = 280
        
        for i, scene in enumerate(scenes):
            x = start_x + i * (button_width + 20)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            self.scene_buttons.append({
                "rect": rect,
                "scene": scene
            })
    
    def update_particles(self):
        """更新粒子"""
        import random
        for p in self.particles:
            p["x"] += p["speed_x"]
            p["y"] += p["speed_y"]
            
            if p["y"] < -10 or p["x"] < -10 or p["x"] > self.screen_width + 10:
                p["x"] = random.randint(0, self.screen_width)
                p["y"] = self.screen_height + 10
    
    def draw_scene_button(self, screen, button, is_hovered):
        """绘制场景按钮"""
        colors = self.config["colors"]
        rect = button["rect"]
        scene = button["scene"]
        
        # 根据悬停状态选择颜色
        if is_hovered:
            bg_color = colors["button_hover"]
            border_color = colors["accent_cyan"]
            scale = 1.05
        else:
            bg_color = colors["button_normal"]
            border_color = colors["border_color"]
            scale = 1.0
        
        # 计算缩放后的矩形
        scaled_w = int(rect.width * scale)
        scaled_h = int(rect.height * scale)
        scaled_x = rect.centerx - scaled_w // 2
        scaled_y = rect.centery - scaled_h // 2
        
        # 背景
        pygame.draw.rect(screen, bg_color, (scaled_x, scaled_y, scaled_w, scaled_h), 
                        border_radius=12)
        pygame.draw.rect(screen, border_color, (scaled_x, scaled_y, scaled_w, scaled_h), 
                        width=2, border_radius=12)
        
        # 等级标记
        level_surf = self.font_manager.render_text(scene["level"], "small", colors["accent_cyan"])
        level_x = scaled_x + (scaled_w - level_surf.get_width()) // 2
        screen.blit(level_surf, (level_x, scaled_y + 20))
        
        # 场景名称
        name_surf = self.font_manager.render_text(scene["name"], "medium", colors["title_gold"])
        name_x = scaled_x + (scaled_w - name_surf.get_width()) // 2
        screen.blit(name_surf, (name_x, scaled_y + 55))
        
        # 描述
        desc_lines = self.font_manager.render_multiline(
            scene["desc"], "small", colors["text_secondary"], max_width=scaled_w - 30
        )
        desc_y = scaled_y + 100
        for i, line_surf in enumerate(desc_lines[:2]):
            line_x = scaled_x + (scaled_w - line_surf.get_width()) // 2
            screen.blit(line_surf, (line_x, desc_y + i * 22))
        
        # 高光效果
        if is_hovered:
            highlight = pygame.Surface((scaled_w - 4, scaled_h // 2), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 20), 
                           (0, 0, scaled_w - 4, scaled_h // 2), border_radius=10)
            screen.blit(highlight, (scaled_x + 2, scaled_y + 2))
    
    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新返回按钮悬停状态
        self.return_hovered = self.return_button.collidepoint(mouse_pos)
        
        # 更新场景按钮悬停
        self.hovered_scene = None
        for button in self.scene_buttons:
            if button["rect"].collidepoint(mouse_pos):
                self.hovered_scene = button["scene"]["id"]
                break
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.return_button.collidepoint(mouse_pos):
                        return "goto_main_menu"
                    
                    # 场景选择（暂时只是提示）
                    for button in self.scene_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            print(f"选择了场景: {button['scene']['name']}")
                            break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
        
        return None
    
    def update(self):
        """更新界面"""
        self.update_particles()
    
    def draw(self, screen):
        """绘制界面"""
        colors = self.config["colors"]
        
        # 背景
        screen.blit(self.background, (0, 0))
        
        # 粒子效果
        for p in self.particles:
            alpha = min(255, p["alpha"])
            pygame.draw.circle(screen, (*p["color"], alpha), 
                             (int(p["x"]), int(p["y"])), p["size"])
        
        # 页面标题
        title_surf = self.font_manager.render_text("战斗", "large", colors["title_gold"])
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
        
        # 副标题
        subtitle = "选择战斗场景"
        sub_surf = self.font_manager.render_text(subtitle, "medium", colors["accent_cyan"])
        sub_x = (self.screen_width - sub_surf.get_width()) // 2
        screen.blit(sub_surf, (sub_x, 200))
        
        # 分割线
        line_y = 245
        line_width = 300
        line_x = (self.screen_width - line_width) // 2
        pygame.draw.line(screen, (*colors["border_color"], 150), 
                        (line_x, line_y), (line_x + line_width, line_y), 1)
        
        # 绘制场景选择按钮
        for button in self.scene_buttons:
            is_hovered = (self.hovered_scene == button["scene"]["id"])
            self.draw_scene_button(screen, button, is_hovered)
        
        # 战斗界面提示（占位）
        placeholder_texts = [
            "战斗系统开发中...",
            "敬请期待弹幕射击+修仙肉鸽玩法！",
        ]
        
        for i, text in enumerate(placeholder_texts):
            text_surf = self.font_manager.render_text(text, "small", colors["text_secondary"])
            text_x = (self.screen_width - text_surf.get_width()) // 2
            screen.blit(text_surf, (text_x, 500 + i * 25))
        
        # 底部提示
        hint = "按 ESC 返回主菜单"
        hint_surf = self.font_manager.render_text(hint, "small", colors["text_secondary"])
        hint_x = (self.screen_width - hint_surf.get_width()) // 2
        screen.blit(hint_surf, (hint_x, self.screen_height - 35))


def run_battle_panel(screen):
    """运行战斗界面"""
    panel = BattlePanel(screen.get_width(), screen.get_height())
    clock = pygame.time.Clock()
    
    while panel.running:
        events = pygame.event.get()
        result = panel.handle_events(events)
        panel.update()
        panel.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        
        if result:
            return result
    
    return "quit"
