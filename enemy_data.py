"""
怪物数据定义
按境界（练气→渡劫）分9档，每档有小怪、精英怪、Boss
"""

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "炼虚", "合体", "大乘", "渡劫"]

# ==================== 怪物模板 ====================
# 每层境界的怪物属性 = (小怪_HP, 小怪_伤害, 小怪_速度, 小怪_颜色, 精英_HP系数, 精英_伤害系数, Boss数据)

ENEMY_TEMPLATES = {
    0: {  # 练气期
        "mob_hp": 1, "mob_dmg": 3, "mob_speed": 1.2, "mob_color": (140, 150, 140),
        "elite_mult": 3, "elite_color": (160, 140, 100),
        "boss": {"name": "灵龟", "hp": 300, "dmg": 8, "speed": 1.0, "size": 30, "color": (120, 100, 80)},
        "mob_names": ["石妖", "土精", "岩虫"],
        "elite_names": ["巨型石妖", "岩甲兽"],
    },
    1: {  # 筑基期
        "mob_hp": 1, "mob_dmg": 6, "mob_speed": 1.4, "mob_color": (160, 150, 130),
        "elite_mult": 3.5, "elite_color": (180, 150, 90),
        "boss": {"name": "灵龟", "hp": 600, "dmg": 14, "speed": 1.8, "size": 32, "color": (180, 50, 50)},
        "mob_names": ["血蝠", "毒蝎", "幽狼"],
        "elite_names": ["巨型血蝠", "蝎尾兽"],
    },
    2: {  # 金丹期
        "mob_hp": 1, "mob_dmg": 10, "mob_speed": 1.6, "mob_color": (170, 160, 100),
        "elite_mult": 4, "elite_color": (190, 160, 80),
        "boss": {"name": "灵龟", "hp": 1000, "dmg": 22, "speed": 1.2, "size": 34, "color": (200, 170, 70)},
        "mob_names": ["僵尸", "骷髅兵", "幽魂"],
        "elite_names": ["尸将", "骸骨骑士"],
    },
    3: {  # 元婴期
        "mob_hp": 1, "mob_dmg": 16, "mob_speed": 1.8, "mob_color": (130, 110, 170),
        "elite_mult": 4.5, "elite_color": (160, 120, 200),
        "boss": {"name": "灵龟", "hp": 1600, "dmg": 32, "speed": 1.5, "size": 36, "color": (150, 50, 200)},
        "mob_names": ["魔修", "邪灵", "煞鬼"],
        "elite_names": ["魔将", "邪灵使"],
    },
    4: {  # 化神期
        "mob_hp": 1, "mob_dmg": 24, "mob_speed": 2.0, "mob_color": (100, 130, 180),
        "elite_mult": 5, "elite_color": (120, 150, 210),
        "boss": {"name": "化神邪君", "hp": 2500, "dmg": 45, "speed": 1.8, "size": 38, "color": (30, 80, 200)},
        "mob_names": ["雷鹰", "冰蟒", "火猿"],
        "elite_names": ["雷鹏", "冰蛟"],
    },
    5: {  # 炼虚期
        "mob_hp": 1, "mob_dmg": 34, "mob_speed": 2.2, "mob_color": (90, 140, 140),
        "elite_mult": 5.5, "elite_color": (100, 170, 170),
        "boss": {"name": "炼虚妖皇", "hp": 3800, "dmg": 60, "speed": 2.0, "size": 40, "color": (20, 150, 150)},
        "mob_names": ["虚空兽", "幻影妖", "噬灵虫"],
        "elite_names": ["虚空领主", "幻影女妖"],
    },
    6: {  # 合体期
        "mob_hp": 1, "mob_dmg": 48, "mob_speed": 2.4, "mob_color": (150, 100, 120),
        "elite_mult": 6, "elite_color": (180, 110, 140),
        "boss": {"name": "合体天魔", "hp": 5500, "dmg": 80, "speed": 2.2, "size": 42, "color": (200, 30, 100)},
        "mob_names": ["天魔兵", "修罗", "夜叉"],
        "elite_names": ["天魔将", "修罗王"],
    },
    7: {  # 大乘期
        "mob_hp": 1, "mob_dmg": 65, "mob_speed": 2.6, "mob_color": (180, 140, 80),
        "elite_mult": 6.5, "elite_color": (210, 160, 70),
        "boss": {"name": "大乘妖帝", "hp": 8000, "dmg": 105, "speed": 2.5, "size": 44, "color": (220, 150, 30)},
        "mob_names": ["金甲卫", "天兵", "灵兽"],
        "elite_names": ["金甲将军", "天将"],
    },
    8: {  # 渡劫期
        "mob_hp": 1, "mob_dmg": 88, "mob_speed": 2.8, "mob_color": (200, 80, 80),
        "elite_mult": 7, "elite_color": (230, 60, 60),
        "boss": {"name": "灵龟", "hp": 12000, "dmg": 140, "speed": 2.8, "size": 48, "color": (255, 200, 50)},
        "mob_names": ["天雷灵", "劫火兽", "灭世魔"],
        "elite_names": ["天雷将", "劫火领主"],
    },
}


def get_realm_enemies(realm_index):
    """获取指定境界的怪物模板"""
    return ENEMY_TEMPLATES.get(realm_index, ENEMY_TEMPLATES[0])