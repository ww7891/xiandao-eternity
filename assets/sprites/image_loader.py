"""
精灵图加载器
用于加载和缓存游戏中的角色精灵图
"""

import pygame
import os

class SpriteLoader:
    """精灵图加载和管理类"""
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.cache = {}
        
    def load_image(self, filename, scale=None):
        """加载图片并可选缩放"""
        cache_key = filename
        if scale:
            cache_key = f"{filename}_{scale[0]}x{scale[1]}"
            
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            filepath = os.path.join(self.base_path, filename)
            image = pygame.image.load(filepath).convert_alpha()
            
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.cache[cache_key] = image
            return image
        except Exception as e:
            print(f"加载图片失败 {filename}: {e}")
            # 返回一个占位符
            return self._create_placeholder(scale or (32, 32))
    
    def load_spritesheet(self, filename, frame_size, scale=None):
        """从精灵表加载多帧动画"""
        spritesheet = self.load_image(filename, scale)
        if not spritesheet:
            return []
            
        sheet_width, sheet_height = spritesheet.get_size()
        frame_width, frame_height = frame_size
        
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(spritesheet, (0, 0), (x, y, frame_width, frame_height))
                frames.append(frame)
                
        return frames
    
    def _create_placeholder(self, size):
        """创建占位符图片"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        w, h = size
        # 绘制一个简单的圆形占位符
        pygame.draw.rect(surface, (255, 0, 0, 128), (0, 0, w, h))
        pygame.draw.rect(surface, (255, 255, 255, 200), (0, 0, w, h), 1)
        # 绘制十字
        pygame.draw.line(surface, (255, 255, 255), (w//2, 0), (w//2, h), 1)
        pygame.draw.line(surface, (255, 255, 255), (0, h//2), (w, h//2), 1)
        return surface
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()


# 全局精灵加载器实例
_sprite_loader = None

def get_sprite_loader(base_path=None):
    """获取全局精灵加载器"""
    global _sprite_loader
    if _sprite_loader is None and base_path:
        _sprite_loader = SpriteLoader(base_path)
    return _sprite_loader


# 预定义的精灵图路径常量
class SpritePaths:
    """精灵图路径常量（修仙风格增强版精灵）"""
    
    # 玩家角色（48x48增强版，修仙配色）
    PLAYER_SWORD_IDLE = "player_sword_idle_48.png"
    PLAYER_SWORD_WALK = "player_sword_idle_48.png"    # 暂无行走帧，复用idle
    PLAYER_MAGE_IDLE = "player_mage_idle_48.png"
    PLAYER_MAGE_WALK = "player_mage_idle_48.png"
    PLAYER_BLADE_IDLE = "player_blade_idle_48.png"
    PLAYER_BLADE_WALK = "player_blade_idle_48.png"
    
    # 敌人（修仙风格配色）
    ENEMY_MOB = "enemy_mob_enhanced.png"
    ENEMY_ELITE = "enemy_elite_enhanced.png"
    ENEMY_BOSS = "enemy_boss_enhanced.png"
    
    # 攻击特效
    SWORD_ATTACK = "sword_attack.png"
    MAGIC_ATTACK = "magic_attack.png"
    BLADE_ATTACK = "blade_attack.png"
    
    # 其他
    HP_BAR = "hp_bar.png"
    EXP_BAR = "exp_bar.png"


# 精灵图尺寸常量（匹配增强版精灵实际尺寸）
class SpriteSizes:
    """精灵图尺寸常量"""
    
    PLAYER = (48, 48)          # 玩家角色尺寸（增强版48px）
    ENEMY_MOB = (32, 32)       # 小怪尺寸
    ENEMY_ELITE = (48, 48)     # 精英尺寸
    ENEMY_BOSS = (64, 64)      # Boss尺寸
    PROJECTILE = (16, 16)      # 弹道尺寸
    EFFECT = (48, 48)          # 特效尺寸