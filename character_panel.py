"""
仙道永恒 - 人物界面
显示角色属性、境界、修为等信息
"""

import pygame
import time
from font_utils import FontManager
import realm_data
import sect_data

CONFIG_PATH = "config.json"


# ==================== 修炼系统（内置于人物模块） ====================

def _get_cultivation_per_interval():
    """根据当前境界返回每次修炼间隔获得的修为（随机值）
    规则：基础7-12点 + 前境界满阶累计 + 当前境界内阶数加成
    练气n阶：7-12 + (n-1)×2-4
    筑基n阶：练气10阶 + 7-12 + (n-1)×10-20
    金丹n阶：筑基10阶 + 7-12 + (n-1)×50-100
    """
    import random
    lo, hi = _get_cultivation_range()
    return random.randint(lo, hi)


def _get_cultivation_range():
    """返回当前修炼每5秒修为范围 (min, max)，用于面板显示
    练气n阶：7-12 + (n-1)×2-4
    筑基n阶：练气10阶 + n×10-20
    金丹n阶：筑基10阶 + n×50-100
    """
    player = realm_data.player
    realm_index = player["realm_index"]
    current_stage = player["current_stage"]

    stage_min = [2, 10, 50, 250, 1250, 6250, 31250, 156250, 781250]

    total_min = 7
    total_max = 12

    # 累加前境界满阶
    for r in range(realm_index):
        sm = stage_min[r]
        if r == 0:
            # 练气10阶: 7-12 + 9×2-4 = 25-48
            total_min += 9 * sm
            total_max += 9 * sm * 2
        else:
            # 其他境界10阶: 10 × 加成
            total_min += 10 * sm
            total_max += 10 * sm * 2

    # 当前境界内阶数加成
    if realm_index < len(stage_min):
        sm = stage_min[realm_index]
        if realm_index == 0:
            # 练气: (stage-1) × 加成
            total_min += (current_stage - 1) * sm
            total_max += (current_stage - 1) * sm * 2
        else:
            # 其他境界: stage × 加成
            total_min += current_stage * sm
            total_max += current_stage * sm * 2

    # 洞府聚灵阵加成
    import cave_data
    cave_boost = cave_data.get_cultivation_boost()
    total_min = int(total_min * (1 + cave_boost))
    total_max = int(total_max * (1 + cave_boost))

    return total_min, total_max


def _start_cultivation():
    """开始手动修炼（3分钟）"""
    state = realm_data.cultivation_state
    state["is_cultivating"] = True
    state["cultivation_start_time"] = time.time()
    state["last_gain_time"] = time.time()
    state["cultivation_per_interval"] = _get_cultivation_per_interval()
    return True


def _stop_cultivation():
    """停止手动修炼"""
    realm_data.cultivation_state["is_cultivating"] = False


def _get_cultivation_remaining():
    """获取修炼剩余时间（秒），-1 表示未在修炼"""
    state = realm_data.cultivation_state
    if not state["is_cultivating"]:
        return -1
    elapsed = time.time() - state["cultivation_start_time"]
    return max(0, int(state["cultivation_duration"] - elapsed))


def _update_cultivation():
    """每帧调用，返回 (gained_amount, is_finished)"""
    state = realm_data.cultivation_state
    player = realm_data.player

    if player["realm_index"] >= 1 and not state["auto_cultivation"]:
        state["auto_cultivation"] = True
        state["is_cultivating"] = True
        state["cultivation_start_time"] = time.time()
        state["last_gain_time"] = time.time()
        state["cultivation_per_interval"] = _get_cultivation_per_interval()

    if not state["is_cultivating"]:
        return 0, False

    now = time.time()

    if not state["auto_cultivation"]:
        elapsed = now - state["cultivation_start_time"]
        if elapsed >= state["cultivation_duration"]:
            state["is_cultivating"] = False
            return 0, True

    if now - state["last_gain_time"] >= state["cultivation_interval"]:
        gained = state["cultivation_per_interval"]
        player["cultivation"] += gained
        state["last_gain_time"] = now
        state["cultivation_per_interval"] = _get_cultivation_per_interval()
        return gained, False

    return 0, False


