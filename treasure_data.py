"""
仙道永恒 - 藏宝阁数据模块
藏宝阁九层，每层对应一个境界（练气-真仙）
包含：藏经阁（功法）、法宝库（装备）、丹药房（丹药）、材料仓（材料）
"""

import random
from gongfa_data import GONGFA_POOL, QUALITIES, QUALITY_BONUS, QUALITY_MIN_REALM, QUALITY_DISPLAY_COLORS
from realm_data import REALM_NAMES

# ==================== 藏宝阁配置 ====================
TREASURE_FLOORS = 9  # 对应9个境界

# 每层的进入条件（境界索引）
FLOOR_REQUIREMENTS = {
    0: 0,  # 练气期
    1: 1,  # 筑基期
    2: 2,  # 金丹期
    3: 3,  # 元婴期
    4: 4,  # 化神期
    5: 5,  # 合体期
    6: 6,  # 渡劫期
    7: 7,  # 大乘期
    8: 8,  # 真仙期
}

# 每层的灵石消耗系数（基础价格 × 系数）
FLOOR_PRICE_MULTIPLIER = {
    0: 1.0,   # 练气
    1: 2.0,   # 筑基
    2: 4.0,   # 金丹
    3: 8.0,   # 元婴
    4: 16.0,  # 化神
    5: 32.0,  # 合体
    6: 64.0,  # 渡劫
    7: 128.0, # 大乘
    8: 256.0, # 真仙
}

# ==================== 藏经阁（功法）配置 ====================
# 功法类型权重（不包含心法）
GONGFA_TYPE_WEIGHTS = {
    "灵技": 60,  # 60%概率
    "内经": 40,  # 40%概率
    "心法": 0,   # 0%概率（不出现）
}

# 品质概率分布（藏宝阁专用，偏向低品质）
TREASURE_QUALITY_WEIGHTS = {
    "白": 50,  # 50%白色
    "绿": 30,  # 30%绿色
    "蓝": 15,  # 15%蓝色
    "紫": 4,   # 4%紫色
    "金": 1,   # 1%金色
}

def get_treasure_gongfa_pool(floor):
    """获取指定楼层的功法池
    规则：只包含灵技和内经，不包含心法
    品质概率按TREASURE_QUALITY_WEIGHTS分布
    境界要求 <= floor
    """
    pool = []
    for gongfa in GONGFA_POOL:
        # 排除心法
        if gongfa["type"] == "心法":
            continue
        
        # 检查境界要求
        if gongfa["realm_min"] > floor:
            continue
        
        # 检查品质是否允许
        if gongfa["quality"] not in TREASURE_QUALITY_WEIGHTS:
            continue
            
        pool.append(gongfa)
    
    return pool

def generate_floor_gongfas(floor, count=6):
    """为指定楼层生成功法商品
    返回：功法ID列表
    """
    pool = get_treasure_gongfa_pool(floor)
    if not pool:
        return []
    
    # 按权重筛选（品质权重 + 类型权重）
    weighted_pool = []
    for g in pool:
        # 品质权重
        quality_weight = TREASURE_QUALITY_WEIGHTS.get(g["quality"], 0)
        if quality_weight == 0:
            continue
        
        # 类型权重
        type_weight = GONGFA_TYPE_WEIGHTS.get(g["type"], 0)
        if type_weight == 0:
            continue
        
        # 总权重
        total_weight = quality_weight + type_weight
        weighted_pool.append((g, total_weight))
    
    if not weighted_pool:
        return []
    
    # 按权重随机选择
    items, weights = zip(*weighted_pool)
    selected = random.choices(items, weights=weights, k=min(count, len(items)))
    
    return [g["id"] for g in selected]

def calculate_gongfa_price(gongfa_id, floor):
    """计算功法价格
    基础价格 = 品质系数 × 类型系数 × 境界系数
    最终价格 = 基础价格 × 楼层系数
    """
    gongfa = None
    for g in GONGFA_POOL:
        if g["id"] == gongfa_id:
            gongfa = g
            break
    
    if not gongfa:
        return 0
    
    # 品质系数
    quality_coeff = {
        "白": 1.0,
        "绿": 2.0,
        "蓝": 5.0,
        "紫": 15.0,
        "金": 50.0,
    }.get(gongfa["quality"], 1.0)
    
    # 类型系数（灵技更贵，内经稍便宜）
    type_coeff = {
        "灵技": 1.5,
        "内经": 1.0,
        "心法": 2.0,
    }.get(gongfa["type"], 1.0)
    
    # 境界系数（境界要求越高越贵）
    realm_coeff = 2.0 ** gongfa["realm_min"]
    
    # 基础价格
    base_price = 100 * quality_coeff * type_coeff * realm_coeff
    
    # 楼层系数
    floor_multiplier = FLOOR_PRICE_MULTIPLIER.get(floor, 1.0)
    
    # 最终价格（取整）
    final_price = int(base_price * floor_multiplier)
    
    # 确保最低价格
    return max(100, final_price)

