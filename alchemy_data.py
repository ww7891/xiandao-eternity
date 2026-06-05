"""
炼丹模块数据
"""
import random

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]

# 每个境界对应一种炼丹材料
REALM_MATERIALS = {
    0: {"name": "青灵草", "desc": "练气期灵草，蕴含稀薄灵气"},
    1: {"name": "筑基花", "desc": "筑基期灵花，花蕊含灵液"},
    2: {"name": "金髓芝", "desc": "金丹期灵材，通体如金"},
    3: {"name": "紫婴藤", "desc": "元婴期灵藤，紫气缭绕"},
    4: {"name": "化神果", "desc": "化神期灵果，助神魂壮大"},
    5: {"name": "合道参", "desc": "合体期宝参，参须如丝"},
    6: {"name": "劫雷砂", "desc": "渡劫期雷砂，含天劫余威"},
    7: {"name": "乘云露", "desc": "大乘期云露，飘渺若仙"},
    8: {"name": "仙灵晶", "desc": "真仙级灵晶，仙气充盈"},
}

# 丹药类型
PILL_TYPES = {
    "巨力丹": {"effect_type": "attack", "base_value": 3, "desc_template": "增加{value}点攻击"},
    "气血丹": {"effect_type": "max_hp", "base_value": 15, "desc_template": "增加{value}点生命上限"},
    "磐石丹": {"effect_type": "defense", "base_value": 2, "desc_template": "增加{value}点防御"},
    "蕴灵丹": {"effect_type": "max_mp", "base_value": 10, "desc_template": "增加{value}点灵力上限"},
    "聚气丹": {"effect_type": "cultivation", "base_value": 100, "desc_template": "获得{value}点修为"},
}

PILL_TYPE_ORDER = ["巨力丹", "气血丹", "磐石丹", "蕴灵丹", "聚气丹"]

QUALITIES = ["白", "绿", "蓝", "紫", "金"]
QUALITY_MULTIPLIER = {"白": 1.0, "绿": 1.2, "蓝": 1.5, "紫": 2.0, "金": 3.0}
QUALITY_DISPLAY_COLORS = {
    "白": (180, 180, 180),
    "绿": (100, 200, 100),
    "蓝": (100, 150, 255),
    "紫": (200, 100, 255),
    "金": (255, 200, 80),
}

ALCHEMIST_MAX_LEVEL = 9


def get_quality_probs(alchemist_level, pill_grade):
    """
    根据丹师等级与丹药品级的差值返回品质权重 [白, 绿, 蓝, 紫, 金]
    pill_grade: 1-9（丹药的品级）
    """
    diff = alchemist_level - pill_grade
    if diff >= 3:
        return [10, 20, 30, 25, 15]
    elif diff >= 1:
        return [20, 25, 25, 20, 10]
    elif diff == 0:
        return [30, 30, 25, 10, 5]
    elif diff >= -2:
        return [45, 30, 15, 7, 3]
    else:
        return [60, 25, 10, 4, 1]


def roll_quality(alchemist_level, pill_grade):
    probs = get_quality_probs(alchemist_level, pill_grade)
    return random.choices(QUALITIES, weights=probs, k=1)[0]


# 玩家炼丹状态
player_alchemy = {
    "level": 1,
    "exp": 0,
    "materials": {},
    "pills": [],
}


def seed_test_materials():
    """新游戏初始材料，已在存档系统中的不触发"""
    if any(v > 0 for v in player_alchemy["materials"].values()) or player_alchemy["pills"]:
        return
    player_alchemy["materials"] = {0: 10, 1: 5}
    print("[Alchemy] 已发放初始炼丹材料")


def get_exp_for_level(level):
    return level * 150


def add_alchemy_exp(amount):
    player_alchemy["exp"] += amount
    current_level = player_alchemy["level"]
    if current_level >= ALCHEMIST_MAX_LEVEL:
        return False
    needed = get_exp_for_level(current_level)
    if player_alchemy["exp"] >= needed:
        player_alchemy["exp"] -= needed
        player_alchemy["level"] += 1
        return True
    return False


def craft_pill(pill_type, grade):
    """
    炼制丹药
    grade: 1-9（丹药品级）
    返回: (pill, quality) 或 (None, None)
    """
    realm_index = grade - 1

    count = player_alchemy["materials"].get(realm_index, 0)
    if count <= 0:
        return None, None

    player_alchemy["materials"][realm_index] = count - 1
    quality = roll_quality(player_alchemy["level"], grade)

    pt = PILL_TYPES[pill_type]
    base = pt["base_value"]
    grade_mult = 1.0 + (grade - 1) * 0.5
    quality_mult = QUALITY_MULTIPLIER[quality]
    effect_value = int(base * grade_mult * quality_mult)

    pill = {
        "name": f"{grade}品{pill_type}",
        "grade": grade,
        "quality": quality,
        "type": pill_type,
        "effect_type": pt["effect_type"],
        "effect_value": effect_value,
        "desc": pt["desc_template"].format(value=effect_value),
    }

    player_alchemy["pills"].append(pill)
    add_alchemy_exp(grade * 10)
    return pill, quality