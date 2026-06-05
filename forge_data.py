"""
炼器模块数据 - 强化 & 锻造
"""
import random

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]

# ==================== 随机名称生成 ====================
_ENHANCE_PREFIX_POOL = ["玄", "灵", "金", "紫", "化", "合", "劫", "乘", "仙", "青", "赤", "银", "玉"]
_ENHANCE_SUFFIX_POOL = ["铁砂", "石晶", "髓液", "婴露", "神淬", "道玉", "雷核", "云精", "灵髓", "钢粉", "铜砾", "骨末", "火硝"]
_FORGE_PREFIX_POOL = ["青玄", "银髓", "金纹", "紫云", "化骨", "合道", "劫雷", "乘云", "仙灵", "赤焰", "寒玉", "墨钢", "星砂"]
_FORGE_SUFFIX_POOL = ["铁", "钢", "玉", "铜", "石", "骨", "晶", "丝", "木"]

def _gen_random_names(pool, count):
    """生成 count 个不重复的随机名称"""
    random.shuffle(pool)
    names = []
    for i in range(count):
        names.append(pool[i % len(pool)])
    return names

# 九种强化材料（练气→真仙），名称随机生成
_ENHANCE_NAMES = _gen_random_names(
    [f"{p}{s}" for p in _ENHANCE_PREFIX_POOL for s in _ENHANCE_SUFFIX_POOL],
    9
)

REALM_ENHANCE_MATERIALS = {}
for realm_idx in range(9):
    REALM_ENHANCE_MATERIALS[realm_idx] = {
        "name": _ENHANCE_NAMES[realm_idx],
        "desc": f"{REALM_NAMES[realm_idx]}级强化材料，用以淬炼法宝神兵"
    }

# 九种锻造材料（练气→真仙），名称随机生成
_FORGE_NAMES = _gen_random_names(
    [f"{p}{s}" for p in _FORGE_PREFIX_POOL for s in _FORGE_SUFFIX_POOL],
    9
)

REALM_FORGE_MATERIALS = {}
for realm_idx in range(9):
    REALM_FORGE_MATERIALS[realm_idx] = {
        "name": _FORGE_NAMES[realm_idx],
        "desc": f"{REALM_NAMES[realm_idx]}级锻造材料，天材地宝熔铸而成"
    }

# ==================== 品质系统 ====================
EQUIP_QUALITIES = ["白", "绿", "蓝", "紫", "金"]
QUALITY_MULTIPLIER = {"白": 1.0, "绿": 1.3, "蓝": 1.7, "紫": 2.2, "金": 3.0}
EQUIP_QUALITY_COLORS = {
    "白": (180, 180, 180),
    "绿": (100, 200, 100),
    "蓝": (100, 150, 255),
    "紫": (200, 100, 255),
    "金": (255, 200, 80),
}
QUALITY_STARS = {"白": 1, "绿": 2, "蓝": 3, "紫": 4, "金": 5}

# ==================== 强化系统 ====================

def get_enhance_cap(realm_index):
    """强化上限：练气+10, 筑基+20, 金丹+30, ..., 真仙+90"""
    return (realm_index + 1) * 10

def get_enhance_success_rate(enhance_level, realm_index):
    """计算强化成功率，随强化等级递减"""
    cap = get_enhance_cap(realm_index)
    if cap == 0:
        return 0.0
    decay = (enhance_level / cap) * 0.75
    return max(0.05, 0.95 * (1.0 - decay))