# ==================== 法宝库（装备）配置 ====================
# 装备类型
EQUIP_TYPES = ["武器", "头盔", "护甲", "手套", "腰带", "鞋子", "饰品1", "饰品2"]

# 装备品质概率
EQUIP_QUALITY_WEIGHTS = {
    "白": 50,
    "绿": 30,
    "蓝": 15,
    "紫": 4,
    "金": 1,
}

# 装备属性加成范围（按品质）
EQUIP_ATTRIBUTE_RANGES = {
    "白": {"attack": (5, 15), "defense": (3, 10), "hp": (20, 50)},
    "绿": {"attack": (15, 30), "defense": (10, 20), "hp": (50, 100)},
    "蓝": {"attack": (30, 60), "defense": (20, 40), "hp": (100, 200)},
    "紫": {"attack": (60, 120), "defense": (40, 80), "hp": (200, 400)},
    "金": {"attack": (120, 250), "defense": (80, 160), "hp": (400, 800)},
}

def generate_equipment(floor, count=6):
    """为指定楼层生成装备商品
    返回：装备字典列表
    """
    equipments = []
    eid = 10000  # 装备ID从10000开始
    
    for _ in range(count):
        # 随机品质
        quality = random.choices(
            list(EQUIP_QUALITY_WEIGHTS.keys()),
            weights=list(EQUIP_QUALITY_WEIGHTS.values()),
            k=1
        )[0]
        
        # 随机装备类型
        equip_type = random.choice(EQUIP_TYPES)
        
        # 根据品质和类型生成属性
        attr_range = EQUIP_ATTRIBUTE_RANGES[quality]
        
        # 确定主属性（武器/饰品加攻击，护甲/头盔加防御，腰带/鞋子加生命）
        if equip_type in ["武器", "饰品1", "饰品2"]:
            main_attr = "attack"
            main_value = random.randint(*attr_range["attack"])
            sub_attr = random.choice(["defense", "hp"])
            sub_value = random.randint(*attr_range[sub_attr]) // 2
        elif equip_type in ["护甲", "头盔", "手套"]:
            main_attr = "defense"
            main_value = random.randint(*attr_range["defense"])
            sub_attr = random.choice(["attack", "hp"])
            sub_value = random.randint(*attr_range[sub_attr]) // 2
        else:  # 腰带、鞋子
            main_attr = "hp"
            main_value = random.randint(*attr_range["hp"])
            sub_attr = random.choice(["attack", "defense"])
            sub_value = random.randint(*attr_range[sub_attr]) // 2
        
        # 装备名称
        quality_prefix = {
            "白": "普通",
            "绿": "精良",
            "蓝": "稀有",
            "紫": "史诗",
            "金": "传说",
        }[quality]
        
        type_suffix = {
            "武器": "剑/刀/杖",
            "头盔": "盔/冠/巾",
            "护甲": "甲/袍/衫",
            "手套": "手/拳/套",
            "腰带": "带/绦/环",
            "鞋子": "靴/履/鞋",
            "饰品1": "戒/镯/佩",
            "饰品2": "链/坠/符",
        }[equip_type]
        
        name = f"{quality_prefix}{type_suffix}"
        
        # 装备描述
        attr_display = {
            "attack": "攻击",
            "defense": "防御",
            "hp": "生命",
        }
        
        desc = f"{attr_display[main_attr]}+{main_value}"
        if sub_value > 0:
            desc += f"，{attr_display[sub_attr]}+{sub_value}"
        
        # 创建装备
        equipment = {
            "id": eid,
            "name": name,
            "type": equip_type,
            "quality": quality,
            "realm_min": floor,  # 装备境界要求
            "attributes": {
                main_attr: main_value,
                sub_attr: sub_value,
            },
            "desc": desc,
        }
        
        equipments.append(equipment)
        eid += 1
    
    return equipments