def _can_breakthrough():
    """检查是否可以突破到下一阶"""
    player = realm_data.player
    stage, progress, stage_total, realm_total = realm_data.get_stage_info(
        player["realm_index"], player["cultivation"], player["current_stage"]
    )
    return progress >= stage_total


def _try_breakthrough():
    """尝试突破，返回 (success, new_stage, new_realm_name)"""
    player = realm_data.player

    if not _can_breakthrough():
        return False, 0, ""

    realm_index = player["realm_index"]
    current_stage = player["current_stage"]
    stage, progress, stage_total, realm_total = realm_data.get_stage_info(
        realm_index, player["cultivation"], current_stage
    )

    player["current_stage"] += 1

    # 突破属性加成：每阶攻+3，血+15，防+2；跨大境界翻倍
    is_cross_realm = player["current_stage"] > realm_data.STAGES_PER_REALM
    multiplier = 2 if is_cross_realm else 1
    player["attack"] += 3 * multiplier
    player["hp"] += 15 * multiplier
    player["defense"] += 2 * multiplier

    if is_cross_realm:
        player["realm_index"] += 1
        player["current_stage"] = 1
        player["cultivation"] = 0  # 新境界从零开始
        new_realm = realm_data.get_realm_name(player["realm_index"])
        new_stage = 1
        realm_data.cultivation_state["cultivation_per_interval"] = _get_cultivation_per_interval()

        if player["realm_index"] >= 1:
            realm_data.cultivation_state["auto_cultivation"] = True
            realm_data.cultivation_state["is_cultivating"] = True
            realm_data.cultivation_state["cultivation_start_time"] = time.time()
            realm_data.cultivation_state["last_gain_time"] = time.time()

        return True, new_stage, new_realm
    else:
        return True, player["current_stage"], realm_data.get_realm_name(realm_index)


def _get_cultivation_status_text():
    """获取修炼状态文本"""
    state = realm_data.cultivation_state
    if state["auto_cultivation"]:
        return "自动修炼中（筑基期永久开启）"
    elif state["is_cultivating"]:
        remaining = _get_cultivation_remaining()
        minutes = remaining // 60
        seconds = remaining % 60
        return f"修炼中... 剩余 {minutes}:{seconds:02d}"
    else:
        return "未在修炼"


