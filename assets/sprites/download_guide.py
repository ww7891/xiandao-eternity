"""
精灵图下载指南脚本
提供直接下载链接和自动下载功能
"""

import os
import requests
import zipfile
import io

class SpriteDownloader:
    """精灵图下载器"""
    
    def __init__(self, download_dir):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
    def download_from_url(self, url, filename=None):
        """从URL下载文件"""
        try:
            print(f"正在下载: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            if not filename:
                # 从URL提取文件名
                if '?' in url:
                    url = url.split('?')[0]
                filename = os.path.basename(url)
                if not filename:
                    filename = "downloaded_file"
                    
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"下载完成: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return None
    
    def download_and_extract_zip(self, url, extract_dir=None):
        """下载并解压ZIP文件"""
        try:
            print(f"正在下载ZIP: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            if not extract_dir:
                extract_dir = self.download_dir
                
            # 在内存中解压
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(extract_dir)
                
            print(f"解压完成到: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            print(f"ZIP下载/解压失败 {url}: {e}")
            return None


# 推荐的免费精灵图资源
RECOMMENDED_RESOURCES = {
    "opengameart_32x32_rpg": {
        "name": "32x32 RPG Character Sprites",
        "url": "https://opengameart.org/sites/default/files/RPGCharacterSprites32x32.png",
        "description": "20个不同的32x32角色精灵，CC0许可证",
        "type": "image",
        "license": "CC0"
    },
    "opengameart_soldier": {
        "name": "32x35 Soldier Sprite",
        "url": "https://opengameart.org/sites/default/files/RPGSoldier32x32.png",
        "description": "士兵精灵图，包含跳跃动画",
        "type": "image",
        "license": "CC0"
    },
    "opengameart_fantasy_kit": {
        "name": "Fantasy RPG Sprite Kit",
        "url": "https://opengameart.org/sites/default/files/fantasy_rpg_sprite_kit.zip",
        "description": "幻想RPG精灵套件，包含战士、法师、弓箭手等",
        "type": "zip",
        "license": "CC0"
    },
    "itchio_topdown_pack": {
        "name": "Top-Down RPG Character Pack",
        "url": "https://itch.io/blog/888310/lust-sisters-",
        "description": "Itch.io上的俯视角RPG角色包（需要手动下载）",
        "type": "webpage",
        "license": "需查看具体许可证"
    }
}


def print_download_instructions():
    """打印下载指南"""
    print("=" * 80)
    print("修仙者角色精灵图下载指南")
    print("=" * 80)
    
    print("\n1. 自动下载（推荐）:")
    print("   运行以下命令下载推荐资源:")
    print("   python download_guide.py --download opengameart_32x32_rpg")
    print("   python download_guide.py --download opengameart_fantasy_kit")
    
    print("\n2. 手动下载链接:")
    for key, resource in RECOMMENDED_RESOURCES.items():
        print(f"\n   {resource['name']}:")
        print(f"   URL: {resource['url']}")
        print(f"   描述: {resource['description']}")
        print(f"   许可证: {resource['license']}")
        print(f"   类型: {resource['type']}")
    
    print("\n3. 其他资源网站:")
    print("   - OpenGameArt.org: https://opengameart.org/")
    print("   - Itch.io (免费资源): https://itch.io/game-assets/free")
    print("   - Kenney.nl: https://kenney.nl/assets")
    print("   - GameDevMarket.net (免费部分): https://www.gamedevmarket.net/category/free/")
    
    print("\n4. 修仙风格素材网站:")
    print("   - 千图网: https://www.58pic.com/")
    print("   - 觅知网: https://www.51miz.com/")
    print("   - 熊猫办公: https://www.tukuppt.com/")
    
    print("\n5. 文件命名规范:")
    print("   下载后请按以下规范重命名文件:")
    print("   - 玩家角色: player_职业_idle.png / player_职业_walk.png")
    print("   - 敌人: enemy_类型_编号.png")
    print("   - 特效: effect_名称.png")
    
    print("\n6. 许可证注意事项:")
    print("   - CC0: 可自由使用，无需署名")
    print("   - CC-BY: 需要署名原作者")
    print("   - 商业使用: 请仔细查看许可证条款")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='精灵图下载工具')
    parser.add_argument('--download', type=str, help='要下载的资源ID')
    parser.add_argument('--list', action='store_true', help='列出所有可用资源')
    parser.add_argument('--dir', type=str, default='.', help='下载目录')
    
    args = parser.parse_args()
    
    if args.list:
        print("可用资源列表:")
        for key, resource in RECOMMENDED_RESOURCES.items():
            print(f"  {key}: {resource['name']}")
        return
    
    if args.download:
        if args.download not in RECOMMENDED_RESOURCES:
            print(f"错误: 资源 '{args.download}' 不存在")
            print("使用 --list 查看可用资源列表")
            return
            
        resource = RECOMMENDED_RESOURCES[args.download]
        downloader = SpriteDownloader(args.dir)
        
        if resource['type'] == 'zip':
            downloader.download_and_extract_zip(resource['url'])
        else:
            downloader.download_from_url(resource['url'])
    else:
        print_download_instructions()


if __name__ == "__main__":
    main()