"""
《仙道永恒》游戏设置界面
作者：游戏开发团队
日期：2026-05-28
功能：设置界面，支持音量调节和游戏设置
"""

import pygame
import sys
import os
import math
from font_utils import FontManager
from settings_manager import get_settings_manager

# 配置路径
CONFIG_PATH = "config.json"


class SettingsScreen:
    """设置界面类"""
    
    def __init__(self, screen_width=1280, screen_height=720, music_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)
        
        import json
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.colors = self.config.get("colors", {})
        
        # 设置管理器
        self.settings_manager = get_settings_manager()
        
        # 音乐管理器（用于实时预览音量变化）
        self.music_manager = music_manager
        
        # 当前音量值
        self.main_volume = self.settings_manager.get_main_menu_volume()
        self.battle_volume = self.settings_manager.get_battle_volume()
        self.master_volume = self.settings_manager.get_master_volume()
        
        # 滑块状态
        self.main_slider_dragging = False
        self.battle_slider_dragging = False
        self.master_slider_dragging = False
        
        # 按钮状态
        self.apply_hovered = False
        self.cancel_hovered = False
        self.save_hovered = False
        self.reset_hovered = False
        
        # 返回状态
        self.return_hovered = False
        self.return_to_title_hovered = False
        
        # 运行状态
        self.running = True
        self.next_state = None
        
        # 临时设置（用于取消时恢复）
        self.original_settings = {
            "main_volume": self.main_volume,
            "battle_volume": self.battle_volume,
            "master_volume": self.master_volume
        }
        
        # 创建水墨背景
        self.create_background()
        
        print("✅ 设置界面初始化完成")
    
    def create_background(self):
        """创建水墨山水背景"""
        self.background = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.background.fill((245, 240, 228))
        
        # 天空渐变
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(220 + 25 * min(ratio, 0.5) * 2)
            g = int(215 + 30 * min(ratio, 0.5) * 2)
            b = int(205 + 40 * min(ratio, 0.5) * 2)
            if ratio > 0.5:
                r = int(245 - 60 * (ratio - 0.5))
                g = int(245 - 55 * (ratio - 0.5))
                b = int(245 - 40 * (ratio - 0.5))
            pygame.draw.line(self.background, (r, g, b), (0, y), (self.screen_width, y))
        
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
                y = self.screen_height * sy - peak * self.screen_height * 0.22
                y += math.sin(t * 4) * 18
                pts.append((x, y))
            pts.append((self.screen_width, self.screen_height))
            pts.append((0, self.screen_height))
            pygame.draw.polygon(self.background, (*color, 170), pts)
    
    def draw_title(self, screen):
        """绘制标题"""
        title = "设置"
        title_surf = self.font_manager.render_text(title, "title", (50, 40, 25), 60)
        screen.blit(title_surf, ((self.screen_width - title_surf.get_width()) // 2, 30))
        
        # 标题下划线
        line_x = (self.screen_width - 400) // 2
        pygame.draw.line(screen, (100, 90, 75, 100), 
                        (line_x, 100), (line_x + 400, 100), 2)
    
    def draw_volume_slider(self, screen, x, y, label, current_value, dragging=False):
        """
        绘制音量滑块
        
        参数:
            screen: 目标Surface
            x, y: 位置
            label: 标签文本
            current_value: 当前值 (0-100)
            dragging: 是否正在拖动
        """
        slider_width = 400
        slider_height = 30
        handle_radius = 12
        
        # 滑块背景
        slider_rect = pygame.Rect(x, y, slider_width, slider_height)
        pygame.draw.rect(screen, (220, 215, 200, 180), slider_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 70, 55, 200), slider_rect, width=1, border_radius=4)
        
        # 填充部分（表示当前音量）
        fill_width = int(slider_width * current_value / 100)
        fill_rect = pygame.Rect(x, y, fill_width, slider_height)
        if dragging:
            fill_color = (180, 160, 100, 200)  # 拖动时高亮
        else:
            fill_color = (150, 130, 80, 180)
        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)
        
        # 滑块手柄
        handle_x = x + fill_width
        handle_color = (200, 180, 120) if dragging else (180, 160, 100)
        pygame.draw.circle(screen, handle_color, (handle_x, y + slider_height // 2), handle_radius)
        pygame.draw.circle(screen, (80, 70, 55), (handle_x, y + slider_height // 2), handle_radius, 1)
        
        # 标签
        label_surf = self.font_manager.render_text(label, "medium", (50, 40, 25), 28)
        screen.blit(label_surf, (x - label_surf.get_width() - 20, y - 5))
        
        # 数值显示
        value_text = f"{current_value}%"
        value_surf = self.font_manager.render_text(value_text, "medium", (40, 30, 18), 24)
        screen.blit(value_surf, (x + slider_width + 20, y - 3))
        
        return slider_rect
    
    def draw_button(self, screen, x, y, width, height, text, hovered=False, disabled=False):
        """
        绘制按钮
        
        参数:
            screen: 目标Surface
            x, y: 位置
            width, height: 尺寸
            text: 按钮文本
            hovered: 是否悬停
            disabled: 是否禁用
        """
        button_rect = pygame.Rect(x, y, width, height)
        
        if disabled:
            # 禁用状态
            pygame.draw.rect(screen, (120, 110, 100, 180), button_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 90, 80, 200), button_rect, width=1, border_radius=8)
            text_color = (150, 140, 130)
        elif hovered:
            # 悬停状态
            pygame.draw.rect(screen, (180, 160, 100, 220), button_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 180, 120, 240), button_rect, width=2, border_radius=8)
            text_color = (40, 30, 18)
        else:
            # 正常状态
            pygame.draw.rect(screen, (150, 130, 80, 200), button_rect, border_radius=8)
            pygame.draw.rect(screen, (180, 160, 100, 220), button_rect, width=1, border_radius=8)
            text_color = (40, 30, 18)
        
        # 按钮文字
        text_surf = self.font_manager.render_text(text, "medium", text_color, 24)
        screen.blit(text_surf, 
                   (x + (width - text_surf.get_width()) // 2,
                    y + (height - text_surf.get_height()) // 2))
        
        return button_rect
    
    def draw(self, screen):
        """绘制设置界面"""
        # 背景
        screen.blit(self.background, (0, 0))
        
        # 标题
        self.draw_title(screen)
        
        # 音频设置标题
        audio_title = self.font_manager.render_text("音频设置", "large", (50, 40, 25), 36)
        screen.blit(audio_title, (self.screen_width // 2 - audio_title.get_width() // 2, 140))
        
        # 主界面音量滑块
        main_slider_y = 200
        self.main_slider_rect = self.draw_volume_slider(
            screen, self.screen_width // 2 - 200, main_slider_y,
            "主界面音量", self.main_volume, self.main_slider_dragging
        )
        
        # 战斗界面音量滑块
        battle_slider_y = 260
        self.battle_slider_rect = self.draw_volume_slider(
            screen, self.screen_width // 2 - 200, battle_slider_y,
            "战斗音量", self.battle_volume, self.battle_slider_dragging
        )
        
        # 主音量滑块
        master_slider_y = 320
        self.master_slider_rect = self.draw_volume_slider(
            screen, self.screen_width // 2 - 200, master_slider_y,
            "主音量", self.master_volume, self.master_slider_dragging
        )
        
        # 按钮区域
        button_y = 400
        button_width = 140
        button_height = 50
        button_gap = 20
        
        # 应用按钮
        apply_x = self.screen_width // 2 - (button_width * 2 + button_gap * 1.5)
        self.apply_button_rect = self.draw_button(
            screen, apply_x, button_y, button_width, button_height,
            "应用", self.apply_hovered
        )
        
        # 保存按钮
        save_x = self.screen_width // 2 - (button_width + button_gap * 0.5)
        self.save_button_rect = self.draw_button(
            screen, save_x, button_y, button_width, button_height,
            "保存", self.save_hovered
        )
        
        # 重置按钮
        reset_x = self.screen_width // 2 + button_gap * 0.5
        self.reset_button_rect = self.draw_button(
            screen, reset_x, button_y, button_width, button_height,
            "重置", self.reset_hovered
        )
        
        # 取消按钮
        cancel_x = self.screen_width // 2 + (button_width + button_gap * 1.5)
        self.cancel_button_rect = self.draw_button(
            screen, cancel_x, button_y, button_width, button_height,
            "取消", self.cancel_hovered
        )
        
        # 返回主菜单按钮
        return_y = 480
        return_width = 200
        return_height = 60
        self.return_button_rect = self.draw_button(
            screen, self.screen_width // 2 - return_width // 2, return_y,
            return_width, return_height, "返回主菜单", self.return_hovered
        )
        
        # 返回标题界面按钮
        return_title_y = 550
        self.return_title_button_rect = self.draw_button(
            screen, self.screen_width // 2 - return_width // 2, return_title_y,
            return_width, return_height, "返回标题界面", self.return_to_title_hovered
        )
        
        # 当前设置状态提示
        status_y = 630
        status_text = "提示：应用按钮立即生效，保存按钮将设置保存到文件"
        status_surf = self.font_manager.render_text(status_text, "small", (100, 90, 75), 18)
        screen.blit(status_surf, (self.screen_width // 2 - status_surf.get_width() // 2, status_y))
    
    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新悬停状态（首次循环 draw 尚未执行时跳过）
        if hasattr(self, 'apply_button_rect'):
            self.apply_hovered = self.apply_button_rect.collidepoint(mouse_pos)
            self.save_hovered = self.save_button_rect.collidepoint(mouse_pos)
            self.reset_hovered = self.reset_button_rect.collidepoint(mouse_pos)
            self.cancel_hovered = self.cancel_button_rect.collidepoint(mouse_pos)
            self.return_hovered = self.return_button_rect.collidepoint(mouse_pos)
            self.return_to_title_hovered = self.return_title_button_rect.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            # 鼠标按下
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查滑块拖动
                if hasattr(self, 'main_slider_rect') and self.main_slider_rect.collidepoint(mouse_pos):
                    self.main_slider_dragging = True
                elif hasattr(self, 'battle_slider_rect') and self.battle_slider_rect.collidepoint(mouse_pos):
                    self.battle_slider_dragging = True
                elif hasattr(self, 'master_slider_rect') and self.master_slider_rect.collidepoint(mouse_pos):
                    self.master_slider_dragging = True
                
                # 检查按钮点击
                if hasattr(self, 'apply_button_rect') and self.apply_button_rect.collidepoint(mouse_pos):
                    self.apply_settings()
                elif hasattr(self, 'save_button_rect') and self.save_button_rect.collidepoint(mouse_pos):
                    self.save_settings()
                elif hasattr(self, 'reset_button_rect') and self.reset_button_rect.collidepoint(mouse_pos):
                    self.reset_settings()
                elif hasattr(self, 'cancel_button_rect') and self.cancel_button_rect.collidepoint(mouse_pos):
                    self.cancel_settings()
                elif hasattr(self, 'return_button_rect') and self.return_button_rect.collidepoint(mouse_pos):
                    return "goto_main_menu"
                elif hasattr(self, 'return_title_button_rect') and self.return_title_button_rect.collidepoint(mouse_pos):
                    return "goto_title_screen"
            
            # 鼠标释放
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.main_slider_dragging = False
                self.battle_slider_dragging = False
                self.master_slider_dragging = False
            
            # 鼠标移动（滑块拖动）
            if event.type == pygame.MOUSEMOTION:
                if self.main_slider_dragging and hasattr(self, 'main_slider_rect'):
                    self.update_slider_value(self.main_slider_rect, mouse_pos[0], "main")
                elif self.battle_slider_dragging and hasattr(self, 'battle_slider_rect'):
                    self.update_slider_value(self.battle_slider_rect, mouse_pos[0], "battle")
                elif self.master_slider_dragging and hasattr(self, 'master_slider_rect'):
                    self.update_slider_value(self.master_slider_rect, mouse_pos[0], "master")
            
            # 键盘事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
                elif event.key == pygame.K_RETURN:
                    self.apply_settings()
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_settings()
        
        return None
    
    def update_slider_value(self, slider_rect, mouse_x, slider_type):
        """更新滑块值"""
        # 计算相对位置
        relative_x = mouse_x - slider_rect.left
        relative_x = max(0, min(slider_rect.width, relative_x))
        
        # 计算百分比
        percentage = int(relative_x / slider_rect.width * 100)
        
        # 更新对应音量
        if slider_type == "main":
            self.main_volume = percentage
        elif slider_type == "battle":
            self.battle_volume = percentage
        elif slider_type == "master":
            self.master_volume = percentage
        
        # 实时预览音量
        self.apply_settings(preview=True)
    
    def apply_settings(self, preview=False):
        """应用设置（立即生效）"""
        # 更新设置管理器
        self.settings_manager.set_main_menu_volume(self.main_volume)
        self.settings_manager.set_battle_volume(self.battle_volume)
        self.settings_manager.set_master_volume(self.master_volume)
        
        if not preview:
            print(f"✅ 设置已应用 - 主界面: {self.main_volume}%, 战斗: {self.battle_volume}%, 主音量: {self.master_volume}%")
        
        # 如果提供了音乐管理器，实时更新音量
        if self.music_manager:
            # 计算当前界面的归一化音量
            # 这里假设当前在设置界面，属于主菜单界面类型
            normalized_volume = self.settings_manager.get_normalized_volume("settings")
            self.music_manager.set_volume(normalized_volume)
    
    def save_settings(self):
        """保存设置到文件"""
        # 先应用设置
        self.apply_settings()
        
        # 保存到文件
        if self.settings_manager.save_settings():
            print("✅ 设置已保存到文件")
        else:
            print("❌ 设置保存失败")
    
    def reset_settings(self):
        """重置为默认设置"""
        self.main_volume = 50
        self.battle_volume = 50
        self.master_volume = 100
        
        print("✅ 设置已重置为默认值")
    
    def cancel_settings(self):
        """取消更改，恢复原始设置"""
        self.main_volume = self.original_settings["main_volume"]
        self.battle_volume = self.original_settings["battle_volume"]
        self.master_volume = self.original_settings["master_volume"]
        
        print("✅ 设置已取消，恢复原始值")
    
    def update(self):
        """更新界面状态"""
        pass


def run_settings_screen(screen, music_manager=None, ling_shi_amount=0):
    """运行设置界面，返回下一个要进入的界面名称"""
    settings = SettingsScreen(screen.get_width(), screen.get_height(), music_manager)
    clock = pygame.time.Clock()
    
    while settings.running:
        events = pygame.event.get()
        settings.draw(screen)  # 先绘制，确保按钮 rect 存在
        result = settings.handle_events(events)
        settings.update()
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        
        pygame.display.flip()
        clock.tick(60)
        
        if result:
            return result
    
    return "quit"


# 导入math模块
# import math  # 已移至文件顶部