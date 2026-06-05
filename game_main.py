"""
仙道永恒 - 游戏主程序
修仙肉鸽游戏（弹幕射击+二次元风格+广告变现）
解决中文显示问题，实现完整的界面切换逻辑
"""

import pygame
import sys
import os
import threading
import time
from font_utils import FontManager, get_font_manager
from title_screen import TitleScreen, run_title_screen
from spiritual_root_screen import SpiritualRootScreen, run_spiritual_root_screen
from main_menu import MainMenu, run_main_menu
from name_input_screen import NameInputScreen, run_name_input
from character_panel import CharacterPanel, run_character_panel
from inventory_panel import InventoryPanel, run_inventory_panel
from equipment_panel import EquipmentPanel, run_equipment_panel
from battle_panel import BattlePanel, run_battle_panel
from background_combat import BackgroundCombat
from combat_renderer import CombatRenderer, draw_combat_status_indicator
from ling_shi_data import LingShiWallet
from ling_shi_renderer import draw_ling_shi_count
from music_manager import MusicManager, GameInterfaceManager
from settings_manager import SettingsManager, get_settings_manager
from settings_screen import SettingsScreen, run_settings_screen
from save_manager import get_save_manager

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# 将配置文件的相对路径更新为绝对路径
if os.path.dirname(__file__) != "":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 更新模块内的配置路径
import title_screen
import spiritual_root_screen
import main_menu
import character_panel
import inventory_panel
import equipment_panel
import battle_panel
title_screen.CONFIG_PATH = CONFIG_PATH
spiritual_root_screen.CONFIG_PATH = CONFIG_PATH
main_menu.CONFIG_PATH = CONFIG_PATH
character_panel.CONFIG_PATH = CONFIG_PATH
inventory_panel.CONFIG_PATH = CONFIG_PATH
equipment_panel.CONFIG_PATH = CONFIG_PATH
battle_panel.CONFIG_PATH = CONFIG_PATH


