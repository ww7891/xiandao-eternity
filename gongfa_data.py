"""
功法数据模块 - 完整版
统一分练气、筑基、金丹、元婴、化神、渡劫、大乘、真仙八个境界
每个境界分白、绿、蓝、紫、金五阶
分三类：灵技、内经、心法
灵技伤害公式：百分比*攻击力 + 固定伤害
"""

import random

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "渡劫", "大乘", "真仙"]
QUALITIES = ["白", "绿", "蓝", "紫", "金"]
QUALITY_BONUS = {"白": 1.0, "绿": 1.2, "蓝": 1.5, "紫": 2.0, "金": 3.0}
QUALITY_MIN_REALM = {"白": 0, "绿": 0, "蓝": 1, "紫": 3, "金": 5}
QUALITY_DISPLAY_COLORS = {
    "白": (180, 180, 180),
    "绿": (100, 200, 100),
    "蓝": (100, 150, 255),
    "紫": (200, 100, 255),
    "金": (255, 200, 80),
}

FIVE_ELEMENTS = ["金", "木", "水", "火", "土"]

# 别名，兼容其他模块
ELEMENTS = FIVE_ELEMENTS
ELEMENT_COLORS = {
    "金": (255, 215, 0),
    "木": (100, 200, 100),
    "水": (100, 150, 255),
    "火": (255, 80, 80),
    "土": (180, 140, 80),
}

# 元素克制：金克木、木克土、土克水、水克火、火克金
ELEMENT_COUNTER = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}

# 灵根配置概率
SPIRITUAL_ROOT_PROB = {
    "五灵根": 40, "四灵根": 25, "三灵根": 17,
    "双灵根": 12, "单灵根": 5, "天灵根": 1
}

# 灵根详细配置
SPIRITUAL_ROOT_CONFIG = {
    "五灵根": {"desc": "五行俱全，资质平庸，但胜在均衡", "num": 5, "bonus": 1.0},
    "四灵根": {"desc": "四系灵根，略有天赋，可修四系功法", "num": 4, "bonus": 1.2},
    "三灵根": {"desc": "三系灵根，颇具资质，修炼速度较快", "num": 3, "bonus": 1.4},
    "双灵根": {"desc": "双系灵根，天赋卓越，功法威力大增", "num": 2, "bonus": 1.6},
    "单灵根": {"desc": "单系灵根，万中无一，同阶无敌", "num": 1, "bonus": 1.8},
    "天灵根": {"desc": "天赐灵根，传说中的资质，可越阶战斗", "num": 1, "bonus": 2.5},
}


def generate_large_techniques():
    """批量生成所有功法"""
    techs = []
    tid = 1

    # 境界基础数值
    realm_bases = [
        (0, "练气", 30, 10), (1, "筑基", 80, 30), (2, "金丹", 200, 80),
        (3, "元婴", 500, 200), (4, "化神", 1200, 500), (5, "渡劫", 3000, 1200),
        (6, "大乘", 8000, 3000), (7, "真仙", 20000, 8000)
    ]

    # 灵技模板：每个元素 + 每个品质 + 每个境界
    lingji_templates = {
        "火": ["火剑诀", "烈焰斩", "焚天掌", "火凤燎原", "炎龙破", "天火坠", "九阳焚天", "南明离火"],
        "水": ["寒冰诀", "冰封万里", "玄水掌", "冰魄神光", "水龙卷", "冰棱刺", "北冥玄冰", "弱水三千"],
        "金": ["金锋诀", "万剑归宗", "裂金斩", "金刚伏魔", "金光刃", "破天剑罡", "白虎裂天", "太白剑诀"],
        "木": ["青木诀", "万木逢春", "藤鞭术", "青莲剑气", "枯木逢春", "木龙吟", "乙木神光", "太乙青木"],
        "土": ["厚土诀", "山崩地裂", "石破天惊", "大地之怒", "流沙葬", "岩龙变", "戊土神罡", "麒麟镇岳"]
    }

    neijing_templates = {
        "火": ["焚天诀", "烈焰心经", "炎帝真解"],
        "水": ["冰心诀", "玄水真经", "北冥心法"],
        "金": ["金刚经", "太白剑经", "白帝真解"],
        "木": ["青帝内经", "长春真解", "乙木心经"],
        "土": ["玄黄诀", "厚土心经", "麒麟真解"]
    }

    xinfa_templates = {
        "火": ["朱雀心法", "离火真意"],
        "水": ["玄武心印", "坎水心印"],
        "金": ["白虎心印", "兑金真意"],
        "木": ["青龙心印", "震木真意"],
        "土": ["麒麟心印", "艮土真意"]
    }

    for realm_idx, realm_name, base_pct, base_fixed in realm_bases:
        for q in QUALITIES:
            # 品质境界限制
            quality_bonus_mult = QUALITY_BONUS[q]

            for elem in FIVE_ELEMENTS:

                # === 灵技 ===
                for tmpl_idx, tmpl_name in enumerate(lingji_templates[elem]):
                    name = f"{realm_name}·{q}·{tmpl_name}"
                    
                    pct_mult = 1.0 + realm_idx * 0.8
                    pct = int(base_pct * quality_bonus_mult * pct_mult)
                    fixed = int(base_fixed * quality_bonus_mult * (1 + realm_idx * 0.5))
                    
                    techs.append({
                        "id": tid, "name": name,
                        "type": "灵技", "element": elem,
                        "quality": q, "realm_min": realm_idx,
                        "realm_name": realm_name,
                        "damage_pct": pct, "damage_fixed": fixed,
                        "desc": f"[{elem}]灵技：造成{pct}%攻击+{fixed}点{elem}属性伤害",
                        "template": tmpl_name,
                    })
                    tid += 1

            for elem in FIVE_ELEMENTS:
                # === 内经 ===
                hp_bonus = int((50 + realm_idx * 80) * quality_bonus_mult)
                mp_bonus = int((30 + realm_idx * 50) * quality_bonus_mult)
                
                for tmpl_name in neijing_templates[elem]:
                    name = f"{realm_name}·{q}·{tmpl_name}"
                    
                    techs.append({
                        "id": tid, "name": name,
                        "type": "内经", "element": elem,
                        "quality": q, "realm_min": realm_idx,
                        "realm_name": realm_name,
                        "hp_bonus": hp_bonus, "mp_bonus": mp_bonus,
                        "desc": f"[{elem}]内经：生命+{hp_bonus}，灵力+{mp_bonus}",
                    })
                    tid += 1

                # === 心法 ===
                atk_bonus = int((8 + realm_idx * 12) * quality_bonus_mult)
                def_bonus = int((5 + realm_idx * 8) * quality_bonus_mult)

                for tmpl_name in xinfa_templates[elem]:
                    name = f"{realm_name}·{q}·{tmpl_name}"
                    
                    techs.append({
                        "id": tid, "name": name,
                        "type": "心法", "element": elem,
                        "quality": q, "realm_min": realm_idx,
                        "realm_name": realm_name,
                        "atk_bonus": atk_bonus, "def_bonus": def_bonus,
                        "desc": f"[{elem}]心法：攻击+{atk_bonus}，防御+{def_bonus}",
                    })
                    tid += 1

    return techs


