"""
仙道永恒 - 宗门数据模块
宗门品阶1-8星，对应境界筑基-真仙
包含：职位系统、任务系统、贡献堂兑换、参悟堂
"""

import time
import random
from realm_data import REALM_NAMES

# ==================== 宗门定义 ====================
SECT_DATA = {
    1: {
        "琅琊派": {
            "star": 1, "realm_required": 1,
            "desc": "上古剑修传承，以一道神秘剑诀名震天下",
            "feature": "宗门绝学·琅琊剑诀",
            "feature_desc": "拥有一门特殊功法「琅琊剑诀」，威力远超同阶功法（伤害×2.5）",
            "feature_type": "special_technique", "technique_id": "sect_langya_sword",
            "color": (180, 140, 240),
            "gongfa": {
                "灵技": {"name": "琅琊剑技", "element": "金", "effect_type": "damage", "effect_value": 55, "desc": "琅琊派基础剑技 · 伤害 55"},
                "心法": {"name": "琅琊心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.12, "desc": "修为获取率 +12%"},
                "内经": [
                    {"name": "金锋锻体", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 25, "desc": "攻击 +25"},
                    {"name": "剑罡护体", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 15, "desc": "防御 +15"},
                    {"name": "锐气冲脉", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 80, "desc": "生命 +80"},
                ],
            },
        },
        "唐门": {
            "star": 1, "realm_required": 1,
            "desc": "暗器与机关之术冠绝天下，铸器之道独步修真界",
            "feature": "铸器世家",
            "feature_desc": "换取装备所需贡献点 -50%",
            "feature_type": "equip_discount", "feature_value": 0.5,
            "color": (60, 180, 220),
            "gongfa": {
                "灵技": {"name": "暴雨梨花", "element": "金", "effect_type": "damage", "effect_value": 50, "desc": "唐门暗器绝学 · 伤害 50"},
                "心法": {"name": "暗器心法", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.10, "desc": "修为获取率 +10%"},
                "内经": [
                    {"name": "千机百变", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 20, "desc": "攻击 +20"},
                    {"name": "机关护甲", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 20, "desc": "防御 +20"},
                    {"name": "毒抗体质", "element": "木", "effect_type": "attribute", "attr": "hp", "effect_value": 90, "desc": "生命 +90"},
                ],
            },
        },
        "灵草派": {
            "star": 1, "realm_required": 1,
            "desc": "精于灵草培育之道，掌握草木生长之秘",
            "feature": "草木通灵",
            "feature_desc": "掌握减少灵草成长所需时间的秘籍（灵草成长时间 -30%）",
            "feature_type": "herb_growth", "feature_value": 0.3,
            "color": (80, 200, 130),
            "gongfa": {
                "灵技": {"name": "荆棘缠绕", "element": "木", "effect_type": "damage", "effect_value": 45, "desc": "灵草派木行法术 · 伤害 45"},
                "心法": {"name": "灵草心经", "element": "木", "effect_type": "cultivation_rate", "effect_value": 1.10, "desc": "修为获取率 +10%"},
                "内经": [
                    {"name": "草木灵体", "element": "木", "effect_type": "attribute", "attr": "hp", "effect_value": 100, "desc": "生命 +100"},
                    {"name": "生生不息", "element": "木", "effect_type": "attribute", "attr": "defense", "effect_value": 15, "desc": "防御 +15"},
                    {"name": "青木回春", "element": "木", "effect_type": "attribute", "attr": "attack", "effect_value": 20, "desc": "攻击 +20"},
                ],
            },
        },
    },
    2: {
        "灵越山": {
            "star": 2, "realm_required": 2,
            "desc": "琅琊派上宗，剑道传承更加完整，底蕴深不可测",
            "feature": "宗门绝学·灵越天剑",
            "feature_desc": "灵越天剑进阶版，威力远超同阶功法（伤害×3.0）",
            "feature_type": "special_technique", "technique_id": "sect_lingyue_sword",
            "color": (200, 120, 255),
            "gongfa": {
                "灵技": {"name": "灵越剑罡", "element": "金", "effect_type": "damage", "effect_value": 80, "desc": "灵越山核心剑技 · 伤害 80"},
                "心法": {"name": "灵越心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.15, "desc": "修为获取率 +15%"},
                "内经": [
                    {"name": "剑心通明", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 40, "desc": "攻击 +40"},
                    {"name": "灵越罡气", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 25, "desc": "防御 +25"},
                    {"name": "剑骨淬炼", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 120, "desc": "生命 +120"},
                ],
            },
        },
        "锤铁山": {
            "star": 2, "realm_required": 2,
            "desc": "唐门上宗，锻造之术已达化境，以锤为道",
            "feature": "神匠传承",
            "feature_desc": "换取装备所需贡献点 -60%",
            "feature_type": "equip_discount", "feature_value": 0.4,
            "color": (40, 160, 240),
            "gongfa": {
                "灵技": {"name": "千钧锤", "element": "金", "effect_type": "damage", "effect_value": 75, "desc": "锤铁山锻造神技 · 伤害 75"},
                "心法": {"name": "锻天心法", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.13, "desc": "修为获取率 +13%"},
                "内经": [
                    {"name": "铁骨铜皮", "element": "土", "effect_type": "attribute", "attr": "defense", "effect_value": 30, "desc": "防御 +30"},
                    {"name": "千锤百炼", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 30, "desc": "攻击 +30"},
                    {"name": "山岳之躯", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 130, "desc": "生命 +130"},
                ],
            },
        },
        "药师谷": {
            "star": 2, "realm_required": 2,
            "desc": "医道圣地，掌握失传已久的疗伤内经",
            "feature": "医道内经",
            "feature_desc": "掌握「回春内经」，战斗中每回合恢复体力",
            "feature_type": "heal_scripture", "technique_id": "sect_heal_scripture",
            "color": (60, 220, 160),
            "gongfa": {
                "灵技": {"name": "药王毒典", "element": "木", "effect_type": "damage", "effect_value": 70, "desc": "药师谷独门毒术 · 伤害 70"},
                "心法": {"name": "济世心经", "element": "木", "effect_type": "cultivation_rate", "effect_value": 1.14, "desc": "修为获取率 +14%"},
                "内经": [
                    {"name": "春华内经", "element": "木", "effect_type": "attribute", "attr": "hp", "effect_value": 150, "desc": "生命 +150"},
                    {"name": "药王百草", "element": "木", "effect_type": "attribute", "attr": "defense", "effect_value": 20, "desc": "防御 +20"},
                    {"name": "毒经要义", "element": "木", "effect_type": "attribute", "attr": "attack", "effect_value": 25, "desc": "攻击 +25"},
                ],
            },
        },
        "凤凰阁": {
            "star": 2, "realm_required": 2,
            "desc": "以凤凰血脉传承闻名，弟子皆天赋异禀",
            "feature": "凤凰血脉",
            "feature_desc": "宗门贡献值获取率 +10%",
            "feature_type": "contrib_bonus", "feature_value": 0.1,
            "color": (255, 140, 70),
            "gongfa": {
                "灵技": {"name": "凤炎击", "element": "火", "effect_type": "damage", "effect_value": 72, "desc": "凤凰阁火行秘技 · 伤害 72"},
                "心法": {"name": "涅槃心经", "element": "火", "effect_type": "cultivation_rate", "effect_value": 1.13, "desc": "修为获取率 +13%"},
                "内经": [
                    {"name": "凤凰血脉", "element": "火", "effect_type": "attribute", "attr": "attack", "effect_value": 35, "desc": "攻击 +35"},
                    {"name": "涅槃火种", "element": "火", "effect_type": "attribute", "attr": "hp", "effect_value": 110, "desc": "生命 +110"},
                    {"name": "凤羽护体", "element": "火", "effect_type": "attribute", "attr": "defense", "effect_value": 22, "desc": "防御 +22"},
                ],
            },
        },
    },
    3: {
        "天剑宗": {
            "star": 3, "realm_required": 3,
            "desc": "天下剑修向往的圣地，剑道传承万载，为灵越山上宗",
            "feature": "天剑真意", "feature_desc": "剑道功法威力 +40%",
            "feature_type": "sword_bonus", "feature_value": 0.4,
            "color": (220, 180, 255),
            "gongfa": {
                "灵技": {"name": "天剑诀", "element": "金", "effect_type": "damage", "effect_value": 110, "desc": "天剑宗镇派剑技 · 伤害 110"},
                "心法": {"name": "天剑心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.18, "desc": "修为获取率 +18%"},
                "内经": [
                    {"name": "天剑锻体", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 60, "desc": "攻击 +60"},
                    {"name": "天罡剑气", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 35, "desc": "防御 +35"},
                    {"name": "剑元归宗", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 180, "desc": "生命 +180"},
                ],
            },
        },
        "万宝楼": {
            "star": 3, "realm_required": 3,
            "desc": "聚天下奇珍异宝，以商入道，为锤铁山上宗",
            "feature": "万宝之缘", "feature_desc": "每周可领取灵石 ×200",
            "feature_type": "weekly_stones", "feature_value": 200,
            "color": (255, 200, 60),
            "gongfa": {
                "灵技": {"name": "金元宝术", "element": "土", "effect_type": "damage", "effect_value": 95, "desc": "万宝楼金钱秘术 · 伤害 95"},
                "心法": {"name": "聚宝心经", "element": "土", "effect_type": "cultivation_rate", "effect_value": 1.16, "desc": "修为获取率 +16%"},
                "内经": [
                    {"name": "富贵金身", "element": "土", "effect_type": "attribute", "attr": "defense", "effect_value": 40, "desc": "防御 +40"},
                    {"name": "万宝奇珍", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 45, "desc": "攻击 +45"},
                    {"name": "聚灵宝体", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 160, "desc": "生命 +160"},
                ],
            },
        },
        "神农谷": {
            "star": 3, "realm_required": 3,
            "desc": "上古神农氏遗脉，炼丹之术冠绝修真界，为药师谷上宗",
            "feature": "神农丹道", "feature_desc": "炼丹成功率 +25%",
            "feature_type": "alchemy_bonus", "feature_value": 0.25,
            "color": (100, 230, 140),
            "gongfa": {
                "灵技": {"name": "百草噬魂", "element": "木", "effect_type": "damage", "effect_value": 100, "desc": "神农谷毒术大成 · 伤害 100"},
                "心法": {"name": "神农本草经", "element": "木", "effect_type": "cultivation_rate", "effect_value": 1.17, "desc": "修为获取率 +17%"},
                "内经": [
                    {"name": "丹道真解", "element": "木", "effect_type": "attribute", "attr": "hp", "effect_value": 200, "desc": "生命 +200"},
                    {"name": "药王百炼", "element": "木", "effect_type": "attribute", "attr": "defense", "effect_value": 30, "desc": "防御 +30"},
                    {"name": "神农百草经", "element": "木", "effect_type": "attribute", "attr": "attack", "effect_value": 35, "desc": "攻击 +35"},
                ],
            },
        },
    },
    4: {
        "九天宫": {
            "star": 4, "realm_required": 4,
            "desc": "九天之上，仙宫临世，掌控天地法则",
            "feature": "九天玄法", "feature_desc": "修炼速度 +25%",
            "feature_type": "cultivation_boost", "feature_value": 0.25,
            "color": (180, 200, 255),
            "gongfa": {
                "灵技": {"name": "九天玄雷", "element": "水", "effect_type": "damage", "effect_value": 140, "desc": "九天宫雷法 · 伤害 140"},
                "心法": {"name": "九天玄心诀", "element": "水", "effect_type": "cultivation_rate", "effect_value": 1.22, "desc": "修为获取率 +22%"},
                "内经": [
                    {"name": "九天玄体", "element": "水", "effect_type": "attribute", "attr": "hp", "effect_value": 250, "desc": "生命 +250"},
                    {"name": "玄天罡气", "element": "水", "effect_type": "attribute", "attr": "defense", "effect_value": 45, "desc": "防御 +45"},
                    {"name": "九霄雷法", "element": "水", "effect_type": "attribute", "attr": "attack", "effect_value": 70, "desc": "攻击 +70"},
                ],
            },
        },
        "鬼王宗": {
            "star": 4, "realm_required": 4,
            "desc": "幽冥鬼道，以战养战，越战越强",
            "feature": "鬼王战意", "feature_desc": "击败敌人后恢复 10% 生命值",
            "feature_type": "kill_heal", "feature_value": 0.1,
            "color": (150, 80, 200),
            "gongfa": {
                "灵技": {"name": "鬼王噬魂", "element": "水", "effect_type": "damage", "effect_value": 135, "desc": "鬼王宗禁术 · 伤害 135"},
                "心法": {"name": "幽冥心经", "element": "水", "effect_type": "cultivation_rate", "effect_value": 1.20, "desc": "修为获取率 +20%"},
                "内经": [
                    {"name": "鬼王真身", "element": "水", "effect_type": "attribute", "attr": "attack", "effect_value": 80, "desc": "攻击 +80"},
                    {"name": "不灭鬼躯", "element": "水", "effect_type": "attribute", "attr": "hp", "effect_value": 220, "desc": "生命 +220"},
                    {"name": "幽冥护体", "element": "水", "effect_type": "attribute", "attr": "defense", "effect_value": 35, "desc": "防御 +35"},
                ],
            },
        },
        "凤炎阁": {
            "star": 4, "realm_required": 4,
            "desc": "凤凰阁上宗，凤凰血脉觉醒，焚尽八荒之力",
            "feature": "凤炎真火", "feature_desc": "灵技伤害 +30%",
            "feature_type": "skill_damage_boost", "feature_value": 0.3,
            "color": (255, 100, 50),
            "gongfa": {
                "灵技": {"name": "凤炎焚天", "element": "火", "effect_type": "damage", "effect_value": 145, "desc": "凤炎阁终极火术 · 伤害 145"},
                "心法": {"name": "凤炎心经", "element": "火", "effect_type": "cultivation_rate", "effect_value": 1.21, "desc": "修为获取率 +21%"},
                "内经": [
                    {"name": "凤炎真体", "element": "火", "effect_type": "attribute", "attr": "attack", "effect_value": 85, "desc": "攻击 +85"},
                    {"name": "涅槃重生", "element": "火", "effect_type": "attribute", "attr": "hp", "effect_value": 240, "desc": "生命 +240"},
                    {"name": "凤羽战甲", "element": "火", "effect_type": "attribute", "attr": "defense", "effect_value": 40, "desc": "防御 +40"},
                ],
            },
        },
    },
    5: {
        "天道盟": {
            "star": 5, "realm_required": 5,
            "desc": "代天行道，维护修真界秩序的超然势力",
            "feature": "天道庇护", "feature_desc": "所有属性 +15%",
            "feature_type": "all_stat_boost", "feature_value": 0.15,
            "color": (255, 220, 100),
            "gongfa": {
                "灵技": {"name": "天罚", "element": "土", "effect_type": "damage", "effect_value": 175, "desc": "天道盟天罚之术 · 伤害 175"},
                "心法": {"name": "天道心经", "element": "土", "effect_type": "cultivation_rate", "effect_value": 1.25, "desc": "修为获取率 +25%"},
                "内经": [
                    {"name": "天道金身", "element": "土", "effect_type": "attribute", "attr": "defense", "effect_value": 60, "desc": "防御 +60"},
                    {"name": "代天行道", "element": "土", "effect_type": "attribute", "attr": "attack", "effect_value": 95, "desc": "攻击 +95"},
                    {"name": "天地正气", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 300, "desc": "生命 +300"},
                ],
            },
        },
        "万剑冢": {
            "star": 5, "realm_required": 5,
            "desc": "天剑宗上宗，万剑归宗之地，历代剑仙埋骨之所",
            "feature": "万剑归宗", "feature_desc": "剑道功法威力 +60%",
            "feature_type": "sword_bonus", "feature_value": 0.6,
            "color": (240, 160, 255),
            "gongfa": {
                "灵技": {"name": "万剑归宗", "element": "金", "effect_type": "damage", "effect_value": 180, "desc": "万剑冢镇派绝学 · 伤害 180"},
                "心法": {"name": "剑冢心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.24, "desc": "修为获取率 +24%"},
                "内经": [
                    {"name": "万剑入体", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 100, "desc": "攻击 +100"},
                    {"name": "剑魂淬炼", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 50, "desc": "防御 +50"},
                    {"name": "剑冢不朽", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 280, "desc": "生命 +280"},
                ],
            },
        },
        "天工殿": {
            "star": 5, "realm_required": 5,
            "desc": "万宝楼上宗，掌握造化天工之秘，炼器之道无人能及",
            "feature": "天工造化", "feature_desc": "炼器成功率 +30%",
            "feature_type": "crafting_bonus", "feature_value": 0.3,
            "color": (255, 180, 40),
            "gongfa": {
                "灵技": {"name": "造化天工", "element": "金", "effect_type": "damage", "effect_value": 170, "desc": "天工殿造化神术 · 伤害 170"},
                "心法": {"name": "天工心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.23, "desc": "修为获取率 +23%"},
                "内经": [
                    {"name": "造化金身", "element": "土", "effect_type": "attribute", "attr": "defense", "effect_value": 65, "desc": "防御 +65"},
                    {"name": "天工神锤", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 90, "desc": "攻击 +90"},
                    {"name": "大地之躯", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 320, "desc": "生命 +320"},
                ],
            },
        },
    },
    6: {
        "大罗殿": {
            "star": 6, "realm_required": 6,
            "desc": "渡劫飞升前的最后试炼之地，非大毅力者不得入",
            "feature": "大罗金身", "feature_desc": "渡劫成功率 +20%，受到伤害 -20%",
            "feature_type": "tribulation_boost", "feature_value": 0.2,
            "color": (255, 200, 50),
            "gongfa": {
                "灵技": {"name": "大罗天雷", "element": "金", "effect_type": "damage", "effect_value": 220, "desc": "大罗殿雷劫之术 · 伤害 220"},
                "心法": {"name": "大罗心经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.28, "desc": "修为获取率 +28%"},
                "内经": [
                    {"name": "大罗金身", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 80, "desc": "防御 +80"},
                    {"name": "渡劫真意", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 400, "desc": "生命 +400"},
                    {"name": "天雷淬体", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 120, "desc": "攻击 +120"},
                ],
            },
        },
        "太虚宫": {
            "star": 6, "realm_required": 6,
            "desc": "九天宫上宗，太虚幻境中参悟天道，修行一日抵百日",
            "feature": "太虚幻境", "feature_desc": "修炼速度 +40%",
            "feature_type": "cultivation_boost", "feature_value": 0.4,
            "color": (140, 200, 255),
            "gongfa": {
                "灵技": {"name": "太虚破灭", "element": "水", "effect_type": "damage", "effect_value": 210, "desc": "太虚宫破灭之法 · 伤害 210"},
                "心法": {"name": "太虚心经", "element": "水", "effect_type": "cultivation_rate", "effect_value": 1.30, "desc": "修为获取率 +30%"},
                "内经": [
                    {"name": "太虚灵体", "element": "水", "effect_type": "attribute", "attr": "hp", "effect_value": 380, "desc": "生命 +380"},
                    {"name": "虚幻护甲", "element": "水", "effect_type": "attribute", "attr": "defense", "effect_value": 70, "desc": "防御 +70"},
                    {"name": "太虚道法", "element": "水", "effect_type": "attribute", "attr": "attack", "effect_value": 110, "desc": "攻击 +110"},
                ],
            },
        },
    },
    7: {
        "仙盟": {
            "star": 7, "realm_required": 7,
            "desc": "大乘修士组成的至高联盟，共享飞升之秘",
            "feature": "仙盟共享", "feature_desc": "可同时拥有两个宗门特性",
            "feature_type": "dual_feature",
            "color": (200, 220, 255),
            "gongfa": {
                "灵技": {"name": "仙盟令", "element": "金", "effect_type": "damage", "effect_value": 260, "desc": "仙盟盟主令法 · 伤害 260"},
                "心法": {"name": "仙盟心经", "element": "土", "effect_type": "cultivation_rate", "effect_value": 1.33, "desc": "修为获取率 +33%"},
                "内经": [
                    {"name": "仙盟金令", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 140, "desc": "攻击 +140"},
                    {"name": "万仙供养", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 480, "desc": "生命 +480"},
                    {"name": "仙盟法则", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 90, "desc": "防御 +90"},
                ],
            },
        },
        "长生殿": {
            "star": 7, "realm_required": 7,
            "desc": "追求永生不朽的古老势力，掌握长生不灭之秘",
            "feature": "长生不灭", "feature_desc": "生命值上限 +30%",
            "feature_type": "hp_boost", "feature_value": 0.3,
            "color": (80, 240, 180),
            "gongfa": {
                "灵技": {"name": "长生劫", "element": "木", "effect_type": "damage", "effect_value": 250, "desc": "长生殿岁月法术 · 伤害 250"},
                "心法": {"name": "长生真经", "element": "木", "effect_type": "cultivation_rate", "effect_value": 1.32, "desc": "修为获取率 +32%"},
                "内经": [
                    {"name": "不死真身", "element": "木", "effect_type": "attribute", "attr": "hp", "effect_value": 500, "desc": "生命 +500"},
                    {"name": "岁月不朽", "element": "木", "effect_type": "attribute", "attr": "defense", "effect_value": 85, "desc": "防御 +85"},
                    {"name": "长生之力", "element": "木", "effect_type": "attribute", "attr": "attack", "effect_value": 130, "desc": "攻击 +130"},
                ],
            },
        },
    },
    8: {
        "天庭": {
            "star": 8, "realm_required": 8,
            "desc": "三界至高无上的统治机构，统御万仙",
            "feature": "天帝诏令", "feature_desc": "所有功法效果 ×2，修炼速度 ×2",
            "feature_type": "divine_boost", "feature_value": 1.0,
            "color": (255, 220, 50),
            "gongfa": {
                "灵技": {"name": "天帝剑", "element": "金", "effect_type": "damage", "effect_value": 350, "desc": "天庭帝道之剑 · 伤害 350"},
                "心法": {"name": "天帝真经", "element": "金", "effect_type": "cultivation_rate", "effect_value": 1.40, "desc": "修为获取率 +40%"},
                "内经": [
                    {"name": "天帝金身", "element": "金", "effect_type": "attribute", "attr": "attack", "effect_value": 200, "desc": "攻击 +200"},
                    {"name": "天庭法则", "element": "金", "effect_type": "attribute", "attr": "defense", "effect_value": 120, "desc": "防御 +120"},
                    {"name": "万仙来朝", "element": "金", "effect_type": "attribute", "attr": "hp", "effect_value": 600, "desc": "生命 +600"},
                ],
            },
        },
        "太初殿": {
            "star": 8, "realm_required": 8,
            "desc": "混沌初开时便已存在的太古势力，掌握太初本源",
            "feature": "太初本源", "feature_desc": "所有属性 +30%，突破无需丹药",
            "feature_type": "primordial_boost", "feature_value": 0.3,
            "color": (200, 200, 255),
            "gongfa": {
                "灵技": {"name": "太初之光", "element": "土", "effect_type": "damage", "effect_value": 380, "desc": "太初殿本源之力 · 伤害 380"},
                "心法": {"name": "太初经", "element": "土", "effect_type": "cultivation_rate", "effect_value": 1.42, "desc": "修为获取率 +42%"},
                "内经": [
                    {"name": "太初玄体", "element": "土", "effect_type": "attribute", "attr": "hp", "effect_value": 650, "desc": "生命 +650"},
                    {"name": "混沌之力", "element": "土", "effect_type": "attribute", "attr": "attack", "effect_value": 180, "desc": "攻击 +180"},
                    {"name": "太古壁垒", "element": "土", "effect_type": "attribute", "attr": "defense", "effect_value": 130, "desc": "防御 +130"},
                ],
            },
        },
    },
}

# ==================== 职位系统 ====================
SECT_RANKS = [
    {"id": 0, "name": "外门弟子", "contrib_required": 0,    "max_task_lv": 1, "meditate_bonus": 1.50},
    {"id": 1, "name": "内门弟子", "contrib_required": 100,  "max_task_lv": 2, "meditate_bonus": 2.00},
    {"id": 2, "name": "核心弟子", "contrib_required": 500,  "max_task_lv": 3, "meditate_bonus": 3.00},
    {"id": 3, "name": "真传弟子", "contrib_required": 2000, "max_task_lv": 4, "meditate_bonus": 4.00},
    {"id": 4, "name": "长老",     "contrib_required": 5000, "max_task_lv": 5, "meditate_bonus": 5.00},
]

# ==================== 任务系统 ====================
# 任务等级定义：(贡献/分钟, 自动完成需时_分钟, 名称前缀)
TASK_LEVELS = [
    {"lv": 1, "contrib_per_min": 1,   "time_minutes": 30, "name": "巡逻值守"},
    {"lv": 2, "contrib_per_min": 2,   "time_minutes": 25, "name": "采集灵材"},
    {"lv": 3, "contrib_per_min": 4,   "time_minutes": 20, "name": "猎杀妖兽"},
    {"lv": 4, "contrib_per_min": 8,   "time_minutes": 15, "name": "护送商队"},
    {"lv": 5, "contrib_per_min": 15,  "time_minutes": 10, "name": "镇守秘境"},
]

# ==================== 贡献堂兑换 ====================
CONTRIB_SHOP = {
    "功法": [
        {"name": "基础心法·绿", "cost": 30,  "desc": "随机绿色品质心法", "type": "gongfa", "quality": "绿"},
        {"name": "基础心法·蓝", "cost": 80,  "desc": "随机蓝色品质心法", "type": "gongfa", "quality": "蓝"},
        {"name": "基础心法·紫", "cost": 200, "desc": "随机紫色品质心法", "type": "gongfa", "quality": "紫"},
        {"name": "灵技残卷·绿", "cost": 40,  "desc": "随机绿色品质灵技", "type": "gongfa", "quality": "绿"},
        {"name": "灵技残卷·蓝", "cost": 100, "desc": "随机蓝色品质灵技", "type": "gongfa", "quality": "蓝"},
        {"name": "灵技残卷·紫", "cost": 250, "desc": "随机紫色品质灵技", "type": "gongfa", "quality": "紫"},
    ],
    "装备": [
        {"name": "凡品装备箱",  "cost": 50,  "desc": "随机绿色-蓝色装备",  "type": "equip",   "quality": "随机"},
        {"name": "良品装备箱",  "cost": 150, "desc": "随机蓝色-紫色装备",  "type": "equip",   "quality": "随机"},
        {"name": "精品装备箱",  "cost": 400, "desc": "随机紫色-金色装备",  "type": "equip",   "quality": "随机"},
    ],
    "材料": [
        {"name": "精铁包",      "cost": 20,  "desc": "精铁 ×10",           "type": "material","quality": "普通"},
        {"name": "灵石袋",      "cost": 30,  "desc": "灵石 ×100",          "type": "material","quality": "普通"},
        {"name": "灵草种子袋",  "cost": 25,  "desc": "随机灵草种子 ×5",    "type": "material","quality": "普通"},
        {"name": "炼器材料包",  "cost": 60,  "desc": "随机炼器材料 ×3",    "type": "material","quality": "普通"},
    ],
    "丹药": [
        {"name": "凝血丹",      "cost": 15,  "desc": "恢复生命 50 点",     "type": "pill",    "quality": "普通"},
        {"name": "聚灵丹",      "cost": 25,  "desc": "立即获得 500 修为",  "type": "pill",    "quality": "普通"},
        {"name": "培元丹",      "cost": 50,  "desc": "修炼速度 +30%，持续30分钟","type": "pill", "quality": "普通"},
        {"name": "破境丹",      "cost": 200, "desc": "突破成功率 +20%",    "type": "pill",    "quality": "稀有"},
    ],
}

# ==================== 宗门特殊功法 ====================
SECT_SPECIAL_TECHNIQUES = {
    "sect_langya_sword": {
        "id": 99901, "name": "琅琊剑诀", "element": "金", "type": "灵技",
        "quality": "金", "realm_min": 1, "effect_type": "damage",
        "effect_value": 75, "desc": "宗门绝学 · 伤害 75", "multiplier": 2.5, "sect_only": True,
    },
    "sect_lingyue_sword": {
        "id": 99902, "name": "灵越天剑", "element": "金", "type": "灵技",
        "quality": "金", "realm_min": 2, "effect_type": "damage",
        "effect_value": 120, "desc": "宗门绝学 · 伤害 120", "multiplier": 3.0, "sect_only": True,
    },
    "sect_heal_scripture": {
        "id": 99903, "name": "回春内经", "element": "木", "type": "内经",
        "quality": "金", "realm_min": 2, "effect_type": "heal_per_turn",
        "effect_value": 20, "desc": "战斗中每回合恢复 20 点生命", "sect_only": True,
    },
}

# ==================== 玩家宗门状态 ====================
player_sect = {
    "joined": False,
    "sect_name": None,
    "sect_star": 0,
    "contribution": 0,
    "rank": 0,                          # 职位索引（0=外门弟子）
    "techniques_learned": [],

    # 任务系统
    "task_lv": 1,                       # 当前执行的任务等级
    "task_start_time": 0,               # 当前任务开始时间
    "task_contrib_accumulated": 0,       # 本轮已累计待结算贡献

    # 参悟堂
    "meditate_active": False,
    "meditate_start_time": 0,
    "meditate_duration": 3600,          # 1小时
    "meditate_bonus": 0,                # 当前倍率（乘数，如1.5表示150%）
}

# ==================== 宗门工具函数 ====================

def get_available_sects(player_realm_index):
    available = {}
    for star, sects in SECT_DATA.items():
        if player_realm_index >= star:
            available[star] = sects
    return available


def get_sect_info(sect_name):
    for star, sects in SECT_DATA.items():
        if sect_name in sects:
            return sects[sect_name]
    return None


def join_sect(sect_name):
    sector = get_sect_info(sect_name)
    if not sector:
        return False
    player_sect["joined"] = True
    player_sect["sect_name"] = sect_name
    player_sect["sect_star"] = sector["star"]
    player_sect["contribution"] = 0
    player_sect["rank"] = 0
    player_sect["techniques_learned"] = []
    player_sect["task_lv"] = 1
    player_sect["task_start_time"] = time.time()
    player_sect["task_contrib_accumulated"] = 0
    player_sect["meditate_active"] = False

    # 自动获得宗门特殊功法（灵技+心法+内经）
    if "gongfa" in sector:
        gf = sector["gongfa"]
        # 灵技
        lingji = gf.get("灵技")
        if lingji:
            tid = f"sect_{sect_name}_lingji"
            SECT_SPECIAL_TECHNIQUES[tid] = {
                "id": tid, "name": lingji["name"], "element": lingji["element"],
                "type": "灵技", "quality": "金", "realm_min": sector["star"],
                "effect_type": lingji["effect_type"], "effect_value": lingji["effect_value"],
                "desc": lingji["desc"], "sect_only": True, "sect_star": sector["star"],
            }
            if tid not in player_sect["techniques_learned"]:
                player_sect["techniques_learned"].append(tid)
        # 心法
        xinfa = gf.get("心法")
        if xinfa:
            tid = f"sect_{sect_name}_xinfa"
            SECT_SPECIAL_TECHNIQUES[tid] = {
                "id": tid, "name": xinfa["name"], "element": xinfa["element"],
                "type": "心法", "quality": "金", "realm_min": sector["star"],
                "effect_type": xinfa["effect_type"], "effect_value": xinfa["effect_value"],
                "desc": xinfa["desc"], "sect_only": True, "sect_star": sector["star"],
            }
            if tid not in player_sect["techniques_learned"]:
                player_sect["techniques_learned"].append(tid)
        # 3本内经
        for neijing in gf.get("内经", []):
            tid = f"sect_{sect_name}_nj_{neijing['name']}"
            SECT_SPECIAL_TECHNIQUES[tid] = {
                "id": tid, "name": neijing["name"], "element": neijing["element"],
                "type": "内经", "quality": "金", "realm_min": sector["star"],
                "effect_type": neijing["effect_type"], "attr": neijing["attr"],
                "effect_value": neijing["effect_value"],
                "desc": neijing["desc"], "sect_only": True, "sect_star": sector["star"],
            }
            if tid not in player_sect["techniques_learned"]:
                player_sect["techniques_learned"].append(tid)

    # 保留旧兼容：特定 feature_type 的特殊功法
    if sector.get("feature_type") == "special_technique":
        tid = sector.get("technique_id")
        if tid and tid in SECT_SPECIAL_TECHNIQUES:
            if tid not in player_sect["techniques_learned"]:
                player_sect["techniques_learned"].append(tid)
    if sector.get("feature_type") == "heal_scripture":
        tid = sector.get("technique_id")
        if tid and tid in SECT_SPECIAL_TECHNIQUES:
            if tid not in player_sect["techniques_learned"]:
                player_sect["techniques_learned"].append(tid)
    return True


def leave_sect():
    player_sect["joined"] = False
    player_sect["sect_name"] = None
    player_sect["sect_star"] = 0
    player_sect["contribution"] = 0
    player_sect["rank"] = 0
    player_sect["techniques_learned"] = []
    player_sect["task_lv"] = 1
    player_sect["task_start_time"] = 0
    player_sect["task_contrib_accumulated"] = 0
    player_sect["meditate_active"] = False


def get_player_sect_feature():
    if not player_sect["joined"] or not player_sect["sect_name"]:
        return None
    sector = get_sect_info(player_sect["sect_name"])
    if sector:
        return {
            "feature": sector["feature"],
            "feature_desc": sector["feature_desc"],
            "feature_type": sector["feature_type"],
            "feature_value": sector.get("feature_value", 0),
            "technique_id": sector.get("technique_id"),
        }
    return None

# ==================== 职位系统函数 ====================

def get_current_rank():
    """获取当前职位信息"""
    rank_id = player_sect.get("rank", 0)
    if 0 <= rank_id < len(SECT_RANKS):
        return SECT_RANKS[rank_id]
    return SECT_RANKS[0]


def get_next_rank():
    """获取下一级职位（用于显示升级条件）"""
    rank_id = player_sect.get("rank", 0)
    next_id = rank_id + 1
    if next_id < len(SECT_RANKS):
        return SECT_RANKS[next_id]
    return None


def promote_rank():
    """提升职位，返回 (成功, 新职位名)"""
    rank_id = player_sect.get("rank", 0)
    next_rank = get_next_rank()
    if not next_rank:
        return False, "已达到最高职位"
    if player_sect["contribution"] < next_rank["contrib_required"]:
        return False, f"贡献不足（需 {next_rank['contrib_required']}）"
    player_sect["contribution"] -= next_rank["contrib_required"]
    player_sect["rank"] = rank_id + 1
    return True, next_rank["name"]

# ==================== 任务系统函数 ====================

def update_tasks():
    """
    每帧调用，自动结算已完成的任务周期
    返回：本次结算获得的贡献值
    """
    if not player_sect["joined"] or player_sect["task_start_time"] == 0:
        return 0

    task_lv = player_sect["task_lv"]
    task_info = None
    for tl in TASK_LEVELS:
        if tl["lv"] == task_lv:
            task_info = tl
            break
    if not task_info:
        return 0

    elapsed = time.time() - player_sect["task_start_time"]
    task_duration = task_info["time_minutes"] * 60

    earned = 0
    contrib_bonus = 1.0
    feature = get_player_sect_feature()
    if feature and feature["feature_type"] == "contrib_bonus":
        contrib_bonus = 1.0 + feature["feature_value"]

    while elapsed >= task_duration:
        earned += int(task_info["contrib_per_min"] * task_info["time_minutes"] * contrib_bonus)
        player_sect["task_start_time"] += task_duration
        elapsed -= task_duration

    if earned > 0:
        player_sect["contribution"] += earned

    return earned


def change_task_level(new_lv):
    """手动更换任务等级"""
    rank = get_current_rank()
    if new_lv > rank["max_task_lv"]:
        return False
    task_info = None
    for tl in TASK_LEVELS:
        if tl["lv"] == new_lv:
            task_info = tl
            break
    if not task_info:
        return False

    player_sect["task_lv"] = new_lv
    player_sect["task_start_time"] = time.time()
    player_sect["task_contrib_accumulated"] = 0
    return True


def get_task_progress():
    """获取当前任务进度 (0.0~1.0) 和剩余秒数"""
    task_lv = player_sect["task_lv"]
    task_info = None
    for tl in TASK_LEVELS:
        if tl["lv"] == task_lv:
            task_info = tl
            break
    if not task_info:
        return 0, 0

    elapsed = time.time() - player_sect["task_start_time"]
    task_duration = task_info["time_minutes"] * 60
    remaining = max(0, task_duration - elapsed)
    progress = min(1.0, elapsed / task_duration)
    return progress, remaining

# ==================== 参悟堂函数 ====================

def start_meditate():
    """开始参悟（消耗贡献，加速修炼1小时）"""
    if player_sect["meditate_active"]:
        return False, "已在参悟中"
    rank = get_current_rank()
    cost = 30  # 基础消耗
    if player_sect["contribution"] < cost:
        return False, f"贡献不足（需 {cost} 点）"
    player_sect["contribution"] -= cost
    player_sect["meditate_active"] = True
    player_sect["meditate_start_time"] = time.time()
    player_sect["meditate_bonus"] = rank["meditate_bonus"]
    return True, f"参悟开始！修炼速度 ×{rank['meditate_bonus']:.0%}（持续1小时）"


def get_meditate_status():
    """获取参悟状态：是否激活、剩余秒数、当前倍率"""
    if not player_sect["meditate_active"]:
        return False, 0, 0

    elapsed = time.time() - player_sect["meditate_start_time"]
    remaining = max(0, player_sect["meditate_duration"] - elapsed)
    if remaining <= 0:
        player_sect["meditate_active"] = False
        return False, 0, 0

    return True, remaining, player_sect["meditate_bonus"]

# ==================== 贡献堂函数 ====================

def buy_shop_item(category, item_index):
    """购买贡献堂物品，返回 (成功, 消息)"""
    if category not in CONTRIB_SHOP:
        return False, "分类不存在"
    items = CONTRIB_SHOP[category]
    if item_index < 0 or item_index >= len(items):
        return False, "物品不存在"
    item = items[item_index]
    cost = item["cost"]

    # 唐门/锤铁山的装备折扣
    feature = get_player_sect_feature()
    if item["type"] == "equip" and feature and feature["feature_type"] == "equip_discount":
        cost = int(cost * feature["feature_value"])

    if player_sect["contribution"] < cost:
        return False, f"贡献不足（需 {cost} 点）"

    player_sect["contribution"] -= cost
    return True, f"成功兑换【{item['name']}】，消耗 {cost} 贡献"