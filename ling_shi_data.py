"""
灵石货币系统 - 数据层
管理灵石数量、增减操作、存档持久化
"""

import json
import os
import threading

# 数据文件路径（存在游戏目录下）
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ling_shi_data.json")

class LingShiWallet:
    """灵石钱包 - 线程安全"""

    def __init__(self, amount=0):
        self._lock = threading.Lock()
        self._amount = amount
        self._load()

    def _load(self):
        """从文件加载灵石数量"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._amount = data.get("amount", 0)
        except:
            self._amount = 0

    def _save(self):
        """保存到文件"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"amount": self._amount}, f, ensure_ascii=False)
        except:
            pass

    @property
    def amount(self):
        """获取当前灵石数量"""
        with self._lock:
            return self._amount

    def add(self, count):
        """增加灵石"""
        if count <= 0:
            return False
        with self._lock:
            self._amount += count
            self._save()
            return True

    def spend(self, count):
        """花费灵石，返回是否成功"""
        if count <= 0:
            return False
        with self._lock:
            if self._amount >= count:
                self._amount -= count
                self._save()
                return True
            return False

    def can_afford(self, count):
        """检查是否足够"""
        with self._lock:
            return self._amount >= count