def calculate_equipment_price(equipment, floor):
    """计算装备价格"""
    # 品质系数
    quality_coeff = {
        "白": 1.0,
        "绿": 2.0,
        "蓝": 5.0,
        "紫": 15.0,
        "金": 50.0,
    }.get(equipment["quality"], 1.0)
    
    # 属性总值系数
    total_attr = sum(equipment["attributes"].values())
    attr_coeff = total_attr / 50.0  # 以50属性为基准
    
    # 境界系数
    realm_coeff = 2.0 ** equipment["realm_min"]
    
    # 基础价格
    base_price = 80 * quality_coeff * attr_coeff * realm_coeff
    
    # 楼层系数
    floor_multiplier = FLOOR_PRICE_MULTIPLIER.get(floor, 1.0)
    
    # 最终价格
    final_price = int(base_price * floor_multiplier)
    
    return max(80, final_price)

# ==================== 丹药房（丹药）配置 ====================
# 丹药类型
PILL_TYPES = [
    {"name": "聚气丹", "effect": "cultivation", "desc": "服用后立即获得修为"},
    {"name": "疗伤丹", "effect": "heal", "desc": "恢复生命值"},
    {"name": "回灵丹", "effect": "mana", "desc": "恢复灵力值"},
    {"name": "破境丹", "effect": "breakthrough", "desc": "提高突破概率"},
    {"name": "属性丹", "effect": "attribute", "desc": "永久增加属性"},
]

# 丹药品质概率
PILL_QUALITY_WEIGHTS = {
    "白": 40,
    "绿": 35,
    "蓝": 15,
    "紫": 8,
    "金": 2,
}

def generate_pills(floor, count=6):
    """为指定楼层生成丹药商品"""
    pills = []
    pid = 20000  # 丹药ID从20000开始
    
    for _ in range(count):
        # 随机品质
        quality = random.choices(
            list(PILL_QUALITY_WEIGHTS.keys()),
            weights=list(PILL_QUALITY_WEIGHTS.values()),
            k=1
        )[0]
        
        # 随机丹药类型
        pill_type = random.choice(PILL_TYPES)
        
        # 根据品质和楼层确定效果值
        quality_multiplier = {
            "白": 1.0,
            "绿": 1.5,
            "蓝": 2.5,
            "紫": 4.0,
            "金": 7.0,
        }[quality]
        
        floor_multiplier = FLOOR_PRICE_MULTIPLIER.get(floor, 1.0)
        
        # 基础效果值
        if pill_type["effect"] == "cultivation":
            base_value = 1000 * floor_multiplier
            effect_value = int(base_value * quality_multiplier)
            desc = f"服用后获得{effect_value}修为"
        elif pill_type["effect"] == "heal":
            base_value = 500 * floor_multiplier
            effect_value = int(base_value * quality_multiplier)
            desc = f"恢复{effect_value}生命值"
        elif pill_type["effect"] == "mana":
            base_value = 300 * floor_multiplier
            effect_value = int(base_value * quality_multiplier)
            desc = f"恢复{effect_value}灵力值"
        elif pill_type["effect"] == "breakthrough":
            base_value = 0.05  # 5%基础概率
            effect_value = base_value * quality_multiplier
            desc = f"突破成功率+{int(effect_value*100)}%"
        else:  # attribute
            base_value = 10 * floor_multiplier
            effect_value = int(base_value * quality_multiplier)
            desc = f"永久增加{effect_value}点随机属性"
        
        # 丹药名称
        quality_suffix = {
            "白": "",
            "绿": "·精",
            "蓝": "·灵",
            "紫": "·仙",
            "金": "·神",
        }[quality]
        
        name = pill_type["name"] + quality_suffix
        
        pill = {
            "id": pid,
            "name": name,
            "type": "丹药",
            "quality": quality,
            "realm_min": floor,
            "effect": pill_type["effect"],
            "effect_value": effect_value,
            "desc": desc,
        }
        
        pills.append(pill)
        pid += 1
    
    return pills

