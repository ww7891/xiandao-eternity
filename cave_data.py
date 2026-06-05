"""
洞府系统数据模块
包含灵药园、聚灵阵、道童等系统
"""

import time
import json
import os

# ==================== 灵药种子数据 ====================
HERB_SEEDS = {
    "凝露草": {
        "name": "凝露草",
        "growth_time": 3600,  # 1小时
        "exp_gain": 10,
        "yield_min": 2,
        "yield_max": 4,
        "quality": "普通",
        "desc": "基础灵草，蕴含微弱灵气",
        "color": (100, 200, 100),
    },
    "赤阳花": {
        "name": "赤阳花", 
        "growth_time": 7200,  # 2小时
        "exp_gain": 20,
        "yield_min": 1,
        "yield_max": 3,
        "quality": "良好",
        "desc": "火属性灵花，可炼制火系丹药",
        "color": (255, 100, 50),
    },
    "寒玉莲": {
        "name": "寒玉莲",
        "growth_time": 14400,  # 4小时
        "exp_gain": 40,
        "yield_min": 1,
        "yield_max": 2,
        "quality": "优秀",
        "desc": "水属性灵莲，炼制冰系丹药的珍稀材料",
        "color": (100, 200, 255),
    },
    "金线参": {
        "name": "金线参",
        "growth_time": 28800,  # 8小时
        "exp_gain": 80,
        "yield_min": 1,
        "yield_max": 2,
        "quality": "稀有",
        "desc": "金属性灵参，可炼制突破丹药",
        "color": (255, 200, 50),
    },
    "地心灵芝": {
        "name": "地心灵芝",
        "growth_time": 43200,  # 12小时
        "exp_gain": 120,
        "yield_min": 1,
        "yield_max": 1,
        "quality": "传说",
        "desc": "土属性灵芝，炼制延寿丹药的至宝",
        "color": (180, 140, 100),
    },
}

# ==================== 灵药园等级 ====================
HERB_GARDEN_LEVELS = [
    {"level": 1, "name": "初阶药田", "field_count": 2, "exp_required": 0, "desc": "初始两块药田"},
    {"level": 2, "name": "中阶药田", "field_count": 3, "exp_required": 100, "desc": "解锁第三块药田"},
    {"level": 3, "name": "高阶药田", "field_count": 4, "exp_required": 300, "desc": "解锁第四块药田"},
    {"level": 4, "name": "灵阶药田", "field_count": 5, "exp_required": 600, "desc": "解锁第五块药田"},
    {"level": 5, "name": "仙阶药田", "field_count": 6, "exp_required": 1000, "desc": "解锁第六块药田"},
    {"level": 6, "name": "神阶药田", "field_count": 7, "exp_required": 1500, "desc": "解锁第七块药田"},
    {"level": 7, "name": "圣阶药田", "field_count": 8, "exp_required": 2100, "desc": "解锁第八块药田"},
    {"level": 8, "name": "天阶药田", "field_count": 9, "exp_required": 2800, "desc": "解锁第九块药田"},
    {"level": 9, "name": "帝阶药田", "field_count": 10, "exp_required": 3600, "desc": "解锁第十块药田"},
    {"level": 10, "name": "道阶药田", "field_count": 12, "exp_required": 4500, "desc": "解锁十二块药田"},
]

# ==================== 聚灵阵等级 ====================
SPIRIT_ARRAY_LEVELS = [
    {"level": 1, "name": "初阶聚灵阵", "cultivation_boost": 0.01, "materials_required": {"spirit_stone": 10}, "desc": "修为获取率 +1%"},
    {"level": 2, "name": "中阶聚灵阵", "cultivation_boost": 0.02, "materials_required": {"spirit_stone": 30, "demon_core": 1}, "desc": "修为获取率 +2%"},
    {"level": 3, "name": "高阶聚灵阵", "cultivation_boost": 0.03, "materials_required": {"spirit_stone": 60, "demon_core": 3}, "desc": "修为获取率 +3%"},
    {"level": 4, "name": "灵阶聚灵阵", "cultivation_boost": 0.04, "materials_required": {"spirit_stone": 100, "demon_core": 6}, "desc": "修为获取率 +4%"},
    {"level": 5, "name": "仙阶聚灵阵", "cultivation_boost": 0.05, "materials_required": {"spirit_stone": 150, "demon_core": 10}, "desc": "修为获取率 +5%"},
    {"level": 6, "name": "神阶聚灵阵", "cultivation_boost": 0.06, "materials_required": {"spirit_stone": 210, "demon_core": 15}, "desc": "修为获取率 +6%"},
    {"level": 7, "name": "圣阶聚灵阵", "cultivation_boost": 0.07, "materials_required": {"spirit_stone": 280, "demon_core": 21}, "desc": "修为获取率 +7%"},
    {"level": 8, "name": "天阶聚灵阵", "cultivation_boost": 0.08, "materials_required": {"spirit_stone": 360, "demon_core": 28}, "desc": "修为获取率 +8%"},
    {"level": 9, "name": "帝阶聚灵阵", "cultivation_boost": 0.09, "materials_required": {"spirit_stone": 450, "demon_core": 36}, "desc": "修为获取率 +9%"},
    {"level": 10, "name": "道阶聚灵阵", "cultivation_boost": 0.10, "materials_required": {"spirit_stone": 550, "demon_core": 45}, "desc": "修为获取率 +10%"},
]