GONGFA_POOL = generate_large_techniques()

# 玩家功法状态
player_gongfa = {
    "spiritual_root": None,  # (类型, [元素列表], 加成系数)
    "equipped": {"灵技": [None] * 3, "内经": [None] * 6, "心法": [None]},
    "learned": [],  # 已学会的功法id列表
}


def roll_gongfa_drop(realm_index):
    """掉落功法：根据当前境界随机掉落"""
    candidates = []
    realm_name = REALM_NAMES[realm_index]
    
    for g in GONGFA_POOL:
        if g["realm_min"] <= realm_index and g["realm_name"] == realm_name:
            candidates.append(g)

    if not candidates:
        return None

    # 按品质权重选择
    quality_weights = {"白": 45, "绿": 30, "蓝": 15, "紫": 7, "金": 3}
    weighted = []
    w = []
    for g in candidates:
        wq = quality_weights.get(g["quality"], 1)
        weighted.append(g)
        w.append(wq)

    chosen = random.choices(weighted, weights=w, k=1)[0]
    return chosen["id"]


def get_gongfa_by_id(gid):
    for g in GONGFA_POOL:
        if g["id"] == gid:
            return g
    return None


def get_equipped_bonuses():
    """获取已装备功法的总加成"""
    total_atk = 0
    total_def = 0
    total_hp = 0
    total_mp = 0

    equipped = player_gongfa.get("equipped", {})
    
    for slot_name, slots in equipped.items():
        if isinstance(slots, list):
            for gid in slots:
                if gid:
                    g = get_gongfa_by_id(gid)
                    if g:
                        total_atk += g.get("atk_bonus", 0)
                        total_def += g.get("def_bonus", 0)
                        total_hp += g.get("hp_bonus", 0)
                        total_mp += g.get("mp_bonus", 0)
        elif slots:
            g = get_gongfa_by_id(slots)
            if g:
                total_atk += g.get("atk_bonus", 0)
                total_def += g.get("def_bonus", 0)
                total_hp += g.get("hp_bonus", 0)
                total_mp += g.get("mp_bonus", 0)

    return total_atk, total_def, total_hp, total_mp


def assign_spiritual_root():
    """分配灵根"""
    types = list(SPIRITUAL_ROOT_PROB.keys())
    weights = list(SPIRITUAL_ROOT_PROB.values())
    root_type = random.choices(types, weights=weights, k=1)[0]

    num_elements = {
        "五灵根": 5, "四灵根": 4, "三灵根": 3,
        "双灵根": 2, "单灵根": 1, "天灵根": 1
    }[root_type]

    elements = random.sample(FIVE_ELEMENTS, num_elements)
    bonus = {
        "五灵根": 1.0, "四灵根": 1.2, "三灵根": 1.4,
        "双灵根": 1.6, "单灵根": 1.8, "天灵根": 2.5
    }[root_type]

    player_gongfa["spiritual_root"] = (root_type, elements, bonus)
    return root_type, elements, bonus


# 别名
draw_spiritual_root = assign_spiritual_root