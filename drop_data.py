"""
掉落系统定义
"""

import random

# 掉落物品类型
DROP_TABLE = {
    "灵石": {"weight": 65, "type": "currency", "min_qty": 1, "max_qty": 5, "quality": 1},
    "精铁": {"weight": 28, "type": "material", "min_qty": 1, "max_qty": 3, "quality": 1},
    "装备": {"weight": 7, "type": "equipment", "min_qty": 1, "max_qty": 1, "quality": 3},
}

# Boss额外掉落
BOSS_DROP_TABLE = {
    "灵石": {"weight": 45, "type": "currency", "min_qty": 10, "max_qty": 50, "quality": 2},
    "精铁": {"weight": 30, "type": "material", "min_qty": 5, "max_qty": 15, "quality": 2},
    "装备": {"weight": 20, "type": "equipment", "min_qty": 1, "max_qty": 1, "quality": 4},
    "丹药": {"weight": 5, "type": "pill", "min_qty": 1, "max_qty": 2, "quality": 3},
}


def roll_drop(is_boss=False, realm_bonus=0):
    """
    计算一次掉落
    返回: [(物品名, 数量, 品质), ...]
    """
    table = BOSS_DROP_TABLE if is_boss else DROP_TABLE
    results = []

    # 普通怪掉落0-1件，精英怪1-2件，Boss 3-5件
    if is_boss:
        drop_count = random.randint(3, 5)
    else:
        drop_count = 1 if random.random() < 0.5 else 0

    for _ in range(drop_count):
        # 加权随机选择
        total_weight = sum(item["weight"] for item in table.values())
        roll = random.uniform(0, total_weight)
        cumulative = 0
        for name, data in table.items():
            cumulative += data["weight"]
            if roll <= cumulative:
                qty = random.randint(data["min_qty"], data["max_qty"])
                # 境界加成：品质随境界略微提升
                quality = data["quality"] + realm_bonus
                results.append((name, qty, quality))
                break

    return results


def process_drops(drops, ling_shi_wallet=None):
    """
    将掉落物应用到玩家数据
    返回掉落摘要文本
    """
    import realm_data
    summary = []

    for name, qty, quality in drops:
        if name == "灵石":
            # 优先使用灵石钱包
            if ling_shi_wallet:
                ling_shi_wallet.add(qty)
            else:
                # 回退到旧系统
                realm_data.player["spirit_stones"] += qty
            summary.append(f"灵石 ×{qty}")
        elif name == "精铁":
            summary.append(f"精铁 ×{qty}")
        elif name == "丹药":
            summary.append(f"丹药 ×{qty}")
        elif name == "装备":
            summary.append(f"装备 ×{qty}")

    return summary