# ==================== 道童系统 ====================
APPRENTICE_DATA = {
    "duration": 259200,  # 3天（秒）
    "ad_required": True,
    "auto_plant": True,
    "auto_harvest": True,
    "desc": "雇佣道童后，3天内自动播种与收获灵药",
}

# ==================== 玩家洞府状态 ====================
player_cave = {
    # 灵药园
    "herb_garden": {
        "level": 1,
        "exp": 0,
        "fields": [],  # 每块药田状态
        "seeds_inventory": {},  # 种子库存
        "herbs_inventory": {},  # 收获的灵药库存
    },
    # 聚灵阵
    "spirit_array": {
        "level": 0,  # 0表示未建造
        "materials_collected": {},  # 已收集的材料
    },
    # 道童
    "apprentice": {
        "active": False,
        "start_time": 0,
        "end_time": 0,
    },
    # 时间戳
    "last_update": time.time(),
}

# 初始化药田
def init_fields():
    """根据当前等级初始化药田"""
    level_info = HERB_GARDEN_LEVELS[player_cave["herb_garden"]["level"] - 1]
    field_count = level_info["field_count"]
    current_fields = player_cave["herb_garden"]["fields"]
    
    # 如果药田数量不足，补充空药田
    while len(current_fields) < field_count:
        current_fields.append({
            "seed": None,
            "plant_time": 0,
            "growth_progress": 0,  # 0-100
            "harvestable": False,
        })
    
    # 如果药田数量过多，截断（降级时）
    player_cave["herb_garden"]["fields"] = current_fields[:field_count]

# 初始化
init_fields()

# ==================== 灵药园功能 ====================

def plant_seed(field_index, seed_name):
    """在指定药田种植种子"""
    if field_index >= len(player_cave["herb_garden"]["fields"]):
        return False, "药田不存在"
    
    field = player_cave["herb_garden"]["fields"][field_index]
    if field["seed"] is not None:
        return False, "药田已被占用"
    
    # 检查种子库存
    if seed_name not in player_cave["herb_garden"]["seeds_inventory"]:
        return False, "没有该种子"
    if player_cave["herb_garden"]["seeds_inventory"][seed_name] <= 0:
        return False, "种子数量不足"
    
    # 消耗种子
    player_cave["herb_garden"]["seeds_inventory"][seed_name] -= 1
    if player_cave["herb_garden"]["seeds_inventory"][seed_name] == 0:
        del player_cave["herb_garden"]["seeds_inventory"][seed_name]
    
    # 种植
    seed_data = HERB_SEEDS[seed_name]
    field["seed"] = seed_name
    field["plant_time"] = time.time()
    field["growth_progress"] = 0
    field["harvestable"] = False
    
    return True, f"成功种植 {seed_name}"

def harvest_field(field_index):
    """收获指定药田"""
    if field_index >= len(player_cave["herb_garden"]["fields"]):
        return False, "药田不存在"
    
    field = player_cave["herb_garden"]["fields"][field_index]
    if field["seed"] is None:
        return False, "药田为空"
    
    if not field["harvestable"]:
        return False, "灵药尚未成熟"
    
    # 收获
    seed_name = field["seed"]
    seed_data = HERB_SEEDS[seed_name]
    
    # 计算产量
    import random
    yield_qty = random.randint(seed_data["yield_min"], seed_data["yield_max"])
    
    # 添加到库存
    if seed_name not in player_cave["herb_garden"]["herbs_inventory"]:
        player_cave["herb_garden"]["herbs_inventory"][seed_name] = 0
    player_cave["herb_garden"]["herbs_inventory"][seed_name] += yield_qty
    
    # 获得经验
    player_cave["herb_garden"]["exp"] += seed_data["exp_gain"]
    
    # 检查升级
    check_level_up()
    
    # 清空药田
    field["seed"] = None
    field["plant_time"] = 0
    field["growth_progress"] = 0
    field["harvestable"] = False
    
    return True, f"收获 {seed_name} ×{yield_qty}，获得 {seed_data['exp_gain']} 经验"

def update_growth():
    """更新所有药田的生长进度"""
    current_time = time.time()
    
    for field in player_cave["herb_garden"]["fields"]:
        if field["seed"] is None or field["harvestable"]:
            continue
        
        seed_name = field["seed"]
        seed_data = HERB_SEEDS[seed_name]
        
        elapsed = current_time - field["plant_time"]
        progress = min(elapsed / seed_data["growth_time"] * 100, 100)
        
        field["growth_progress"] = progress
        if progress >= 100:
            field["harvestable"] = True

def check_level_up():
    """检查灵药园是否升级"""
    current_level = player_cave["herb_garden"]["level"]
    if current_level >= len(HERB_GARDEN_LEVELS):
        return False
    
    next_level_info = HERB_GARDEN_LEVELS[current_level]  # 当前等级的下一个等级
    if player_cave["herb_garden"]["exp"] >= next_level_info["exp_required"]:
        player_cave["herb_garden"]["level"] = current_level + 1
        init_fields()  # 重新初始化药田
        return True
    return False