class Game:
    """游戏主类"""
    
    def __init__(self):
        """初始化游戏"""
        # 初始化Pygame
        pygame.init()
        
        # 加载配置
        self.load_config()
        
        # 设置显示
        width = self.config.get("display", {}).get("width", 1280)
        height = self.config.get("display", {}).get("height", 720)
        fullscreen = self.config.get("display", {}).get("fullscreen", False)
        
        if fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))
        
        # 设置窗口标题
        game_title = self.config.get("game", {}).get("title", "仙道永恒")
        pygame.display.set_caption(game_title)
        
        # 初始化字体管理器
        self.font_manager = FontManager(CONFIG_PATH)
        
        # 初始化设置系统
        self.settings_manager = get_settings_manager()
        
        # 初始化音乐系统
        self.music_manager = MusicManager()
        self.interface_manager = GameInterfaceManager(self.music_manager)
        
        # 加载主界面音乐
        main_music_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "修仙背景音乐_鬼谷风格.mid")
        if os.path.exists(main_music_file):
            self.music_manager.load_music('main_menu', main_music_file)
            print(f"🎵 主界面音乐加载成功: {os.path.basename(main_music_file)}")
        else:
            print("⚠️ 主界面音乐文件未找到，将静音运行")
        
        # 加载战斗音乐
        battle_music_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "战斗背景音乐_悲壮战斗版.mid")
        if os.path.exists(battle_music_file):
            self.music_manager.load_music('battle', battle_music_file)
            print(f"🎵 战斗音乐加载成功: {os.path.basename(battle_music_file)}")
        else:
            print("⚠️ 战斗音乐文件未找到，战斗将静音")
        
        # 应用保存的音量设置
        self.apply_volume_settings()
        
        # 游戏状态
        self.current_state = "title_screen"  # 从标题界面开始
        self.running = True
        self.spiritual_root_data = None  # 灵根抽取结果
        
        # 后台战斗系统
        self.background_combat = None
        self.combat_renderer = None
        self.combat_status = None
        self.current_map_id = None
        self.combat_result = None
        self.combat_drops = None
        
        # 灵石钱包系统
        self.ling_shi_wallet = LingShiWallet()
        
        # 存档系统
        self.save_manager = get_save_manager()
        self._last_auto_save_time = time.time()
        self._auto_save_interval = 60  # 自动存档间隔（秒）
        
        # 界面路由映射
        self.state_handlers = {
            "title_screen": self.run_title_screen,
            "load_game": self.run_load_game,
            "name_input": self.run_name_input,
            "spiritual_root": self.run_spiritual_root,
            "profession_select": self.run_profession_select,
            "main_menu": self.run_main_menu,
            "character": self.run_character_panel,
            "inventory": self.run_inventory_panel,
            "sect": self.run_sect_panel,
            "settings": self.run_settings_screen,
            "battle_历练之路": self.run_adventure_select,
            "battle_锁妖塔": self.run_tower_select,
            "battle_远古战场": self.run_ancient_select,
            "adventure_map": self.run_adventure_map,
            "combat_view": self.run_combat_view,
            "combat_result": self.run_combat_result,
            "combat_death": self.run_combat_death,
            "craft_炼丹": self.run_craft_pill,
            "craft_炼器": self.run_craft_artifact,
            "craft_绘符": self.run_craft_talisman,
        }
        
        print(f"✅ 游戏初始化完成 - {game_title} v{self.config.get('game', {}).get('version', '1.0.0')}")
        print(f"📺 屏幕大小: {width}x{height}")
        print(f"🔤 字体路径: {self.config.get('font', {}).get('primary', '默认')}")
    
    def load_config(self):
        """加载配置文件"""
        import json
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print("✅ 配置文件加载成功")
        except FileNotFoundError:
            print("⚠️ 配置文件未找到，使用默认配置")
            self.config = self.get_default_config()
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}，使用默认配置")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "game": {"title": "仙道永恒", "version": "1.0.0"},
            "display": {"width": 1280, "height": 720, "fullscreen": False, "fps": 60},
            "font": {
                "primary": "assets/fonts/STXINGKA.TTF",
                "fallback": "assets/fonts/simhei.ttf",
                "title_size": 72, "large_size": 48, "medium_size": 32,
                "small_size": 24, "button_size": 28
            },
            "colors": {
                "background": [20, 20, 40],
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
    
    def run_name_input(self):
        """运行角色取名界面"""
        result = run_name_input(self.screen, self.ling_shi_wallet.amount)
        if result == "__quit__":
            self.running = False
        elif result is None:
            # 返回标题界面
            self.switch_state("title_screen")
        else:
            # 写入玩家名字
            import realm_data
            realm_data.player["name"] = result
            print(f"📛 角色命名: {result}")
            self.switch_state("spiritual_root")

    def run_spiritual_root(self):
        """运行灵根抽取界面"""
        result = run_spiritual_root_screen(self.screen, self.ling_shi_wallet.amount)
        if result is None:
            self.running = False
            return
        self.spiritual_root_data = result
        # 写入功法数据模块
        import gongfa_data
        gongfa_data.player_gongfa["spiritual_root"] = (
            result["root_type"], result["elements"], result["bonus"]
        )
        print(f"✅ 灵根抽取完成: {result['root_type']} ({', '.join(result['elements'])})")
        self.switch_state("profession_select")

    def run_profession_select(self):
        """运行职业选择界面"""
        from profession_select import run_profession_select
        result = run_profession_select(self.screen, self.spiritual_root_data, self.ling_shi_wallet.amount)
        if result is None:
            self.running = False
            return
        print(f"✅ 职业选择完成: {result}")
        self.switch_state("main_menu")
        # 发放初始炼丹材料
        import alchemy_data as ad
        ad.seed_test_materials()
        # 角色创建完成后立即存档到槽位1
        game_data = self.save_manager.collect_game_data(ling_shi_amount=self.ling_shi_wallet.amount)
        self.save_manager.save_game(1, game_data)
        print("💾 新游戏自动存档完成")

    def run_main_menu(self):
        """运行主菜单界面（带战斗状态指示器）"""
        result = run_main_menu(self.screen, self._get_combat_status(), self.background_combat is not None, self.ling_shi_wallet.amount, self.ling_shi_wallet)
        self.handle_state_result(result)
    
    def run_settings_screen(self):
        """运行设置界面"""
        result = run_settings_screen(self.screen, self.music_manager, self.ling_shi_wallet.amount)
        if result == "goto_main_menu":
            # 从设置返回主菜单时，重新应用音量设置
            self.apply_volume_settings()
            self.switch_state("main_menu")
        elif result == "goto_title_screen":
            self.switch_state("title_screen")
        elif result == "quit":
            self.running = False
        else:
            self.switch_state("main_menu")
    
    def apply_volume_settings(self):
        """应用音量设置到音乐管理器"""
        current_interface = self.interface_manager.get_current_interface()
        if current_interface:
            normalized_volume = self.settings_manager.get_normalized_volume(current_interface)
            self.music_manager.set_volume(normalized_volume)
    
    def run_adventure_select(self):
        """历练之路 - 地图选择"""
        print("[DEBUG] run_adventure_select: importing adventure_select...")
        from adventure_select import run_adventure_select
        print("[DEBUG] run_adventure_select: calling run_adventure_select()...")
        result = run_adventure_select(self.screen, self.ling_shi_wallet.amount)
        print(f"[DEBUG] run_adventure_select: result={result}")
        if result is None:
            self.switch_state("main_menu")
            return
        self.current_map_id = result
        print(f"✅ 选择地图: {result}")
        self.switch_state("adventure_map")
    
    def run_adventure_map(self):
        """进入地图并开始战斗（后台模式）"""
        # 启动后台战斗模拟
        try:
            self.background_combat = BackgroundCombat(self.current_map_id, self.screen.get_width(), self.screen.get_height(), self.ling_shi_wallet)
            self.background_combat.start()
            self.combat_renderer = CombatRenderer(self.screen, self.config["font"]["primary"])
            print(f"✅ 后台战斗启动: {self.current_map_id}")
            self.switch_state("combat_view")
        except Exception as e:
            print(f"❌ 后台战斗启动失败: {e}")
            self.switch_state("main_menu")
    
    def run_combat_result(self):
        """战斗结果界面"""
        from combat_result import run_combat_result
        result = run_combat_result(self.screen, self.combat_result, self.combat_drops, self.current_map_id, self.ling_shi_wallet.amount)
        if result == "retry":
            self.switch_state("adventure_map")
        else:
            self.switch_state("main_menu")
    
    def run_combat_view(self):
        """战斗画面（后台战斗的实时渲染）"""
        clock = pygame.time.Clock()
        font_path = self.config["font"]["primary"]
        
        # 导入修炼系统
        from character_panel import _update_cultivation
        
        while self.current_state == "combat_view" and self.running:
            dt = clock.tick(60) / 1000.0
            
            # 更新修炼系统（即使在战斗中）
            gained, finished = _update_cultivation()
            if gained > 0:
                print(f"获得修为: {gained}")
            
            # 处理输入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # 退出战斗画面，战斗继续后台运行
                        # 先清空事件队列防止残留事件影响后续界面
                        pygame.event.clear()
                        self.switch_state("main_menu")
                        return
                    if event.key == pygame.K_b:
                        # 激活Boss
                        if self.background_combat:
                            self.background_combat.activate_boss()
            
            # 检查战斗是否结束
            if self.background_combat:
                end_info = self.background_combat.get_combat_end_info()
                if end_info:
                    reason = end_info["reason"]
                    drops = end_info["drops"]
                    self.background_combat.stop()
                    self.combat_result = reason
                    self.combat_drops = drops
                    self.background_combat = None
                    self.combat_renderer = None
                    if reason == "victory":
                        pygame.event.clear()
                        self.switch_state("combat_result")
                    else:
                        pygame.event.clear()
                        self.switch_state("combat_death")
                    return
            
            # 渲染战斗画面
            if self.background_combat and self.combat_renderer:
                try:
                    snapshot = self.background_combat.snapshot()
                    self.combat_renderer.render(snapshot)
                    draw_ling_shi_count(self.screen, self.ling_shi_wallet.amount)
                except Exception as e:
                    print(f"战斗渲染异常: {e}")
                finally:
                    pygame.display.flip()
    
    def run_combat_death(self):
        """角色死亡界面"""
        from combat_death import run_combat_death
        result = run_combat_death(self.screen, self.combat_drops or [], self.current_map_id, self.ling_shi_wallet.amount)
        if result == "retry":
            self.switch_state("adventure_map")
        else:
            self.switch_state("main_menu")
    
    def run_tower_select(self):
        """锁妖塔（占位）"""
        from combat_placeholder import run_combat_placeholder
        result = run_combat_placeholder(self.screen, "锁妖塔", "逐层攀登，挑战极限", self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_ancient_select(self):
        """远古战场（占位）"""
        from combat_placeholder import run_combat_placeholder
        result = run_combat_placeholder(self.screen, "远古战场", "与远古英灵交锋", self.ling_shi_wallet.amount)
        self.handle_state_result(result)
    
    def run_character_panel(self):
        """运行人物界面（带战斗状态指示器）"""
        result = run_character_panel(self.screen, self._get_combat_status(), self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_inventory_panel(self):
        """运行背包界面（带战斗状态指示器）"""
        result = run_inventory_panel(self.screen, self._get_combat_status(), self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_sect_panel(self):
        """运行宗门界面（占位，返回主菜单）"""
        from craft_placeholder import run_craft_placeholder
        result = run_craft_placeholder(self.screen, "宗门", "天下修仙者，皆聚于宗门之下", self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_equipment_panel(self):
        """运行装备界面（带战斗状态指示器）"""
        result = run_equipment_panel(self.screen, self._get_combat_status(), self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_craft_pill(self):
        """丹药炼制界面（占位）"""
        from craft_placeholder import run_craft_placeholder
        result = run_craft_placeholder(self.screen, "炼丹", "炉火纯青，丹成九转", self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_craft_artifact(self):
        """法器炼制界面（占位）"""
        from craft_placeholder import run_craft_placeholder
        result = run_craft_placeholder(self.screen, "炼器", "千锤百炼，神兵出世", self.ling_shi_wallet.amount)
        self.handle_state_result(result)

    def run_craft_talisman(self):
        """符箓绘制界面（占位）"""
        from craft_placeholder import run_craft_placeholder
        result = run_craft_placeholder(self.screen, "绘符", "笔走龙蛇，符成惊天地", self.ling_shi_wallet.amount)
        self.handle_state_result(result)
    
    def handle_state_result(self, result):
        """处理界面切换结果"""
        if result is None:
            return
        
        if result == "quit":
            self.running = False
        elif result == "start_game":
            self.switch_state("name_input")  # 标题 → 取名
        elif result == "goto_main_menu":
            self.switch_state("main_menu")
        elif result == "goto_settings":
            self.switch_state("settings")
        elif result.startswith("goto_"):
            target = result.replace("goto_", "")
            self.switch_state(target)
    
    def run_title_screen(self):
        """运行标题界面"""
        result = run_title_screen(self.screen, self.ling_shi_wallet.amount)
        if result == "load_game":
            self.run_load_game()
        else:
            self.handle_state_result(result)
    
    def run_load_game(self):
        """读取存档界面 - 列出所有存档供选择"""
        import pygame
        from font_utils import FontManager
        import traceback
        
        print("[LOAD_UI] 进入读取存档界面")
        try:
            font_manager = FontManager(CONFIG_PATH)
        except Exception as e:
            print(f"[LOAD_UI] ❌ FontManager 初始化失败: {e}")
            traceback.print_exc()
            return
        
        clock = pygame.time.Clock()
        
        # 获取存档列表
        try:
            slots = self.save_manager.get_available_slots()
            print(f"[LOAD_UI] 找到 {len(slots)} 个存档")
        except Exception as e:
            print(f"[LOAD_UI] ❌ 获取存档列表失败: {e}")
            traceback.print_exc()
            return
        
        if not slots:
            # 没有存档，显示提示
            self._show_no_save_message(font_manager, clock)
            return
        
        # 按时间戳倒序排列
        slots.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 存档选择界面
        scroll_offset = 0
        max_visible = 8
        selected_index = 0
        
        while self.running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # 返回标题界面
                    if event.key == pygame.K_DOWN:
                        selected_index = min(selected_index + 1, len(slots) - 1)
                        if selected_index >= scroll_offset + max_visible:
                            scroll_offset = selected_index - max_visible + 1
                    if event.key == pygame.K_UP:
                        selected_index = max(selected_index - 1, 0)
                        if selected_index < scroll_offset:
                            scroll_offset = selected_index
                    if event.key == pygame.K_RETURN:
                        # 加载选中的存档
                        self._load_selected_save(slots[selected_index]["slot_id"])
                        return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # 检查是否点击了某个存档条目
                    for i in range(scroll_offset, min(scroll_offset + max_visible, len(slots))):
                        item_y = 180 + (i - scroll_offset) * 55
                        item_rect = pygame.Rect(100, item_y, self.screen.get_width() - 200, 50)
                        if item_rect.collidepoint(mouse_pos):
                            self._load_selected_save(slots[i]["slot_id"])
                            return
                    # 检查返回按钮
                    back_rect = pygame.Rect(100, self.screen.get_height() - 80, 120, 45)
                    if back_rect.collidepoint(mouse_pos):
                        return
            
            # 绘制存档选择界面
            self.screen.fill((245, 240, 228))
            
            # 标题
            title = font_manager.render_text("读取存档", "title", (50, 40, 25), 48)
            self.screen.blit(title, ((self.screen.get_width() - title.get_width()) // 2, 40))
            
            # 分隔线
            lx = (self.screen.get_width() - 400) // 2
            pygame.draw.line(self.screen, (100, 90, 75, 100), (lx, 100), (lx + 400, 100), 1)
            
            # 存档列表
            for i in range(scroll_offset, min(scroll_offset + max_visible, len(slots))):
                slot = slots[i]
                item_y = 180 + (i - scroll_offset) * 55
                
                is_selected = (i == selected_index)
                
                # 条目背景
                item_rect = pygame.Rect(100, item_y, self.screen.get_width() - 200, 50)
                if is_selected:
                    pygame.draw.rect(self.screen, (200, 190, 160, 200), item_rect, border_radius=6)
                    pygame.draw.rect(self.screen, (80, 70, 55, 220), item_rect, width=2, border_radius=6)
                else:
                    pygame.draw.rect(self.screen, (232, 227, 214, 150), item_rect, border_radius=6)
                    pygame.draw.rect(self.screen, (150, 140, 120, 100), item_rect, width=1, border_radius=6)
                
                # 存档信息
                info_text = f"存档 {slot['slot_id']:03d}  |  {slot['player_name']}  |  {slot['realm']}第{slot['stage']}阶  |  灵石: {slot['ling_shi']}  |  {slot.get('save_time', '')}"
                info_surf = font_manager.render_text(info_text, "small", (40, 30, 18), 18)
                self.screen.blit(info_surf, (115, item_y + 15))
            
            # 操作提示
            hint = "↑↓ 选择  Enter 确认  ESC 返回"
            hint_surf = font_manager.render_text(hint, "small", (120, 110, 95), 18)
            self.screen.blit(hint_surf, ((self.screen.get_width() - hint_surf.get_width()) // 2, self.screen.get_height() - 120))
            
            # 返回按钮
            back_rect = pygame.Rect(100, self.screen.get_height() - 80, 120, 45)
            pygame.draw.rect(self.screen, (150, 130, 80, 200), back_rect, border_radius=6)
            pygame.draw.rect(self.screen, (180, 160, 100, 220), back_rect, width=1, border_radius=6)
            back_text = font_manager.render_text("返回", "medium", (40, 30, 18), 22)
            self.screen.blit(back_text, (back_rect.x + (back_rect.width - back_text.get_width()) // 2, back_rect.y + 10))
            
            # 灵石显示
            from ling_shi_renderer import draw_ling_shi_count
            draw_ling_shi_count(self.screen, self.ling_shi_wallet.amount)
            
            pygame.display.flip()
    
    def _show_no_save_message(self, font_manager, clock):
        """显示无存档提示"""
        start_time = time.time()
        while self.running and time.time() - start_time < 2.0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
            
            self.screen.fill((245, 240, 228))
            
            msg = font_manager.render_text("暂无存档", "title", (120, 100, 80), 40)
            self.screen.blit(msg, ((self.screen.get_width() - msg.get_width()) // 2, self.screen.get_height() // 2 - 30))
            
            sub = font_manager.render_text("请先开始新游戏创建存档", "medium", (150, 140, 120), 24)
            self.screen.blit(sub, ((self.screen.get_width() - sub.get_width()) // 2, self.screen.get_height() // 2 + 30))
            
            from ling_shi_renderer import draw_ling_shi_count
            draw_ling_shi_count(self.screen, self.ling_shi_wallet.amount)
            
            pygame.display.flip()
            clock.tick(60)
    
    def _load_selected_save(self, slot_id):
        """加载选中的存档并恢复游戏状态"""
        import traceback
        print(f"[LOAD] === 开始加载存档 slot_id={slot_id} ===")
        try:
            data = self.save_manager.load_game(slot_id)
            if not data:
                print(f"❌ 加载存档失败: slot {slot_id}")
                return
            
            print(f"[LOAD] ✅ 存档文件读取成功")
            
            # 恢复玩家数据
            import realm_data
            import gongfa_data
            
            player_data = data.get("player", {})
            print(f"[LOAD] 恢复基础属性...")
            realm_data.player["name"] = player_data.get("name", "李云修")
            realm_data.player["realm_index"] = player_data.get("realm_index", 0)
            realm_data.player["cultivation"] = player_data.get("cultivation", 0)
            realm_data.player["current_stage"] = player_data.get("current_stage", 1)
            realm_data.player["attack"] = player_data.get("attack", 10)
            realm_data.player["hp"] = player_data.get("hp", 100)
            realm_data.player["max_hp"] = player_data.get("max_hp", realm_data.player.get("max_hp", 100))
            realm_data.player["mp"] = player_data.get("mp", realm_data.player.get("mp", 50))
            realm_data.player["max_mp"] = player_data.get("max_mp", realm_data.player.get("max_mp", 50))
            realm_data.player["defense"] = player_data.get("defense", 5)
            realm_data.player["free_points"] = player_data.get("free_points", 0)
            realm_data.player["spirit_stones"] = player_data.get("spirit_stones", 0)
            
            # 恢复灵根数据
            print(f"[LOAD] 恢复灵根数据...")
            root_data = player_data.get("spiritual_root")
            if root_data:
                gongfa_data.player_gongfa["spiritual_root"] = (
                    root_data["type"], root_data["elements"], root_data["bonus"]
                )
            
            # 恢复功法数据
            print(f"[LOAD] 恢复功法数据...")
            equipped = player_data.get("equipped_gongfa", {})
            if equipped:
                gongfa_data.player_gongfa["equipped"] = equipped
            
            # 恢复灵石
            print(f"[LOAD] 恢复灵石...")
            ling_shi = player_data.get("ling_shi", 0)
            if ling_shi > self.ling_shi_wallet.amount:
                self.ling_shi_wallet.add(ling_shi - self.ling_shi_wallet.amount)
            
            # 恢复修炼状态
            print(f"[LOAD] 恢复修炼状态...")
            cult_state = player_data.get("cultivation_state")
            if cult_state:
                realm_data.cultivation_state.update(cult_state)
            
            # 恢复洞府数据
            print(f"[LOAD] 恢复洞府数据...")
            cave_data = player_data.get("cave_data")
            if cave_data:
                import cave_data as cd
                if "herb_garden" in cave_data:
                    cd.player_cave["herb_garden"] = cave_data["herb_garden"]
                if "spirit_array" in cave_data:
                    cd.player_cave["spirit_array"] = cave_data["spirit_array"]
                if "apprentice" in cave_data:
                    cd.player_cave["apprentice"] = cave_data["apprentice"]
            
            # 恢复藏宝阁数据
            print(f"[LOAD] 恢复藏宝阁数据...")
            treasure_data = player_data.get("treasure_data")
            if treasure_data:
                import treasure_data as td
                if "player_treasure" in treasure_data:
                    td.player_treasure = treasure_data["player_treasure"]

            # 恢复炼丹数据
            print(f"[LOAD] 恢复炼丹数据...")
            alchemy_data = player_data.get("alchemy_data")
            import alchemy_data as ad
            if alchemy_data:
                ad.player_alchemy["level"] = alchemy_data.get("level", 1)
                ad.player_alchemy["exp"] = alchemy_data.get("exp", 0)
                ad.player_alchemy["materials"] = alchemy_data.get("materials", {})
                ad.player_alchemy["pills"] = alchemy_data.get("pills", [])
            else:
                ad.seed_test_materials()

            # 恢复炼器数据
            print(f"[LOAD] 恢复炼器数据...")
            forge_data = player_data.get("forge_data")
            import forge_data as fd
            if forge_data:
                fd.player_forge["level"] = forge_data.get("level", 1)
                fd.player_forge["exp"] = forge_data.get("exp", 0)
                fd.player_forge["enhance_materials"] = forge_data.get("enhance_materials", {})
                fd.player_forge["forge_materials"] = forge_data.get("forge_materials", {})
            else:
                fd.seed_test_materials()
            
            # 恢复设置
            print(f"[LOAD] 恢复设置...")
            settings_data = data.get("settings", {})
            if settings_data:
                audio_settings = settings_data.get("audio", {})
                for key, value in audio_settings.items():
                    self.settings_manager.set_setting("audio", key, value)
                display_settings = settings_data.get("display", {})
                for key, value in display_settings.items():
                    self.settings_manager.set_setting("display", key, value)
                self.settings_manager.save_settings()
            
            # 应用音量设置
            print(f"[LOAD] 应用音量设置...")
            self.apply_volume_settings()
            
            # 直接进入主菜单
            print(f"[LOAD] 切换到主菜单...")
            self.switch_state("main_menu")
            print(f"[LOAD] === 存档加载完成 ===")
        except Exception as e:
            print(f"[LOAD] ❌❌❌ 存档加载崩溃: {e}")
            traceback.print_exc()
            # 尝试回退到标题界面
            try:
                self.switch_state("title_screen")
            except:
                pass
    
    def switch_state(self, new_state):
        """切换游戏状态"""
        old_state = self.current_state
        
        if new_state in self.state_handlers:
            self.current_state = new_state
            print(f"🔀 界面切换: {old_state} -> {new_state}")
            
            # 清空事件队列，防止事件泄露到下一界面
            pygame.event.clear()
            
            # 音乐切换：战斗相关界面播战斗音乐，其他界面播主界面音乐
            try:
                self.interface_manager.switch_interface(new_state)
            except Exception as e:
                print(f"⚠️ 音乐切换失败（非致命）: {e}")
            
            # 应用音量设置
            try:
                self.apply_volume_settings()
            except Exception as e:
                print(f"⚠️ 音量设置失败（非致命）: {e}")
        else:
            print(f"❌ 未知界面: {new_state}")
    
    def run(self):
        """运行游戏主循环"""
        print("🎮 游戏启动中...")
        print("=" * 50)
        
        # 开始播放主界面音乐
        self.interface_manager.switch_interface(self.current_state)
        
        # 外循环时钟（P1 修复：限帧避免 CPU 空转）
        outer_clock = pygame.time.Clock()
        
        while self.running:
            outer_clock.tick(60)  # P1: 限帧 60FPS，防止状态切换时空转死机
            
            # 防止 Windows 标记窗口为"未响应"（状态切换间隙确保事件泵工作）
            pygame.event.pump()
            
            # 检查是否需要自动存档（P2 修复：移至定期检查而非依赖状态切换）
            current_time = time.time()
            if current_time - self._last_auto_save_time >= self._auto_save_interval:
                self._perform_auto_save()
                self._last_auto_save_time = current_time
            
            # 运行当前界面（修炼更新由内部循环各自负责）
            handler = self.state_handlers.get(self.current_state)
            if handler:
                handler()
            else:
                print(f"❌ 未找到界面处理函数: {self.current_state}")
                self.running = False
            
            # 检查后台战斗是否结束（当不在战斗界面时）
            if (self.background_combat and
                self.current_state not in ["combat_view", "combat_result", "combat_death"]):
                end_info = self.background_combat.get_combat_end_info()
                if end_info:
                    reason = end_info["reason"]
                    drops = end_info["drops"]
                    self.background_combat.stop()
                    self.combat_result = reason
                    self.combat_drops = drops
                    self.background_combat = None
                    self.combat_renderer = None
                    if reason == "victory":
                        self.switch_state("combat_result")
                    else:
                        self.switch_state("combat_death")
        
        self.quit_game()
    
    def _perform_auto_save(self):
        """执行自动存档"""
        try:
            # 收集当前游戏数据
            game_data = self.save_manager.collect_game_data(
                ling_shi_amount=self.ling_shi_wallet.amount
            )
            game_data["meta"]["save_type"] = "auto"
            
            # 执行自动存档
            success = self.save_manager.auto_save(game_data)
            if success:
                print(f"✅ 自动存档完成 ({time.strftime('%H:%M:%S')})")
            else:
                print(f"❌ 自动存档失败")
        except Exception as e:
            print(f"❌ 自动存档异常: {e}")
    
    def _get_combat_status(self):
        """获取当前战斗状态快照（轻量级）"""
        if not self.background_combat:
            return None
        try:
            return self.background_combat.status_snapshot()
        except Exception:
            return None

    def quit_game(self):
        """退出游戏"""
        # 停止音乐
        self.music_manager.cleanup()
        # 停止后台战斗线程
        if self.background_combat:
            try:
                self.background_combat.stop()
            except Exception:
                pass
            self.background_combat = None
        print("👋 游戏退出")
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