def calculate_pill_price(pill, floor):
    """计算丹药价格"""
    # 品质系数
    quality_coeff = {
        "白": 1.0,
        "绿": 2.0,
        "蓝": 5.0,
        "紫": 15.0,
        "金": 50.0,
    }.get(pill["quality"], 1.0)
    
    # 效果系数（根据效果类型）
    effect_coeff = {
        "cultivation": 1.2,
        "heal": 1.0,
        "mana": 0.8,
        "breakthrough": 2.0,
        "attribute": 1.5,
    }.get(pill["effect"], 1.0)
    
    # 效果值系数
    if isinstance(pill["effect_value"], (int, float)):
        value_coeff = pill["effect_value"] / 1000.0
    else:
        value_coeff = 1.0
    
    # 境界系数
    realm_coeff = 2.0 ** pill["realm_min"]
    
    # 基础价格
    base_price = 50 * quality_coeff * effect_coeff * value_coeff * realm_coeff
    
    # 楼层系数
    floor_multiplier = FLOOR_PRICE_MULTIPLIER.get(floor, 1.0)
    
    # 最终价格
    final_price = int(base_price * floor_multiplier)
    
    return max(50, final_price)

# ==================== 材料仓（材料）配置 ====================
# 材料类型
MATERIAL_TYPES = [
    {"name": "灵石", "desc": "修炼基础资源"},
    {"name": "妖兽内丹", "desc": "妖兽精华凝聚"},
    {"name": "灵草", "desc": "炼丹基础材料"},
    {"name": "矿石", "desc": "炼器基础材料"},
    {"name": "符纸", "desc": "制符基础材料"},
    {"name": "阵法材料", "desc": "布阵基础材料"},
]

# 材料品质概率
MATERIAL_QUALITY_WEIGHTS = {
    "白": 60,
    "绿": 25,
    "蓝": 10,
    "紫": 4,
    "金": 1,
}

def generate_materials(floor, count=6):
    """为指定楼层生成材料商品"""
    materials = []
    mid = 30000  # 材料ID从30000开始
    
    for _ in range(count):
        # 随机品质
        quality = random.choices(
            list(MATERIAL_QUALITY_WEIGHTS.keys()),
            weights=list(MATERIAL_QUALITY_WEIGHTS.values()),
            k=1
        )[0]
        
        # 随机材料类型
        material_type = random.choice(MATERIAL_TYPES)
        
        # 根据品质确定数量
        quality_multiplier = {
            "白": 10,
            "绿": 5,
            "蓝": 3,
            "紫": 2,
            "金": 1,
        }[quality]
        
        floor_multiplier = int(FLOOR_PRICE_MULTIPLIER.get(floor, 1.0))
        
        # 基础数量
        base_quantity = 100 // quality_multiplier
        quantity = base_quantity * floor_multiplier
        
        # 材料名称
        quality_prefix = {
            "白": "普通",
            "绿": "精良",
            "蓝": "稀有",
            "紫": "珍稀",
            "金": "绝世",
        }[quality]
        
        name = f"{quality_prefix}{material_type['name']}"
        
        material = {
            "id": mid,
            "name": name,
            "type": "材料",
            "quality": quality,
            "realm_min": floor,
            "quantity": quantity,
            "desc": f"{material_type['desc']} ×{quantity}",
        }
        
        materials.append(material)
        mid += 1
    
    return materials

def calculate_material_price(material, floor):
    """计算材料价格"""
    # 品质系数
    quality_coeff = {
        "白": 1.0,
        "绿": 2.0,
        "蓝": 5.0,
        "紫": 15.0,
        "金": 50.0,
    }.get(material["quality"], 1.0)
    
    # 数量系数
    quantity_coeff = material["quantity"] / 100.0
    
    # 类型系数（灵石最便宜，其他材料稍贵）
    type_coeff = 1.0
    if "灵石" not in material["name"]:
        type_coeff = 1.5
    
    # 境界系数
    realm_coeff = 2.0 ** material["realm_min"]
    
    # 基础价格
    base_price = 20 * quality_coeff * quantity_coeff * type_coeff * realm_coeff
    
    # 楼层系数
    floor_multiplier = FLOOR_PRICE_MULTIPLIER.get(floor, 1.0)
    
    # 最终价格
    final_price = int(base_price * floor_multiplier)
    
    return max(20, final_price)

# ==================== 玩家藏宝阁状态 ====================
player_treasure = {
    "current_floor": 0,  # 当前所在楼层（0-8）
    "last_visit": {},    # 各楼层最后访问时间（用于刷新商品）
    "inventory": {       # 已购买的商品
        "gongfa": [],    # 功法ID列表
        "equipment": [], # 装备ID列表
        "pills": [],     # 丹药ID列表
        "materials": [], # 材料ID列表
    },
}

