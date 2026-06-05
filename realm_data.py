"""
仙道永恒 - 境界数据模块
修为规则：练气每阶+100，筑基每阶+1000，金丹每阶+10000，以此类推（×10）
"""

# 9大境界
REALM_NAMES = ["练气", "筑基", "金丹", "元婴", "化神", "合体", "渡劫", "大乘", "真仙"]
STAGES_PER_REALM = 10


def get_stage_cultivation_cost(realm_index, stage):
    """获取第 stage 阶所需的修为（单阶）
    规则：练气一阶每次突破+100所需修为，筑基突破一小阶+1000所需修为，以此类推
    即：第n阶所需修为 = 基础值 * n
    基础值：练气=100，筑基=1000，金丹=10000...
    """
    base = 100 * (10 ** realm_index)
    return base * stage


def get_realm_total_cultivation(realm_index):
    """获取完成整个境界所需的总修为"""
    base = 100 * (10 ** realm_index)
    return base * 55  # 1+2+...+10 = 55


def get_realm_name(realm_index):
    """获取境界名称"""
    if 0 <= realm_index < len(REALM_NAMES):
        return REALM_NAMES[realm_index]
    return "未知"


def get_stage_info(realm_index, cultivation, current_stage=None):
    """根据境界内累计修为，计算当前阶数、阶内进度、阶所需修为
    返回: (stage, progress_in_stage, stage_total, realm_total)
    """
    base = 100 * (10 ** realm_index)
    
    # 如果提供了当前阶数，使用它
    if current_stage is not None:
        stage = current_stage
        if stage > STAGES_PER_REALM:
            stage = STAGES_PER_REALM
        
        # 计算该阶所需总修为
        cumulative_before = 0
        for s in range(1, stage):
            cumulative_before += base * s
        
        stage_cost = base * stage
        progress = cultivation - cumulative_before
        
        # 如果进度超过当前阶所需，则进度为满
        if progress > stage_cost:
            progress = stage_cost
        
        return stage, progress, stage_cost, base * 55
    
    # 否则使用旧逻辑
    cumulative = 0
    for s in range(1, STAGES_PER_REALM + 1):
        stage_cost = base * s
        if cultivation <= cumulative + stage_cost:
            return s, cultivation - cumulative, stage_cost, base * 55
        cumulative += stage_cost
    # 满阶
    return STAGES_PER_REALM, cultivation - cumulative, base * STAGES_PER_REALM, base * 55


# 玩家状态（初始角色，灵根觉醒后从零开始）
player = {
    "name": "李云修",
    "realm_index": 0,       # 练气
    "cultivation": 0,       # 当前境界内累计修为
    "current_stage": 1,     # 当前阶数（1-10）
    "attack": 10,
    "hp": 100,
    "max_hp": 100,
    "mp": 50,
    "max_mp": 50,
    "defense": 5,
    "free_points": 0,
    "spirit_stones": 0,
}

# 修炼系统状态
cultivation_state = {
    "is_cultivating": False,      # 是否正在修炼
    "cultivation_start_time": 0,  # 修炼开始时间（秒）
    "cultivation_duration": 180,  # 修炼时长（秒），3分钟
    "cultivation_interval": 5,    # 修为获取间隔（秒）
    "last_gain_time": 0,          # 上次获取修为的时间
    "cultivation_per_interval": 10,  # 每次间隔获得的修为
    "auto_cultivation": False,    # 是否开启自动修炼（筑基期后）
}
