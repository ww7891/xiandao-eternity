"""
《仙道永恒》游戏设置管理模块
作者：游戏开发团队
日期：2026-05-28
功能：管理游戏设置，支持音量设置、保存和加载
"""

import json
import os
from pathlib import Path

class SettingsManager:
    """设置管理器类"""
    
    def __init__(self, config_path=None):
        """
        初始化设置管理器
        
        参数:
            config_path: 配置文件路径，默认为 settings.json
        """
        if config_path is None:
            # 默认配置文件路径
            self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        else:
            self.config_path = config_path
        
        # 默认设置
        self.default_settings = {
            "audio": {
                "main_menu_volume": 50,   # 主界面音量 (0-100)
                "battle_volume": 50,      # 战斗界面音量 (0-100)
                "master_volume": 100      # 主音量 (0-100)
            },
            "display": {
                "fullscreen": False,
                "resolution": "1280x720"
            },
            "gameplay": {
                "difficulty": "normal",   # 难度: normal, hard, expert
                "language": "zh_CN"       # 语言
            }
        }
        
        # 当前设置
        self.settings = self.default_settings.copy()
        
        # 加载保存的设置
        self.load_settings()
    
    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合并加载的设置（保留默认值中未保存的设置）
                self._merge_settings(loaded_settings)
                print(f"✅ 设置加载成功: {self.config_path}")
                return True
            else:
                print("ℹ️ 设置文件不存在，使用默认设置")
                return False
        except Exception as e:
            print(f"❌ 设置加载失败: {e}")
            return False
    
    def save_settings(self):
        """保存设置到配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 设置保存成功: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ 设置保存失败: {e}")
            return False
    
    def _merge_settings(self, loaded_settings):
        """合并加载的设置到当前设置"""
        def merge_dicts(base, update):
            """递归合并字典"""
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self.settings, loaded_settings)
    
    def get_setting(self, category, key):
        """获取指定设置值"""
        try:
            return self.settings.get(category, {}).get(key)
        except:
            return None
    
    def set_setting(self, category, key, value):
        """设置指定值"""
        if category not in self.settings:
            self.settings[category] = {}
        
        self.settings[category][key] = value
    
    def get_main_menu_volume(self):
        """获取主界面音量 (0-100)"""
        return self.get_setting("audio", "main_menu_volume")
    
    def set_main_menu_volume(self, volume):
        """设置主界面音量 (0-100)"""
        if 0 <= volume <= 100:
            self.set_setting("audio", "main_menu_volume", volume)
            return True
        return False
    
    def get_battle_volume(self):
        """获取战斗界面音量 (0-100)"""
        return self.get_setting("audio", "battle_volume")
    
    def set_battle_volume(self, volume):
        """设置战斗界面音量 (0-100)"""
        if 0 <= volume <= 100:
            self.set_setting("audio", "battle_volume", volume)
            return True
        return False
    
    def get_master_volume(self):
        """获取主音量 (0-100)"""
        return self.get_setting("audio", "master_volume")
    
    def set_master_volume(self, volume):
        """设置主音量 (0-100)"""
        if 0 <= volume <= 100:
            self.set_setting("audio", "master_volume", volume)
            return True
        return False
    
    def get_volume_for_interface(self, interface_name):
        """
        根据界面名称获取对应的音量值
        
        参数:
            interface_name: 界面名称
        """
        # 使用主界面音乐的界面
        main_menu_interfaces = [
            'title_screen',       # 标题界面
            'spiritual_root',     # 灵根抽取界面
            'profession_select',  # 职业选择界面
            'main_menu',          # 主菜单界面
            'settings',           # 设置界面
            'character',          # 人物界面
            'inventory',          # 背包界面
            'equipment',          # 装备界面
            'craft_炼丹',         # 炼丹界面
            'craft_炼器',         # 炼器界面
            'craft_绘符',         # 绘符界面
        ]
        
        # 战斗界面
        battle_interfaces = [
            'battle_历练之路',    # 历练之路
            'battle_锁妖塔',      # 锁妖塔
            'battle_远古战场',    # 远古战场
            'adventure_map',      # 冒险地图
            'combat_view',        # 战斗界面
            'combat_result',      # 战斗结果
            'combat_death',       # 战斗死亡
        ]
        
        if interface_name in main_menu_interfaces:
            return self.get_main_menu_volume()
        elif interface_name in battle_interfaces:
            return self.get_battle_volume()
        else:
            # 默认使用主界面音量
            return self.get_main_menu_volume()
    
    def get_normalized_volume(self, interface_name):
        """
        获取归一化的音量值 (0.0-1.0)
        
        参数:
            interface_name: 界面名称
        """
        volume_percent = self.get_volume_for_interface(interface_name)
        master_volume = self.get_master_volume()
        
        # 计算最终音量：界面音量 * 主音量 / 10000
        final_volume = (volume_percent * master_volume) / 10000.0
        return max(0.0, min(1.0, final_volume))
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self.settings = self.default_settings.copy()
        return True
    
    def get_all_settings(self):
        """获取所有设置"""
        return self.settings.copy()


# 全局设置管理器实例
_settings_manager_instance = None

def get_settings_manager(config_path=None):
    """
    获取全局设置管理器实例（单例模式）
    
    参数:
        config_path: 配置文件路径
    """
    global _settings_manager_instance
    
    if _settings_manager_instance is None:
        _settings_manager_instance = SettingsManager(config_path)
    
    return _settings_manager_instance