"""
丹药数据模块
分四个类型：气血丹、暴力丹、龟甲丹、聚气丹
每个境界白绿蓝紫金五阶，金色数值约为白色2倍
金色丹药只能靠炼制获取，无法在宗门或藏宝阁获取
"""

REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "渡劫", "大乘", "真仙"]
QUALITIES = ["白", "绿", "蓝", "紫", "金"]
QUALITY_MULT = {"白": 1.0, "绿": 1.25, "蓝": 1.5, "紫": 1.75, "金": 2.0}

# 境界基础数值（气血丹加HP、暴力丹加攻击、龟甲丹加防御、聚气丹加修为）
# 格式: (气血, 攻击, 防御, 修为)
BASE_VALUES = {
    0: (100, 5, 3, 50),       # 练气
    1: (300, 15, 8, 200),     # 筑基
    2: (800, 40, 20, 800),    # 金丹
    3: (2000, 100, 50, 3000), # 元婴
    4: (5000, 250, 120, 10000), # 化神
    5: (12000, 600, 300, 35000), # 渡劫
    6: (30000, 1500, 700, 120000), # 大乘
    7: (80000, 4000, 1800, 500000), # 真仙
}

def generate_all_pills():
    """生成全部丹药数据"""
    pills = []
    pid = 1
    
    pill_types = [
        {"name": "气血丹", "attr": "hp", "desc": "永久增加生命上限"},
        {"name": "暴力丹", "attr": "attack", "desc": "永久增加攻击力"},
        {"name": "龟甲丹", "attr": "defense", "desc": "永久增加防御力"},
        {"name": "聚气丹", "attr": "cultivation", "desc": "立即获得修为"},
    ]
    
    for realm_idx in range(8):
        realm_name = REALM_NAMES[realm_idx]
        base_hp, base_atk, base_def, base_cult = BASE_VALUES[realm_idx]
        
        for q in QUALITIES:
            quality_mult = QUALITY_MULT[q]
            quality_name = q
            
            for pt in pill_types:
                name = f"{realm_name}·{quality_name}·{pt['name']}"
                
                if pt["attr"] == "hp":
                    value = int(base_hp * quality_mult)
                elif pt["attr"] == "attack":
                    value = int(base_atk * quality_mult)
                elif pt["attr"] == "defense":
                    value = int(base_def * quality_mult)
                else:  # cultivation
                    value = int(base_cult * quality_mult)
                
                pill = {
                    "id": pid,
                    "name": name,
                    "type": "丹药",
                    "pill_attr": pt["attr"],
                    "quality": q,
                    "realm": realm_idx,
                    "realm_name": realm_name,
                    "value": value,
                    "desc": f"{pt['desc']}：{value}",
                    "obtainable_from_shop": q != "金",  # 金色只能炼制
                    "max_stack": 99 if pt["attr"] != "cultivation" else 0,  # 聚气丹无上限
                }
                pills.append(pill)
                pid += 1
    
    return pills

PILL_POOL = generate_all_pills()