# ==================== 楼层商品缓存 ====================
floor_goods_cache = {}

def get_floor_goods(floor, force_refresh=False):
    """获取指定楼层的所有商品
    返回：{
        "gongfa": [(gongfa_id, price), ...],
        "equipment": [(equipment_dict, price), ...],
        "pills": [(pill_dict, price), ...],
        "materials": [(material_dict, price), ...],
    }
    """
    # 检查缓存
    cache_key = f"floor_{floor}"
    if not force_refresh and cache_key in floor_goods_cache:
        return floor_goods_cache[cache_key]
    
    # 生成商品
    goods = {
        "gongfa": [],
        "equipment": [],
        "pills": [],
        "materials": [],
    }
    
    # 功法（6个）
    gongfa_ids = generate_floor_gongfas(floor, 6)
    for gid in gongfa_ids:
        price = calculate_gongfa_price(gid, floor)
        goods["gongfa"].append((gid, price))
    
    # 装备（6个）
    equipments = generate_equipment(floor, 6)
    for equip in equipments:
        price = calculate_equipment_price(equip, floor)
        goods["equipment"].append((equip, price))
    
    # 丹药（6个）
    pills = generate_pills(floor, 6)
    for pill in pills:
        price = calculate_pill_price(pill, floor)
        goods["pills"].append((pill, price))
    
    # 材料（6个）
    materials = generate_materials(floor, 6)
    for material in materials:
        price = calculate_material_price(material, floor)
        goods["materials"].append((material, price))
    
    # 缓存
    floor_goods_cache[cache_key] = goods
    return goods

def can_enter_floor(floor, player_realm_index):
    """检查玩家是否可以进入指定楼层"""
    required_realm = FLOOR_REQUIREMENTS.get(floor, 0)
    return player_realm_index >= required_realm

def buy_gongfa(gongfa_id, floor, player_spirit_stones):
    """购买功法"""
    price = calculate_gongfa_price(gongfa_id, floor)
    
    if player_spirit_stones < price:
        return False, "灵石不足"
    
    # 扣除灵石
    # 这里需要与主游戏系统的灵石系统对接
    # 暂时返回成功
    
    # 添加到库存
    player_treasure["inventory"]["gongfa"].append(gongfa_id)
    
    return True, f"成功购买功法，消耗{price}灵石"

def buy_equipment(equipment, floor, player_spirit_stones):
    """购买装备"""
    price = calculate_equipment_price(equipment, floor)
    
    if player_spirit_stones < price:
        return False, "灵石不足"
    
    # 扣除灵石
    # 暂时返回成功
    
    # 添加到库存
    player_treasure["inventory"]["equipment"].append(equipment["id"])
    
    return True, f"成功购买装备，消耗{price}灵石"

def buy_pill(pill, floor, player_spirit_stones):
    """购买丹药"""
    price = calculate_pill_price(pill, floor)
    
    if player_spirit_stones < price:
        return False, "灵石不足"
    
    # 扣除灵石
    # 暂时返回成功
    
    # 添加到库存
    player_treasure["inventory"]["pills"].append(pill["id"])
    
    return True, f"成功购买丹药，消耗{price}灵石"

def buy_material(material, floor, player_spirit_stones):
    """购买材料"""
    price = calculate_material_price(material, floor)
    
    if player_spirit_stones < price:
        return False, "灵石不足"
    
    # 扣除灵石
    # 暂时返回成功
    
    # 添加到库存
    player_treasure["inventory"]["materials"].append(material["id"])
    
    return True, f"成功购买材料，消耗{price}灵石"

# ==================== 保存/加载 ====================
import json
import os

def save_data():
    """保存藏宝阁数据"""
    data = {
        "player_treasure": player_treasure,
    }
    
    try:
        with open("treasure_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存藏宝阁数据失败: {e}")
        return False

def load_data():
    """加载藏宝阁数据"""
    global player_treasure
    
    if not os.path.exists("treasure_data.json"):
        return False
    
    try:
        with open("treasure_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        player_treasure = data.get("player_treasure", player_treasure)
        return True
    except Exception as e:
        print(f"加载藏宝阁数据失败: {e}")
        return False

# 初始化加载
load_data()

# ==================== 辅助函数 ====================

def get_gongfa_by_id(gid):
    """根据ID获取功法"""
    for g in GONGFA_POOL:
        if g["id"] == gid:
            return g
    return None