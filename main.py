"""
仙道永恒 - Android 兼容入口点
处理 Android 平台适配：字体路径、屏幕缩放、生命周期管理
同时保持桌面端兼容
"""

import os
import sys

# 确保工作目录正确（Android 和桌面端都需要）
__dir__ = os.path.dirname(os.path.abspath(__file__))
os.chdir(__dir__)
if __dir__ not in sys.path:
    sys.path.insert(0, __dir__)

# 检测运行平台
IS_ANDROID = False
try:
    import android
    IS_ANDROID = True
except ImportError:
    pass

def patch_config_for_platform():
    """
    根据平台修补配置文件
    - Android: 确保使用相对路径字体，调整屏幕模式
    - 桌面端: 保持原有行为
    """
    import json
    config_path = os.path.join(__dir__, "config.json")

    if not os.path.exists(config_path):
        print("⚠️ 配置文件不存在，将使用默认配置")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 确保字体路径有效（跨平台兼容）
    primary_font = config.get("font", {}).get("primary", "")
    fallback_font = config.get("font", {}).get("fallback", "")

    # Android 平台特殊处理
    if IS_ANDROID:
        print("📱 检测到 Android 平台，应用适配设置...")

        # 强制全屏模式
        if "display" in config:
            config["display"]["fullscreen"] = True

        # 字体路径修正
        if primary_font and not os.path.exists(primary_font):
            # 尝试在 assets/fonts 目录下查找
            bundled_primary = os.path.join(__dir__, "assets", "fonts", "STXINGKA.TTF")
            if os.path.exists(bundled_primary):
                config["font"]["primary"] = bundled_primary
                print(f"✅ 使用打包字体: {bundled_primary}")
            else:
                # 尝试 simhei
                bundled_fallback = os.path.join(__dir__, "assets", "fonts", "simhei.ttf")
                if os.path.exists(bundled_fallback):
                    config["font"]["primary"] = bundled_fallback
                    print(f"✅ 使用后备打包字体: {bundled_fallback}")

        if fallback_font and not os.path.exists(fallback_font):
            bundled_fallback = os.path.join(__dir__, "assets", "fonts", "simhei.ttf")
            if os.path.exists(bundled_fallback):
                config["font"]["fallback"] = bundled_fallback

        # 写入修补后的配置
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ Android 平台配置适配完成")
    else:
        # 桌面端：如果配置中的字体路径不存在，尝试使用绑定的字体
        if primary_font and not os.path.exists(primary_font):
            bundled_primary = os.path.join(__dir__, "assets", "fonts", "STXINGKA.TTF")
            if os.path.exists(bundled_primary):
                config["font"]["primary"] = bundled_primary
                print(f"✅ 使用捆绑字体: {bundled_primary}")

        if fallback_font and not os.path.exists(fallback_font):
            bundled_fallback = os.path.join(__dir__, "assets", "fonts", "simhei.ttf")
            if os.path.exists(bundled_fallback):
                config["font"]["fallback"] = bundled_fallback
                print(f"✅ 使用捆绑后备字体: {bundled_fallback}")

        # 仅在路径被修改时才写回
        if (primary_font and not os.path.exists(primary_font)) or \
           (fallback_font and not os.path.exists(fallback_font)):
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)


def main():
    """主入口点 - 兼容 Android 和桌面端"""
    print("=" * 50)
    print("🎮 仙道永恒 - 启动中...")
    print(f"📁 工作目录: {__dir__}")
    print(f"📱 Android 平台: {IS_ANDROID}")
    print("=" * 50)

    # 修补配置以适配当前平台
    patch_config_for_platform()

    # 导入并运行游戏
    from game_main import Game

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
