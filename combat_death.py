"""
角色死亡界面
当玩家在后台战斗中死亡时显示
"""

import pygame
import math
import random
import os

def draw_death_background(screen, width, height, time):
    """绘制死亡背景"""
    # 深色渐变背景
    for y in range(0, height, 2):
        ratio = y / height
        r = int(20 + 10 * ratio)
        g = int(10 + 5 * ratio)
        b = int(30 + 15 * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
        if y + 1 < height:
            pygame.draw.line(screen, (r, g, b), (0, y + 1), (width, y + 1))
    
    # 破碎的符文
    for i in range(8):
        x = width * (0.1 + 0.8 * (i / 7))
        y = height * 0.3 + 30 * math.sin(time * 0.5 + i * 0.8)
        size = 20 + 10 * math.sin(time * 0.3 + i * 1.2)
        alpha = 30 + int(15 * math.sin(time * 0.4 + i * 0.5))
        
        # 破碎的圆形
        for j in range(3):
            a = time * 0.2 + i * 0.5 + j * 1.2
            r = size * (0.3 + 0.2 * j)
            ox = x + math.cos(a) * r * 0.5
            oy = y + math.sin(a) * r * 0.5
            pygame.draw.circle(screen, (100, 20, 20, alpha), (int(ox), int(oy)), int(r * 0.7), 1)
    
    # 血色雾气
    for i in range(12):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = 50 + 30 * math.sin(time * 0.1 + i * 0.3)
        alpha = 10 + int(5 * math.sin(time * 0.2 + i * 0.4))
        pygame.draw.circle(screen, (80, 10, 10, alpha), (x, y), int(r))

def draw_rip_effect(screen, width, height, time):
    """绘制RIP效果"""
    center_x, center_y = width // 2, height // 2 - 50
    
    # 墓碑轮廓
    tomb_w, tomb_h = 180, 240
    tomb_x, tomb_y = center_x - tomb_w // 2, center_y - tomb_h // 2
    
    # 墓碑主体
    pts = [
        (tomb_x, tomb_y + tomb_h),
        (tomb_x + tomb_w // 3, tomb_y + tomb_h * 0.7),
        (tomb_x + tomb_w * 2 // 3, tomb_y + tomb_h * 0.7),
        (tomb_x + tomb_w, tomb_y + tomb_h),
        (tomb_x + tomb_w, tomb_y + tomb_h * 0.3),
        (tomb_x + tomb_w * 0.7, tomb_y),
        (tomb_x + tomb_w * 0.3, tomb_y),
        (tomb_x, tomb_y + tomb_h * 0.3),
    ]
    pygame.draw.polygon(screen, (60, 50, 40), pts)
    pygame.draw.polygon(screen, (100, 80, 60), pts, 2)
    
    # 墓碑裂纹
    for _ in range(8):
        start_x = tomb_x + random.randint(20, tomb_w - 20)
        start_y = tomb_y + random.randint(20, int(tomb_h * 0.6))
        end_x = start_x + random.randint(-30, 30)
        end_y = start_y + random.randint(20, 60)
        pygame.draw.line(screen, (40, 30, 20), (start_x, start_y), (end_x, end_y), 1)
    
    # 墓碑文字 "RIP"
    rip_font = pygame.font.Font(None, 48)
    rip_text = rip_font.render("RIP", True, (180, 150, 120))
    screen.blit(rip_text, (center_x - rip_text.get_width() // 2, tomb_y + 40))
    
    # 飘落的樱花/花瓣（死亡特效）
    if hasattr(draw_rip_effect, "petals"):
        petals = draw_rip_effect.petals
    else:
        petals = []
        for _ in range(15):
            petals.append({
                'x': random.randint(0, width),
                'y': random.randint(-100, 0),
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(3, 8),
                'color': (random.randint(180, 220), random.randint(80, 120), random.randint(100, 140), 150),
                'sway': random.uniform(0, math.pi * 2),
            })
        draw_rip_effect.petals = petals
    
    for p in petals:
        p['y'] += p['speed']
        p['x'] += math.sin(time * 0.5 + p['sway']) * 0.5
        if p['y'] > height:
            p['y'] = -10
            p['x'] = random.randint(0, width)
        pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])

def run_combat_death(screen, drops, map_id, ling_shi_amount=0):
    """运行角色死亡界面"""
    width, height = screen.get_width(), screen.get_height()
    clock = pygame.time.Clock()
    font_manager = None
    
    # 尝试获取字体管理器
    try:
        from font_utils import FontManager
        font_manager = FontManager()
    except:
        # 降级：使用系统字体
        title_font = pygame.font.Font(None, 64)
        text_font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
    
    start_time = pygame.time.get_ticks()
    running = True
    
    # 掉落物显示
    drop_items = []
    for drop in drops:
        if isinstance(drop, dict):
            drop_items.append(f"{drop.get('name', '未知')} x{drop.get('count', 1)}")
        else:
            drop_items.append(str(drop))
    
    while running:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000.0
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "main_menu"
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 点击任意位置继续
                    return "main_menu"
        
        # 绘制背景
        draw_death_background(screen, width, height, elapsed)
        
        # 绘制RIP效果
        draw_rip_effect(screen, width, height, elapsed)
        
        # 标题文字
        if font_manager:
            title = font_manager.render_text("身死道消", "title", (180, 60, 60), 72)
            subtitle = font_manager.render_text("魂魄归天，修为尽散", "medium", (150, 100, 100), 36)
        else:
            title = title_font.render("身死道消", True, (180, 60, 60))
            subtitle = text_font.render("魂魄归天，修为尽散", True, (150, 100, 100))
        
        screen.blit(title, ((width - title.get_width()) // 2, 80))
        screen.blit(subtitle, ((width - subtitle.get_width()) // 2, 160))
        
        # 掉落物显示
        drop_y = height // 2 + 100
        if drop_items:
            if font_manager:
                drop_title = font_manager.render_text("战利品", "medium", (180, 150, 120), 32)
            else:
                drop_title = text_font.render("战利品", True, (180, 150, 120))
            screen.blit(drop_title, ((width - drop_title.get_width()) // 2, drop_y))
            
            for i, item in enumerate(drop_items):
                if font_manager:
                    item_text = font_manager.render_text(f"· {item}", "small", (160, 140, 110), 24)
                else:
                    item_text = small_font.render(f"· {item}", True, (160, 140, 110))
                screen.blit(item_text, ((width - item_text.get_width()) // 2, drop_y + 40 + i * 30))
        else:
            if font_manager:
                no_drop = font_manager.render_text("身无长物，唯余遗憾", "medium", (140, 120, 100), 28)
            else:
                no_drop = text_font.render("身无长物，唯余遗憾", True, (140, 120, 100))
            screen.blit(no_drop, ((width - no_drop.get_width()) // 2, drop_y + 20))
        
        # 提示文字
        hint_y = height - 100
        if font_manager:
            hint1 = font_manager.render_text("按 R 键重试", "small", (120, 100, 80), 24)
            hint2 = font_manager.render_text("按 空格/ESC 返回主菜单", "small", (120, 100, 80), 24)
        else:
            hint1 = small_font.render("按 R 键重试", True, (120, 100, 80))
            hint2 = small_font.render("按 空格/ESC 返回主菜单", True, (120, 100, 80))
        
        screen.blit(hint1, ((width - hint1.get_width()) // 2, hint_y))
        screen.blit(hint2, ((width - hint2.get_width()) // 2, hint_y + 30))
        
        # 闪烁的"点击继续"
        if int(elapsed * 2) % 2 == 0:
            if font_manager:
                click_hint = font_manager.render_text("点击任意位置继续", "small", (180, 100, 100), 22)
            else:
                click_hint = small_font.render("点击任意位置继续", True, (180, 100, 100))
            screen.blit(click_hint, ((width - click_hint.get_width()) // 2, hint_y + 70))
        
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        pygame.display.flip()
        clock.tick(60)
    
    return "main_menu"