class CharacterPanel:
    """人物界面"""
    
    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)
        
        # 加载配置
        self.load_config()
        
        # 界面状态
        self.running = True
        self.next_state = None
        
        # 返回按钮
        self.return_button = pygame.Rect(30, 30, 120, 40)
        self.return_hovered = False
        
        # 开始修炼按钮
        self.cultivate_button = pygame.Rect(880, 400, 360, 50)
        self.cultivate_hovered = False
        
        # 突破按钮
        self.breakthrough_button = pygame.Rect(880, 470, 360, 50)
        self.breakthrough_hovered = False
        
        # 角色数据（从 realm_data 获取）
        self.update_character_data()
        print("✅ 人物界面初始化完成")
    
    def update_character_data(self):
        """根据 realm_data 更新角色数据"""
        p = realm_data.player
        realm_name = realm_data.get_realm_name(p["realm_index"])
        stage, progress, stage_total, realm_total = realm_data.get_stage_info(
            p["realm_index"], p["cultivation"], p["current_stage"]
        )
        realm_progress = int(p["cultivation"] / realm_total * 100) if realm_total > 0 else 0

        self.character_data = {
            "name": p["name"],
            "title": "初入仙途" if p["realm_index"] == 0 else "修仙者",
            "realm": f"{realm_name}期",
            "realm_stage": stage,
            "realm_progress": realm_progress,
            "cultivation": p["cultivation"],
            "realm_total": realm_total,
            "level": 1,
            "exp": 120,
            "exp_to_next": 500,
            "hp": p["hp"],
            "max_hp": p["hp"],
            "mp": 50,
            "max_mp": 50,
            "attack": p["attack"],
            "defense": p["defense"],
            "speed": 10,
            "spirit": 12,
            "luck": 5,
            "sect": sect_data.player_sect["sect_name"] if sect_data.player_sect.get("sect_name") else "散修",
            "spirit_stones": p["spirit_stones"]
        }
    
    def load_config(self):
        """加载配置"""
        import json
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "colors": {
                    "background": [20, 20, 40],
                    "panel_background": [30, 30, 60, 220],
                    "title_gold": [255, 215, 0],
                    "text_primary": [240, 240, 240],
                    "text_secondary": [180, 180, 200],
                    "button_normal": [60, 60, 120],
                    "button_hover": [100, 80, 180],
                    "button_text": [255, 255, 255],
                    "accent_cyan": [0, 200, 200],
                    "accent_purple": [160, 80, 255],
                    "border_color": [100, 100, 160]
                }
            }
    
    def create_background(self):
        """创建背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        colors = self.config["colors"]
        
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(colors["background"][0] * (1 - ratio * 0.3))
            g = int(colors["background"][1] * (1 - ratio * 0.2))
            b = int(colors["background"][2] * (1 + ratio * 0.3))
            pygame.draw.line(bg, (max(r, 0), max(g, 0), min(b, 255)), 
                           (0, y), (self.screen_width, y))
        
        return bg
    
    def draw_panel(self, screen, rect, title, content_lines, title_color=None):
        """绘制面板"""
        colors = self.config["colors"]
        if title_color is None:
            title_color = colors["accent_cyan"]
        
        # 面板背景
        panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, colors["panel_background"], 
                        (0, 0, rect.width, rect.height), 
                        border_radius=16)
        pygame.draw.rect(panel_surf, (*colors["border_color"], 200), 
                        (0, 0, rect.width, rect.height), 
                        width=2, border_radius=16)
        screen.blit(panel_surf, (rect.x, rect.y))
        
        # 标题
        title_surf = self.font_manager.render_text(title, "medium", title_color)
        screen.blit(title_surf, (rect.x + 20, rect.y + 15))
        
        # 分割线
        line_y = rect.y + 55
        pygame.draw.line(screen, (*colors["border_color"], 150), 
                        (rect.x + 15, line_y), (rect.x + rect.width - 15, line_y), 1)
        
        # 内容
        y_offset = rect.y + 70
        for line in content_lines:
            if isinstance(line, tuple):
                # (label, value, color)
                label, value, color = line
                text = f"{label}: {value}"
                text_surf = self.font_manager.render_text(text, "small", color)
            else:
                text_surf = self.font_manager.render_text(line, "small", colors["text_secondary"])
            
            screen.blit(text_surf, (rect.x + 20, y_offset))
            y_offset += 30
    
    def draw_progress_bar(self, screen, x, y, width, height, progress, 
                          fill_color, bg_color=None):
        """绘制进度条"""
        colors = self.config["colors"]
        if bg_color is None:
            bg_color = (40, 40, 80)
        
        # 背景
        pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=6)
        
        # 填充
        fill_width = int(width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, fill_color, 
                           (x, y, fill_width, height), border_radius=6)
        
        # 边框
        pygame.draw.rect(screen, colors["border_color"], 
                        (x, y, width, height), width=1, border_radius=6)
    
    def handle_events(self, events):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮悬停状态
        self.return_hovered = self.return_button.collidepoint(mouse_pos)
        self.cultivate_hovered = self.cultivate_button.collidepoint(mouse_pos)
        self.breakthrough_hovered = self.breakthrough_button.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.return_button.collidepoint(mouse_pos):
                        return "goto_main_menu"
                    elif self.cultivate_button.collidepoint(mouse_pos):
                        state = realm_data.cultivation_state
                        if state["is_cultivating"]:
                            _stop_cultivation()
                            print("停止修炼...")
                        else:
                            _start_cultivation()
                            print("开始修炼...")
                    elif self.breakthrough_button.collidepoint(mouse_pos):
                        if _can_breakthrough():
                            success, new_stage, new_realm = _try_breakthrough()
                            if success:
                                print(f"突破成功！当前境界: {new_realm} 第{new_stage}阶")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "goto_main_menu"
        
        return None
    
    def update(self):
        """更新界面"""
        # 更新修炼状态
        gained, finished = _update_cultivation()
        if gained > 0:
            print(f"获得修为: {gained}")
        
        # 更新角色数据
        self.update_character_data()
    
    def draw(self, screen):
        """绘制界面"""
        colors = self.config["colors"]
        data = self.character_data
        
        # 背景
        screen.blit(self.background, (0, 0))
        
        # 页面标题
        title_surf = self.font_manager.render_text("人物", "large", colors["title_gold"])
        title_x = (self.screen_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, 30))
        
        # 返回按钮
        btn_color = colors["button_hover"] if self.return_hovered else colors["button_normal"]
        pygame.draw.rect(screen, btn_color, self.return_button, border_radius=8)
        pygame.draw.rect(screen, colors["border_color"], self.return_button, 
                        width=1, border_radius=8)
        return_text = self.font_manager.render_text("← 返回", "small", colors["button_text"])
        return_x = self.return_button.centerx - return_text.get_width() // 2
        return_y = self.return_button.centery - return_text.get_height() // 2
        screen.blit(return_text, (return_x, return_y))
        
        # 左侧面板 - 基本信息
        left_panel = pygame.Rect(40, 100, 380, 580)
        basic_info = [
            ("道号", data["name"], colors["title_gold"]),
            ("称号", data["title"], colors["accent_cyan"]),
            ("宗门", data["sect"], colors["text_primary"]),
            ("灵石", str(data["spirit_stones"]), colors["accent_cyan"]),
        ]
        self.draw_panel(screen, left_panel, "基本信息", basic_info)
        
        # 境界进度条
        realm_y = left_panel.y + 220
        realm_label = self.font_manager.render_text(
            f"境界: {data['realm']} · 第{data['realm_stage']}阶", "small", colors["accent_purple"]
        )
        screen.blit(realm_label, (left_panel.x + 20, realm_y))
        
        self.draw_progress_bar(screen, left_panel.x + 20, realm_y + 35, 
                              left_panel.width - 40, 20, data["realm_progress"],
                              colors["accent_purple"])
        
        progress_text = self.font_manager.render_text(
            f"修为进度: {data['realm_progress']}%", "small", colors["text_secondary"]
        )
        screen.blit(progress_text, (left_panel.x + 20, realm_y + 65))
        
        # 等级经验
        exp_y = realm_y + 100
        level_label = self.font_manager.render_text(
            f"等级: Lv.{data['level']}", "small", colors["text_primary"]
        )
        screen.blit(level_label, (left_panel.x + 20, exp_y))
        
        self.draw_progress_bar(screen, left_panel.x + 20, exp_y + 35,
                              left_panel.width - 40, 20,
                              int(data["exp"] / data["exp_to_next"] * 100),
                              colors["accent_cyan"])
        
        exp_text = self.font_manager.render_text(
            f"经验: {data['exp']}/{data['exp_to_next']}", "small", colors["text_secondary"]
        )
        screen.blit(exp_text, (left_panel.x + 20, exp_y + 65))
        
        # 右侧面板 - 属性
        right_panel = pygame.Rect(460, 100, 380, 580)
        stats = [
            ("生命值", f"{data['hp']}/{data['max_hp']}", colors["text_primary"]),
            ("法力值", f"{data['mp']}/{data['max_mp']}", colors["text_primary"]),
            ("攻击力", str(data["attack"]), colors["text_primary"]),
            ("防御力", str(data["defense"]), colors["text_primary"]),
            ("速度", str(data["speed"]), colors["text_primary"]),
            ("灵力", str(data["spirit"]), colors["text_primary"]),
            ("气运", str(data["luck"]), colors["text_primary"]),
        ]
        self.draw_panel(screen, right_panel, "属性", stats)
        
        # 中间面板 - 修炼状态
        center_panel = pygame.Rect(880, 100, 360, 280)
        cultivation_status = _get_cultivation_status_text()
        stage, progress, stage_total, realm_total = realm_data.get_stage_info(
            realm_data.player["realm_index"], realm_data.player["cultivation"], realm_data.player["current_stage"]
        )
        progress_percent = int(progress / stage_total * 100) if stage_total > 0 else 0
        
        cultivation_info = [
            ("当前状态", cultivation_status, colors["accent_cyan"]),
            ("当前阶数", f"第{stage}阶", colors["text_primary"]),
            ("阶内进度", f"{progress_percent}% ({progress}/{stage_total})", colors["text_primary"]),
            ("修为总量", f"{realm_data.player['cultivation']}", colors["text_primary"]),
            ("修炼速度", f"{_get_cultivation_range()[0]}-{_get_cultivation_range()[1]}/5秒", colors["text_primary"]),
        ]
        self.draw_panel(screen, center_panel, "修炼", cultivation_info)
        
        # 开始修炼按钮
        btn_color = colors["button_hover"] if self.cultivate_hovered else colors["button_normal"]
        pygame.draw.rect(screen, btn_color, self.cultivate_button, border_radius=8)
        pygame.draw.rect(screen, colors["border_color"], self.cultivate_button, 
                        width=1, border_radius=8)
        state = realm_data.cultivation_state
        btn_text = "修炼结束" if state["is_cultivating"] else "开始修炼"
        cultivate_text = self.font_manager.render_text(btn_text, "medium", colors["button_text"])
        cultivate_x = self.cultivate_button.centerx - cultivate_text.get_width() // 2
        cultivate_y = self.cultivate_button.centery - cultivate_text.get_height() // 2
        screen.blit(cultivate_text, (cultivate_x, cultivate_y))
        
        # 突破按钮
        breakthrough_btn_color = colors["button_hover"] if self.breakthrough_hovered else colors["button_normal"]
        pygame.draw.rect(screen, breakthrough_btn_color, self.breakthrough_button, border_radius=8)
        pygame.draw.rect(screen, colors["border_color"], self.breakthrough_button, 
                        width=1, border_radius=8)
        can_breakthrough = _can_breakthrough()
        breakthrough_text_str = "突破！" if can_breakthrough else "修为不足"
        breakthrough_text = self.font_manager.render_text(breakthrough_text_str, "medium", 
                                                         colors["button_text"] if can_breakthrough else colors["text_secondary"])
        breakthrough_x = self.breakthrough_button.centerx - breakthrough_text.get_width() // 2
        breakthrough_y = self.breakthrough_button.centery - breakthrough_text.get_height() // 2
        screen.blit(breakthrough_text, (breakthrough_x, breakthrough_y))
        
        # 底部提示
        hint = "按 ESC 或点击返回按钮回到主菜单"
        hint_surf = self.font_manager.render_text(hint, "small", colors["text_secondary"])
        hint_x = (self.screen_width - hint_surf.get_width()) // 2
        screen.blit(hint_surf, (hint_x, self.screen_height - 35))


def run_character_panel(screen, combat_status=None, ling_shi_amount=0):
    """运行人物界面"""
    panel = CharacterPanel(screen.get_width(), screen.get_height())
    clock = pygame.time.Clock()
    
    while panel.running:
        events = pygame.event.get()
        result = panel.handle_events(events)
        panel.update()
        panel.draw(screen)
        
        # 绘制战斗状态指示器
        if combat_status:
            from combat_renderer import draw_combat_status_indicator
            font_path = panel.font_manager.config["font"]["primary"]
            draw_combat_status_indicator(screen, font_path, combat_status)
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        
        pygame.display.flip()
        clock.tick(60)
        
        if result:
            return result
    
    return "quit"
