"""
历练之路 - 18张地图定义
每个大境界对应2张地图
"""

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "炼虚", "合体", "大乘", "渡劫"]

MAPS = [
    # 练气期 (地图0-1)
    {"id": 0, "name": "青竹林", "realm": 0, "desc": "练气修士初次历练之地，妖物尚弱", "bg_color": (180, 200, 170)},
    {"id": 1, "name": "乱石岗", "realm": 0, "desc": "碎石遍布的荒岗，石妖盘踞", "bg_color": (170, 165, 155)},

    # 筑基期 (地图2-3)
    {"id": 2, "name": "黑风洞", "realm": 1, "desc": "阴风阵阵的洞穴，血蝠成群", "bg_color": (100, 90, 80)},
    {"id": 3, "name": "毒蝎谷", "realm": 1, "desc": "毒雾弥漫的山谷，蝎尾兽出没", "bg_color": (130, 150, 100)},

    # 金丹期 (地图4-5)
    {"id": 4, "name": "古墓陵", "realm": 2, "desc": "阴森的古代陵墓，僵尸横行", "bg_color": (90, 85, 80)},
    {"id": 5, "name": "幽冥涧", "realm": 2, "desc": "深不见底的幽谷，幽魂飘荡", "bg_color": (60, 60, 90)},

    # 元婴期 (地图6-7)
    {"id": 6, "name": "魔修岭", "realm": 3, "desc": "魔修聚集的山岭，邪气冲天", "bg_color": (100, 80, 110)},
    {"id": 7, "name": "邪灵殿", "realm": 3, "desc": "废弃的宫殿遗迹，邪灵盘踞", "bg_color": (80, 70, 90)},

    # 化神期 (地图8-9)
    {"id": 8, "name": "雷鹰崖", "realm": 4, "desc": "雷电交加的悬崖，雷鹰翱翔", "bg_color": (80, 90, 120)},
    {"id": 9, "name": "冰蟒潭", "realm": 4, "desc": "寒气刺骨的深潭，冰蟒潜伏", "bg_color": (140, 170, 200)},

    # 炼虚期 (地图10-11)
    {"id": 10, "name": "虚空裂隙", "realm": 5, "desc": "空间破碎之地，虚空兽穿梭", "bg_color": (70, 100, 110)},
    {"id": 11, "name": "幻影森林", "realm": 5, "desc": "虚实难辨的森林，幻影妖迷惑", "bg_color": (100, 120, 100)},

    # 合体期 (地图12-13)
    {"id": 12, "name": "天魔战场", "realm": 6, "desc": "上古天魔大战遗迹，天魔兵残留", "bg_color": (120, 70, 80)},
    {"id": 13, "name": "修罗道", "realm": 6, "desc": "通往修罗界的大门，修罗横行", "bg_color": (140, 60, 60)},

    # 大乘期 (地图14-15)
    {"id": 14, "name": "金甲要塞", "realm": 7, "desc": "天兵守护的要塞，金甲卫镇守", "bg_color": (180, 160, 80)},
    {"id": 15, "name": "灵兽园", "realm": 7, "desc": "远古灵兽栖息之地，灵兽狂暴", "bg_color": (140, 160, 100)},

    # 渡劫期 (地图16-17)
    {"id": 16, "name": "天雷台", "realm": 8, "desc": "引动天雷的祭台，天雷灵肆虐", "bg_color": (80, 80, 100)},
    {"id": 17, "name": "劫火炼狱", "realm": 8, "desc": "渡劫之火燃烧的炼狱，灭世魔潜伏", "bg_color": (160, 60, 40)},
]

# 玩家当前解锁的地图ID（初始只有地图0）
unlocked_maps = {0}  # 集合，存储已解锁的地图ID


def get_map(map_id):
    """获取地图数据"""
    for m in MAPS:
        if m["id"] == map_id:
            return m
    return None


def unlock_map(map_id):
    """解锁地图"""
    if map_id < len(MAPS):
        unlocked_maps.add(map_id)


def get_unlocked_maps():
    """获取所有已解锁的地图列表"""
    return [m for m in MAPS if m["id"] in unlocked_maps]