"""
存档管理系统 - 支持游戏进度保存和加载
JSON格式存档，包含玩家数据、游戏进度、设置信息等
"""

import json
import os
import time
import threading
from datetime import datetime

# 存档目录
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")

class SaveManager:
    """存档管理器 - 线程安全"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._ensure_save_dir()
    
    def _ensure_save_dir(self):
        """确保存档目录存在"""
        with self._lock:
            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR)
    
    def _get_slot_path(self, slot_id):
        """获取存档文件路径"""
        return os.path.join(SAVE_DIR, f"save_{slot_id:03d}.json")
    
    def get_available_slots(self):
        """获取所有可用存档槽位信息"""
        with self._lock:
            slots = []
            for i in range(1, 101):  # 最多100个存档槽
                path = self._get_slot_path(i)
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            player = data.get("player", {})
                            realm_index = player.get("realm_index", 0)
                            realm_name = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"][realm_index] if 0 <= realm_index < 9 else "未知"
                            slots.append({
                                "slot_id": i,
                                "path": path,
                                "timestamp": data.get("meta", {}).get("timestamp", 0),
                                "save_time": data.get("meta", {}).get("save_time", ""),
                                "player_name": player.get("name", "未知"),
                                "realm": realm_name,
                                "stage": player.get("current_stage", 0),
                                "cultivation": player.get("cultivation", 0),
                                "ling_shi": player.get("ling_shi", 0)
                            })
                    except:
                        # 如果读取失败，跳过该存档
                        continue
            return slots
    
    def save_game(self, slot_id, game_data):
        """
        保存游戏进度
        
        参数:
            slot_id: 存档槽位ID (1-100)
            game_data: 游戏数据字典，包含:
                - player: 玩家数据 (姓名/灵根/职业/修为/灵石等)
                - progress: 游戏进度 (当前界面/已解锁功能等)
                - settings: 设置信息
                - meta: 元信息 (时间戳、版本等)
        """
        with self._lock:
            # 确保数据完整
            if "meta" not in game_data:
                game_data["meta"] = {}
            
            game_data["meta"]["timestamp"] = int(time.time())
            game_data["meta"]["save_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            game_data["meta"]["version"] = "1.0.0"
            
            # 保存到文件
            path = self._get_slot_path(slot_id)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(game_data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"存档失败: {e}")
                return False
    
    def load_game(self, slot_id):
        """加载指定存档槽位的游戏数据"""
        with self._lock:
            path = self._get_slot_path(slot_id)
            if not os.path.exists(path):
                return None
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"读档失败: {e}")
                return None
    
    def delete_save(self, slot_id):
        """删除指定存档"""
        with self._lock:
            path = self._get_slot_path(slot_id)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    return True
                except:
                    return False
            return False
    
    def auto_save(self, game_data, max_auto_saves=10):
        """
        自动存档 - 使用自动存档槽位
        
        参数:
            game_data: 游戏数据
            max_auto_saves: 最大自动存档数量，超过时覆盖最旧的
        """
        with self._lock:
            # 查找所有自动存档
            auto_saves = []
            for i in range(1, max_auto_saves + 1):
                path = self._get_slot_path(1000 + i)  # 1001-1010为自动存档槽
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            auto_saves.append({
                                "slot_id": 1000 + i,
                                "path": path,
                                "timestamp": data.get("meta", {}).get("timestamp", 0)
                            })
                    except:
                        continue
            
            # 按时间戳排序
            auto_saves.sort(key=lambda x: x["timestamp"])
            
            # 选择存档槽位
            if len(auto_saves) < max_auto_saves:
                # 使用空槽位
                slot_id = 1001
                while os.path.exists(self._get_slot_path(slot_id)):
                    slot_id += 1
            else:
                # 覆盖最旧的
                slot_id = auto_saves[0]["slot_id"]
            
            # 保存
            return self.save_game(slot_id, game_data)
    
    def collect_game_data(self, ling_shi_amount=None):
        """
        收集当前游戏状态数据
        
        参数:
            ling_shi_amount: 当前灵石数量（可选，用于避免重复读取文件）
        
        返回包含完整游戏状态的字典，用于存档
        """
        import realm_data
        import gongfa_data
        
        # 玩家数据
        player = realm_data.player.copy()
        
        # 灵根数据
        spiritual_root = gongfa_data.player_gongfa.get("spiritual_root")
        if spiritual_root:
            root_type, elements, bonus = spiritual_root
            player["spiritual_root"] = {
                "type": root_type,
                "elements": elements,
                "bonus": bonus
            }
        
        # 功法数据
        player["equipped_gongfa"] = gongfa_data.player_gongfa.get("equipped", {})
        
        # 灵石数据
        if ling_shi_amount is not None:
            player["ling_shi"] = ling_shi_amount
        else:
            from ling_shi_data import LingShiWallet
            wallet = LingShiWallet()
            player["ling_shi"] = wallet.amount
        
        # 修炼状态
        player["cultivation_state"] = realm_data.cultivation_state.copy()
        
        # 洞府数据
        import cave_data
        player["cave_data"] = {
            "herb_garden": cave_data.player_cave["herb_garden"].copy(),
            "spirit_array": cave_data.player_cave["spirit_array"].copy(),
            "apprentice": cave_data.player_cave["apprentice"].copy(),
        }

        # 藏宝阁数据
        import treasure_data
        player["treasure_data"] = {
            "player_treasure": treasure_data.player_treasure.copy(),
        }
        
        # 游戏进度
        progress = {
            "unlocked_features": [],  # 已解锁功能列表
            "current_interface": None,  # 当前界面
            "completed_maps": [],  # 已通关地图
            "highest_tower_level": 0,  # 锁妖塔最高层数
        }
        
        # 设置信息
        from settings_manager import get_settings_manager
        settings_manager = get_settings_manager()
        all_settings = settings_manager.get_all_settings()
        
        return {
            "player": player,
            "progress": progress,
            "settings": all_settings,
            "meta": {
                "game_version": "1.0.0",
                "save_type": "manual"
            }
        }


# 全局存档管理器实例
_save_manager = None

def get_save_manager():
    """获取全局存档管理器实例"""
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveManager()
    return _save_manager