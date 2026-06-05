"""
字体加载工具类 - 解决Pygame中文显示问题
"""
import pygame
import os
import json

class FontManager:
    """字体管理器，确保中文正确显示"""
    
    def __init__(self, config_path=None):
        """初始化字体管理器"""
        pygame.font.init()
        self.fonts = {}
        self.config = {}
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            self.load_default_config()
    
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 配置文件加载成功: {config_path}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            self.load_default_config()
    
    def load_default_config(self):
        """加载默认配置"""
        self.config = {
            "font": {
                "primary": "C:/Windows/Fonts/simhei.ttf",
                "fallback": "C:/Windows/Fonts/simsunb.ttf",
                "title_size": 72,
                "large_size": 48,
                "medium_size": 32,
                "small_size": 24,
                "button_size": 28
            }
        }
        print("⚠️ 使用默认字体配置")
    
    def get_font(self, font_type="medium", size=None):
        """
        获取字体对象
        
        Args:
            font_type: 字体类型 (title/large/medium/small/button)
            size: 字体大小，如果为None则使用配置中的大小
        
        Returns:
            pygame.font.Font 对象
        """
        # 确定字体大小
        if size is None:
            size_key = f"{font_type}_size"
            if size_key in self.config.get("font", {}):
                size = self.config["font"][size_key]
            else:
                size = self.config["font"]["medium_size"]
        
        # 确定字体文件路径
        font_path = self.config["font"]["primary"]
        
        # 检查字体文件是否存在
        if not os.path.exists(font_path):
            print(f"⚠️ 主字体文件不存在: {font_path}")
            font_path = self.config["font"]["fallback"]
            if not os.path.exists(font_path):
                print(f"⚠️ 备用字体文件也不存在: {font_path}")
                print("⚠️ 使用Pygame默认字体")
                return pygame.font.SysFont(None, size)
        
        # 创建字体缓存键
        cache_key = f"{font_path}_{size}"
        
        # 如果字体已缓存，直接返回
        if cache_key in self.fonts:
            return self.fonts[cache_key]
        
        # 创建新字体对象
        try:
            font = pygame.font.Font(font_path, size)
            self.fonts[cache_key] = font
            return font
        except Exception as e:
            print(f"❌ 字体加载失败 {font_path}: {e}")
            # 回退到系统字体
            return pygame.font.SysFont(None, size)
    
    def render_text(self, text, font_type="medium", color=(255, 255, 255), size=None, antialias=True):
        """
        渲染文本为Surface
        
        Args:
            text: 要渲染的文本
            font_type: 字体类型
            color: 文本颜色 (R,G,B)
            size: 字体大小
            antialias: 是否抗锯齿
        
        Returns:
            渲染后的Surface对象
        """
        font = self.get_font(font_type, size)
        return font.render(text, antialias, color)
    
    def render_multiline(self, text, font_type="medium", color=(255, 255, 255), 
                         line_spacing=1.2, max_width=None, size=None):
        """
        渲染多行文本
        
        Args:
            text: 文本内容
            font_type: 字体类型
            color: 文本颜色
            line_spacing: 行间距倍数
            max_width: 最大宽度，超过则自动换行
            size: 字体大小
        
        Returns:
            包含所有行Surface的列表
        """
        font = self.get_font(font_type, size)
        lines = []
        
        if max_width:
            # 自动换行逻辑
            words = text.split(' ')
            current_line = ''
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                test_width = font.size(test_line)[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        else:
            # 按换行符分割
            lines = text.split('\n')
        
        # 渲染每一行
        surfaces = []
        for line in lines:
            if line.strip():  # 跳过空行
                surface = font.render(line, True, color)
                surfaces.append(surface)
        
        return surfaces

# 全局字体管理器实例
_font_manager = None

def get_font_manager(config_path=None):
    """获取全局字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager(config_path)
    return _font_manager

def render_text(text, font_type="medium", color=(255, 255, 255), size=None):
    """便捷函数：渲染文本"""
    return get_font_manager().render_text(text, font_type, color, size)

def render_multiline(text, font_type="medium", color=(255, 255, 255), 
                     line_spacing=1.2, max_width=None, size=None):
    """便捷函数：渲染多行文本"""
    return get_font_manager().render_multiline(text, font_type, color, 
                                               line_spacing, max_width, size)