def add_seed(seed_name, quantity=1):
    """添加种子到库存"""
    if seed_name not in player_cave["herb_garden"]["seeds_inventory"]:
        player_cave["herb_garden"]["seeds_inventory"][seed_name] = 0
    player_cave["herb_garden"]["seeds_inventory"][seed_name] += quantity

# ==================== 聚灵阵功能 ====================

def upgrade_spirit_array():
    """升级聚灵阵"""
    current_level = player_cave["spirit_array"]["level"]
    if current_level >= len(SPIRIT_ARRAY_LEVELS):
        return False, "已达最高等级"
    
    next_level_info = SPIRIT_ARRAY_LEVELS[current_level]
    
    # 检查材料
    for material, required in next_level_info["materials_required"].items():
        if player_cave["spirit_array"]["materials_collected"].get(material, 0) < required:
            return False, f"材料不足：{material}"
    
    # 消耗材料
    for material, required in next_level_info["materials_required"].items():
        player_cave["spirit_array"]["materials_collected"][material] -= required
        if player_cave["spirit_array"]["materials_collected"][material] == 0:
            del player_cave["spirit_array"]["materials_collected"][material]
    
    # 升级
    player_cave["spirit_array"]["level"] = current_level + 1
    return True, f"成功升级到 {SPIRIT_ARRAY_LEVELS[current_level]['name']}"

def add_material(material_name, quantity=1):
    """添加材料到聚灵阵材料库"""
    if material_name not in player_cave["spirit_array"]["materials_collected"]:
        player_cave["spirit_array"]["materials_collected"][material_name] = 0
    player_cave["spirit_array"]["materials_collected"][material_name] += quantity

def get_cultivation_boost():
    """获取聚灵阵的修炼加成"""
    if player_cave["spirit_array"]["level"] == 0:
        return 0.0
    return SPIRIT_ARRAY_LEVELS[player_cave["spirit_array"]["level"] - 1]["cultivation_boost"]

# ==================== 道童功能 ====================

def hire_apprentice():
    """雇佣道童（看广告）"""
    if player_cave["apprentice"]["active"]:
        return False, "道童已在工作中"
    
    # 这里模拟看广告成功
    current_time = time.time()
    player_cave["apprentice"]["active"] = True
    player_cave["apprentice"]["start_time"] = current_time
    player_cave["apprentice"]["end_time"] = current_time + APPRENTICE_DATA["duration"]
    
    return True, "成功雇佣道童，3天内自动管理灵药园"

def update_apprentice():
    """更新道童状态"""
    if not player_cave["apprentice"]["active"]:
        return
    
    current_time = time.time()
    if current_time >= player_cave["apprentice"]["end_time"]:
        player_cave["apprentice"]["active"] = False
        player_cave["apprentice"]["start_time"] = 0
        player_cave["apprentice"]["end_time"] = 0

def auto_manage_garden():
    """道童自动管理灵药园"""
    if not player_cave["apprentice"]["active"]:
        return
    
    # 自动收获
    for i, field in enumerate(player_cave["herb_garden"]["fields"]):
        if field["harvestable"]:
            harvest_field(i)
    
    # 自动种植（如果有种子）
    for i, field in enumerate(player_cave["herb_garden"]["fields"]):
        if field["seed"] is None and player_cave["herb_garden"]["seeds_inventory"]:
            # 选择第一个可用的种子
            seed_name = next(iter(player_cave["herb_garden"]["seeds_inventory"]))
            plant_seed(i, seed_name)

# ==================== 保存/加载 ====================

def save_data():
    """保存洞府数据"""
    data = {
        "herb_garden": player_cave["herb_garden"],
        "spirit_array": player_cave["spirit_array"],
        "apprentice": player_cave["apprentice"],
        "last_update": time.time(),
    }
    
    try:
        with open("cave_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存洞府数据失败: {e}")
        return False

def load_data():
    """加载洞府数据"""
    global player_cave
    
    if not os.path.exists("cave_data.json"):
        return False
    
    try:
        with open("cave_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 更新数据
        player_cave["herb_garden"] = data.get("herb_garden", player_cave["herb_garden"])
        player_cave["spirit_array"] = data.get("spirit_array", player_cave["spirit_array"])
        player_cave["apprentice"] = data.get("apprentice", player_cave["apprentice"])
        player_cave["last_update"] = data.get("last_update", time.time())
        
        # 重新初始化药田
        init_fields()
        
        # 更新道童状态
        update_apprentice()
        
        return True
    except Exception as e:
        print(f"加载洞府数据失败: {e}")
        return False

# ==================== 主更新函数 ====================

def update_all():
    """更新所有洞府系统"""
    # 更新生长进度
    update_growth()
    
    # 更新道童状态
    update_apprentice()
    
    # 道童自动管理
    auto_manage_garden()
    
    # 保存数据
    save_data()

# 初始化加载
load_data()