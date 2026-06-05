"""
职业数据定义
剑修 / 法修 / 刀修
"""

# 当前选择的职业（灵根抽取后由角色选择界面写入）
current_profession = None  # "sword" / "mage" / "blade"

PROFESSIONS = {
    "sword": {
        "id": "sword",
        "name": "剑修",
        "subtitle": "御剑之道，以快制胜",
        "description": "以气御剑，剑光如雨。攻击速度极快，\n连续射出法剑贯穿敌人，适合风筝游走。",
        "attack_name": "御剑术",
        "attack_interval": 0.6,    # 攻击间隔（秒）
        "attack_damage": 8,        # 基础伤害
        "attack_speed": 12,        # 弹道速度
        "attack_type": "projectile",  # 弹道类型
        "attack_color": (100, 180, 255),  # 攻击颜色
        "color": (100, 180, 255),  # 玩家颜色
        "attack_size": (18, 4),    # 攻击尺寸
        "aoe_range": 0,            # 无范围伤害
    },
    "mage": {
        "id": "mage",
        "name": "法修",
        "subtitle": "法术之道，毁天灭地",
        "description": "引天地灵气化为龙卷飓风。攻击间隔较长，\n但龙卷风会持续伤害范围内所有敌人。",
        "attack_name": "飓风术",
        "attack_interval": 2.0,    # 攻击间隔（秒）
        "attack_damage": 25,       # 基础伤害
        "attack_speed": 3,         # 移动速度慢
        "attack_type": "aoe_persist",  # 持续AOE
        "attack_color": (180, 220, 255),
        "color": (180, 220, 255),  # 玩家颜色
        "attack_size": (60, 60),   # 龙卷风范围
        "aoe_range": 60,           # AOE半径
    },
    "blade": {
        "id": "blade",
        "name": "刀修",
        "subtitle": "刀法之道，横扫千军",
        "description": "一力降十会，刀气纵横。攻击间隔适中，\n挥刀造成中等范围的扇形AOE伤害。",
        "attack_name": "横扫千军",
        "attack_interval": 0.8,    # 攻击间隔（秒）
        "attack_damage": 15,       # 基础伤害
        "attack_speed": 0,         # 即时伤害
        "attack_type": "slash",    # 扇形斩击
        "attack_color": (255, 200, 100),
        "color": (255, 200, 100),  # 玩家颜色
        "attack_size": (120, 0),   # 范围角度
        "aoe_range": 120,          # 扇形半径
    },
}


def get_profession():
    """获取当前职业数据"""
    if current_profession is None:
        return None
    return PROFESSIONS.get(current_profession)