def get_enhance_bonus_per_level(realm_index):
    """每级强化的属性加成基数（与境界倍率一致）"""
    realm_mult = 5 ** realm_index
    return {
        "attack": realm_mult * 1,
        "hp": realm_mult * 5,
        "defense": max(1, realm_mult // 2),
    }

def apply_enhance_stats(equip, enhance_level):
    """根据强化等级重置装备属性（base → enhanced）"""
    if "base_attack" not in equip:
        equip["base_attack"] = equip.get("attack", 0)
        equip["base_hp"] = equip.get("hp", 0)
        equip["base_defense"] = equip.get("defense", 0)
        equip["realm_index"] = equip.get("realm_index", 0)
        equip["enhance_level"] = 0

    realm_idx = equip.get("realm_index", 0)
    bonus = get_enhance_bonus_per_level(realm_idx)

    equip["enhance_level"] = enhance_level
    equip["attack"] = equip["base_attack"] + bonus["attack"] * enhance_level
    equip["hp"] = equip["base_hp"] + bonus["hp"] * enhance_level
    equip["defense"] = equip["base_defense"] + bonus["defense"] * enhance_level

    return equip

# ==================== 锻造系统 ====================

FORGER_MAX_LEVEL = 9

def get_forge_quality_probs(forger_level, equip_realm):
    """根据锻造师等级与装备境界的差值返回品质权重 [白,绿,蓝,紫,金]
    equip_realm: 0-8（装备境界指数）
    """
    diff = forger_level - (equip_realm + 1)  # +1 因为锻造师1级对应练气
    if diff >= 3:
        return [5, 15, 30, 30, 20]
    elif diff >= 1:
        return [15, 25, 30, 20, 10]
    elif diff == 0:
        return [25, 30, 25, 15, 5]
    elif diff >= -2:
        return [45, 30, 15, 7, 3]
    else:
        return [60, 25, 10, 4, 1]

def roll_forge_quality(forger_level, equip_realm):
    """随机生成装备品质"""
    probs = get_forge_quality_probs(forger_level, equip_realm)
    return random.choices(EQUIP_QUALITIES, weights=probs, k=1)[0]

# ==================== 装备名称与属性 ====================

EQUIP_SLOT_CN = {
    "weapon": "武器", "helmet": "头盔", "armor": "防具",
    "gloves": "手套", "belt": "腰带", "shoes": "鞋子",
    "accessory1": "饰品一", "accessory2": "饰品二",
}

EQUIP_REALM_PREFIX = {
    0: "凡铁", 1: "灵铜", 2: "金纹", 3: "元婴",
    4: "化神", 5: "合体", 6: "渡劫", 7: "大乘", 8: "仙品",
}

EQUIP_NAME_POOL = {
    "weapon": ["飞剑", "灵刀", "战戟", "长枪", "宝扇", "拂尘", "法杖", "短匕"],
    "helmet": ["道冠", "战盔", "灵冠", "斗笠", "玉簪"],
    "armor": ["道袍", "战甲", "灵铠", "法衣", "玄衣"],
    "gloves": ["护手", "灵掌", "拳套", "铁手", "丝套"],
    "belt": ["灵带", "玉带", "金缕带", "战带", "玄索"],
    "shoes": ["云履", "战靴", "疾风靴", "灵屐", "踏云"],
    "accessory1": ["玉佩", "灵珠", "铜铃", "骨符", "魂坠"],
    "accessory2": ["护符", "灵环", "宝镜", "龟甲", "道印"],
}

def generate_equip_name(slot, realm_index, quality):
    """生成装备名称"""
    prefix = EQUIP_REALM_PREFIX.get(realm_index, "灵物")
    pool = EQUIP_NAME_POOL.get(slot, ["灵器"])
    suffix = random.choice(pool)
    qual_tag = {"金": "·圣", "紫": "·极", "蓝": "·上"}.get(quality, "")
    return f"{prefix}{qual_tag}{suffix}"

def generate_equip_stats(realm_index, quality):
    """根据境界和品质生成装备基础属性
    境界倍率 = 5^realm_index，与角色属性增长比例一致
    练气(0): 倍率1, 筑基(1): 倍率5, 金丹(2): 倍率25, 元婴(3): 倍率125...
    """
    mult = QUALITY_MULTIPLIER.get(quality, 1.0)
    realm_mult = 5 ** realm_index
    base_power = realm_mult * 10 * mult

    attack = int(base_power * random.uniform(0.6, 1.4))
    hp = int(base_power * random.uniform(2.0, 4.0))
    defense = int(base_power * random.uniform(0.4, 0.9))

    return {
        "attack": max(1, attack),
        "hp": max(8, hp),
        "defense": max(1, defense),
    }

def forge_equipment(slot, realm_index, quality):
    """锻造一件装备，返回装备字典"""
    stats = generate_equip_stats(realm_index, quality)
    return {
        "name": generate_equip_name(slot, realm_index, quality),
        "type": EQUIP_SLOT_CN.get(slot, "装备"),
        "slot": slot,
        "quality": quality,
        "realm_index": realm_index,
        "enhance_level": 0,
        "base_attack": stats["attack"],
        "base_hp": stats["hp"],
        "base_defense": stats["defense"],
        "attack": stats["attack"],
        "hp": stats["hp"],
        "defense": stats["defense"],
        "description": f"{REALM_NAMES[realm_index]}境界·{quality}品质{EQUIP_SLOT_CN.get(slot, '装备')}",
    }

# ==================== 经验公式 ====================

def get_exp_for_level(level):
    """锻造师升级所需经验"""
    return 100 * level * level

# ==================== 玩家锻造状态 ====================

player_forge = {
    "level": 1,
    "exp": 0,
    "enhance_materials": {},   # {realm_index: count}
    "forge_materials": {},     # {realm_index: count}
}

def seed_test_materials():
    """新游戏初始化材料（测试用）"""
    if any(v > 0 for v in player_forge["enhance_materials"].values()) or \
       any(v > 0 for v in player_forge["forge_materials"].values()):
        return
    for i in range(6):
        player_forge["enhance_materials"][i] = 20
        player_forge["forge_materials"][i] = 15