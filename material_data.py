"""
材料数据模块
- 种子：可在灵田种植获得药材
- 药材：炼丹所需
- 器材：炼器所需
- 强化材料：强化装备所需
"""

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "渡劫", "大乘", "真仙"]
QUALITIES = ["白", "绿", "蓝", "紫", "金"]
QUALITY_MULT = {"白": 1.0, "绿": 1.25, "蓝": 1.5, "紫": 1.75, "金": 2.0}

# 基础种子名称
SEED_TYPES = [
    "灵参", "灵芝", "龙血草", "冰魄花", "火灵芝",
    "雷击木苗", "养魂草", "天元果树", "金莲", "玄阴藤"
]

# 基础器材名称
EQUIP_MATERIAL_TYPES = [
    "玄铁", "寒玉", "炎晶", "风铜", "雷石",
    "魂钢", "天星沙", "龙鳞", "凤羽", "灵脉石"
]

# 基础强化材料名称
ENHANCE_MATERIAL_TYPES = [
    "强化石", "淬灵石", "融灵液", "天炼符", "道纹碎片"
]


def generate_all_materials():
    """生成全部材料"""
    materials = []
    mid = 1

    realm_base = [
        (0, "练气", 10), (1, "筑基", 25), (2, "金丹", 60),
        (3, "元婴", 150), (4, "化神", 400), (5, "渡劫", 1000),
        (6, "大乘", 2500), (7, "真仙", 6000)
    ]

    for realm_idx, realm_name, base_val in realm_base:
        for q in QUALITIES:
            quality_name = q
            mult = QUALITY_MULT[q]
            val = int(base_val * mult)

            # 种子
            for i, seed_name in enumerate(SEED_TYPES[:3 + realm_idx]):
                materials.append({
                    "id": mid,
                    "name": f"{realm_name}·{quality_name}·{seed_name}种",
                    "type": "种子",
                    "quality": q,
                    "realm": realm_idx,
                    "value": val,
                    "desc": f"{seed_name}的种子，可在灵田种植"
                })
                mid += 1

            # 药材
            for i, herb_name in enumerate(SEED_TYPES[:3 + realm_idx]):
                materials.append({
                    "id": mid,
                    "name": f"{realm_name}·{quality_name}·{herb_name}",
                    "type": "药材",
                    "quality": q,
                    "realm": realm_idx,
                    "value": val,
                    "desc": f"炼丹所需药材"
                })
                mid += 1

            # 器材
            for i, equip_name in enumerate(EQUIP_MATERIAL_TYPES[:3 + realm_idx]):
                materials.append({
                    "id": mid,
                    "name": f"{realm_name}·{quality_name}·{equip_name}",
                    "type": "器材",
                    "quality": q,
                    "realm": realm_idx,
                    "value": val,
                    "desc": f"炼器所需器材"
                })
                mid += 1

            # 强化材料
            for i, enh_name in enumerate(ENHANCE_MATERIAL_TYPES[:2 + realm_idx]):
                materials.append({
                    "id": mid,
                    "name": f"{realm_name}·{quality_name}·{enh_name}",
                    "type": "强化材料",
                    "quality": q,
                    "realm": realm_idx,
                    "value": val,
                    "desc": f"强化装备所需材料"
                })
                mid += 1

    return materials


MATERIAL_POOL = generate_all_materials()