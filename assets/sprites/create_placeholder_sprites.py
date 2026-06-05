"""
创建占位符精灵图
在没有真实素材时，创建简单的占位符图片
"""

import pygame
import os

def create_color_sprite(size, color, border_color=(255, 255, 255), text=""):
    """创建纯色精灵图"""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # 填充主色
    pygame.draw.rect(surface, color, (0, 0, size[0], size[1]))
    
    # 边框
    pygame.draw.rect(surface, border_color, (0, 0, size[0], size[1]), 2)
    
    # 文字标签
    if text:
        try:
            font = pygame.font.Font(None, 12)
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
            surface.blit(text_surf, text_rect)
        except:
            pass
            
    return surface

def create_player_placeholder(profession, size=(32, 32)):
    """创建玩家角色占位符"""
    colors = {
        "sword": (100, 180, 255),    # 蓝色 - 剑修
        "mage": (180, 220, 255),     # 浅蓝 - 法修
        "blade": (255, 200, 100)     # 橙色 - 刀修
    }
    
    color = colors.get(profession, (200, 200, 200))
    return create_color_sprite(size, color, text=profession.upper())

def create_enemy_placeholder(enemy_type, size=(32, 32)):
    """创建敌人占位符"""
    colors = {
        "mob": (150, 50, 50),        # 红色 - 小怪
        "elite": (200, 150, 50),     # 金色 - 精英
        "boss": (100, 50, 150)       # 紫色 - Boss
    }
    
    color = colors.get(enemy_type, (150, 150, 150))
    return create_color_sprite(size, color, text=enemy_type.upper())

def create_effect_placeholder(effect_type, size=(48, 48)):
    """创建特效占位符"""
    colors = {
        "sword": (100, 150, 255),    # 蓝色 - 剑光
        "magic": (200, 100, 255),    # 紫色 - 魔法
        "blade": (255, 150, 50)      # 橙色 - 刀气
    }
    
    color = colors.get(effect_type, (200, 200, 200))
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # 中心圆形
    pygame.draw.circle(surface, color, (size[0]//2, size[1]//2), size[0]//3)
    
    # 外发光
    for i in range(3, 0, -1):
        alpha = 50 // i
        glow_color = (*color[:3], alpha)
        pygame.draw.circle(surface, glow_color, (size[0]//2, size[1]//2), 
                          size[0]//3 + i*2, 1)
    
    return surface

def save_sprite(surface, filename, output_dir):
    """保存精灵图到文件"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    pygame.image.save(surface, filepath)
    print(f"已保存: {filepath}")
    return filepath

def create_all_placeholders(output_dir="."):
    """创建所有占位符精灵图"""
    pygame.init()
    
    # 玩家角色
    player_sprites = {
        "player_sword_idle.png": create_player_placeholder("sword"),
        "player_mage_idle.png": create_player_placeholder("mage"),
        "player_blade_idle.png": create_player_placeholder("blade"),
    }
    
    # 敌人
    enemy_sprites = {
        "enemy_mob.png": create_enemy_placeholder("mob", size=(20, 20)),
        "enemy_elite.png": create_enemy_placeholder("elite", size=(36, 36)),
        "enemy_boss.png": create_enemy_placeholder("boss", size=(64, 64)),
    }
    
    # 特效
    effect_sprites = {
        "sword_attack.png": create_effect_placeholder("sword"),
        "magic_attack.png": create_effect_placeholder("magic"),
        "blade_attack.png": create_effect_placeholder("blade"),
    }
    
    # 保存所有精灵图
    saved_files = []
    
    for filename, sprite in player_sprites.items():
        saved_files.append(save_sprite(sprite, filename, output_dir))
        
    for filename, sprite in enemy_sprites.items():
        saved_files.append(save_sprite(sprite, filename, output_dir))
        
    for filename, sprite in effect_sprites.items():
        saved_files.append(save_sprite(sprite, filename, output_dir))
    
    print(f"\n共创建了 {len(saved_files)} 个占位符精灵图")
    print("这些文件可以在下载真实素材前作为临时替代")
    
    return saved_files

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='创建占位符精灵图')
    parser.add_argument('--output', type=str, default='.', help='输出目录')
    parser.add_argument('--create-all', action='store_true', help='创建所有占位符')
    
    args = parser.parse_args()
    
    if args.create_all:
        create_all_placeholders(args.output)
    else:
        print("占位符精灵图创建工具")
        print("用法: python create_placeholder_sprites.py --create-all --output ./sprites")
        print("\n这将创建以下文件:")
        print("  - player_sword_idle.png, player_mage_idle.png, player_blade_idle.png")
        print("  - enemy_mob.png, enemy_elite.png, enemy_boss.png")
        print("  - sword_attack.png, magic_attack.png, blade_attack.png")

if __name__ == "__main__":
    main()