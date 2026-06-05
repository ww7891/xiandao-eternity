"""
从精灵表中提取单个角色精灵图
"""

import pygame
import os

def extract_sprites_from_sheet(sheet_path, output_dir, frame_size=(32, 32), 
                              start_x=0, start_y=0, rows=1, cols=1, 
                              prefix="sprite", offset_x=0, offset_y=0):
    """
    从精灵表中提取指定区域的精灵图
    
    参数:
        sheet_path: 精灵表文件路径
        output_dir: 输出目录
        frame_size: 每个精灵的尺寸 (宽, 高)
        start_x, start_y: 起始坐标
        rows, cols: 行数和列数
        prefix: 输出文件前缀
        offset_x, offset_y: 每个精灵之间的间隔
    """
    pygame.init()
    
    # 加载精灵表
    sheet = pygame.image.load(sheet_path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    
    print(f"精灵表尺寸: {sheet_width}x{sheet_height}")
    print(f"帧尺寸: {frame_size[0]}x{frame_size[1]}")
    print(f"提取区域: ({start_x}, {start_y}) 到 ({start_x + cols * (frame_size[0] + offset_x)}, {start_y + rows * (frame_size[1] + offset_y)})")
    
    os.makedirs(output_dir, exist_ok=True)
    extracted_files = []
    
    # 提取每个精灵
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (frame_size[0] + offset_x)
            y = start_y + row * (frame_size[1] + offset_y)
            
            # 检查是否超出边界
            if x + frame_size[0] > sheet_width or y + frame_size[1] > sheet_height:
                print(f"警告: 位置 ({x}, {y}) 超出边界")
                continue
            
            # 创建新表面并复制精灵
            sprite = pygame.Surface(frame_size, pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (x, y, frame_size[0], frame_size[1]))
            
            # 保存文件
            filename = f"{prefix}_{row}_{col}.png"
            filepath = os.path.join(output_dir, filename)
            pygame.image.save(sprite, filepath)
            extracted_files.append(filepath)
            
            print(f"提取: {filename} ({x}, {y})")
    
    print(f"\n共提取了 {len(extracted_files)} 个精灵图")
    return extracted_files

def extract_player_sprites():
    """提取玩家角色精灵图"""
    output_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(output_dir, "spritesheet_original.png")
    
    if not os.path.exists(sheet_path):
        print(f"错误: 找不到精灵表文件 {sheet_path}")
        return []
    
    # 从精灵表中提取适合的角色
    # 根据观察，第1行第0列看起来像战士/剑修
    # 第2行第0列看起来像法师
    # 第3行第0列看起来像盗贼/刀修
    
    extracted = []
    
    # 剑修 (第1行第0列)
    sword_sprites = extract_sprites_from_sheet(
        sheet_path, output_dir,
        frame_size=(32, 32),
        start_x=0, start_y=32,  # 第1行 (0-based)
        rows=1, cols=1,
        prefix="player_sword"
    )
    if sword_sprites:
        # 重命名为标准文件名
        old_path = sword_sprites[0]
        new_path = os.path.join(output_dir, "player_sword_idle.png")
        os.rename(old_path, new_path)
        extracted.append(new_path)
        print(f"重命名为: {os.path.basename(new_path)}")
    
    # 法修 (第2行第0列)
    mage_sprites = extract_sprites_from_sheet(
        sheet_path, output_dir,
        frame_size=(32, 32),
        start_x=0, start_y=64,  # 第2行
        rows=1, cols=1,
        prefix="player_mage"
    )
    if mage_sprites:
        old_path = mage_sprites[0]
        new_path = os.path.join(output_dir, "player_mage_idle.png")
        os.rename(old_path, new_path)
        extracted.append(new_path)
        print(f"重命名为: {os.path.basename(new_path)}")
    
    # 刀修 (第3行第0列)
    blade_sprites = extract_sprites_from_sheet(
        sheet_path, output_dir,
        frame_size=(32, 32),
        start_x=0, start_y=96,  # 第3行
        rows=1, cols=1,
        prefix="player_blade"
    )
    if blade_sprites:
        old_path = blade_sprites[0]
        new_path = os.path.join(output_dir, "player_blade_idle.png")
        os.rename(old_path, new_path)
        extracted.append(new_path)
        print(f"重命名为: {os.path.basename(new_path)}")
    
    # 提取一些敌人精灵
    # 第4-6行看起来像怪物/敌人
    enemy_types = ["mob", "elite", "boss"]
    for i, enemy_type in enumerate(enemy_types):
        enemy_sprites = extract_sprites_from_sheet(
            sheet_path, output_dir,
            frame_size=(32, 32),
            start_x=32 * i, start_y=128 + 32 * i,  # 不同位置
            rows=1, cols=1,
            prefix=f"enemy_{enemy_type}"
        )
        if enemy_sprites:
            old_path = enemy_sprites[0]
            new_path = os.path.join(output_dir, f"enemy_{enemy_type}.png")
            os.rename(old_path, new_path)
            extracted.append(new_path)
            print(f"重命名为: {os.path.basename(new_path)}")
    
    return extracted

def analyze_sprite_sheet():
    """分析精灵表结构"""
    output_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(output_dir, "spritesheet_original.png")
    
    if not os.path.exists(sheet_path):
        print(f"错误: 找不到精灵表文件 {sheet_path}")
        return
    
    pygame.init()
    sheet = pygame.image.load(sheet_path).convert_alpha()
    width, height = sheet.get_size()
    
    print("=" * 80)
    print("精灵表分析报告")
    print("=" * 80)
    print(f"文件: {os.path.basename(sheet_path)}")
    print(f"尺寸: {width}x{height} 像素")
    print(f"建议帧尺寸: 32x32 像素")
    print(f"网格: {width//32}列 x {height//32}行")
    print()
    
    print("角色分布建议:")
    print("第0行 (y=0-31): 各种站立姿势")
    print("第1行 (y=32-63): 战士/剑修角色")
    print("第2行 (y=64-95): 法师角色")
    print("第3行 (y=96-127): 盗贼/刺客角色")
    print("第4-7行 (y=128-255): 怪物/敌人角色")
    print("第8-11行 (y=256-383): 更多敌人/NPC")
    print("第12-15行 (y=384-511): 状态图标/物品")
    print()
    
    print("提取建议命令:")
    print("python extract_sprites.py --extract-all")
    print("python extract_sprites.py --extract-player")
    print("python extract_sprites.py --analyze")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='精灵表提取工具')
    parser.add_argument('--extract-all', action='store_true', help='提取所有角色精灵')
    parser.add_argument('--extract-player', action='store_true', help='只提取玩家角色')
    parser.add_argument('--analyze', action='store_true', help='分析精灵表结构')
    parser.add_argument('--custom', action='store_true', help='自定义提取')
    parser.add_argument('--sheet', type=str, default='spritesheet_original.png', help='精灵表文件名')
    parser.add_argument('--output', type=str, default='.', help='输出目录')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_sprite_sheet()
    elif args.extract_all or args.extract_player:
        extract_player_sprites()
        print("\n提取完成！现在可以运行游戏测试精灵图效果。")
        print("运行: cd ..\\.. && python game_main.py")
    elif args.custom:
        print("自定义提取功能待实现")
        print("使用 --extract-all 自动提取推荐角色")
    else:
        print("精灵表提取工具")
        print("用法:")
        print("  python extract_sprites.py --analyze          # 分析精灵表")
        print("  python extract_sprites.py --extract-player   # 提取玩家角色")
        print("  python extract_sprites.py --extract-all      # 提取所有角色")
        print("\n已下载的精灵表:")
        print("  - spritesheet_original.png (20个32x32角色)")
        print("  - soldier_original.png (士兵角色)")

if __name__ == "__main__":
    main()