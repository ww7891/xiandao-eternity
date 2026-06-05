"""
《仙道永恒》游戏音乐管理模块
作者：游戏开发团队
日期：2026-05-28
功能：管理游戏背景音乐，支持加载、播放、停止、音量调节等功能
"""

import pygame
import os
import sys

class MusicManager:
    """音乐管理器类"""

    def __init__(self):
        """初始化音乐管理器"""
        self.current_music = None
        self.volume = 0.5  # 默认音量50%
        self.is_playing = False
        self.mixer_available = False  # 混音器是否可用
        self.silent_mode = False  # 静音模式（MIDI 故障时启用）

        # 音乐文件路径
        self.music_files = {
            'main_menu': None,  # 主界面音乐
            'battle': None      # 战斗音乐（预留）
        }

        # 安全初始化音频混音器
        try:
            # 减小 buffer 避免延迟，添加异常处理防止 MIDI 卡死
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            self.mixer_available = True
            print("✅ 音频混音器初始化成功")
        except Exception as e:
            print(f"⚠️ 音频混音器初始化失败: {e}")
            print("⚠️ 游戏将以静音模式运行")
            self.mixer_available = False
            self.silent_mode = True
    
    def load_music(self, music_type, file_path):
        """
        加载音乐文件
        
        参数:
            music_type: 音乐类型 ('main_menu' 或 'battle')
            file_path: 音乐文件路径
        """
        if not os.path.exists(file_path):
            print(f"错误: 音乐文件不存在 - {file_path}")
            return False
        
        try:
            self.music_files[music_type] = file_path
            print(f"成功加载 {music_type} 音乐: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            print(f"加载音乐失败: {e}")
            return False
    
    def play_music(self, music_type, loops=-1):
        """
        播放指定类型的音乐

        参数:
            music_type: 音乐类型 ('main_menu' 或 'battle')
            loops: 循环次数，-1表示无限循环
        """
        # 静音模式或混音器不可用，直接返回成功（允许游戏继续运行）
        if self.silent_mode or not self.mixer_available:
            self.current_music = music_type
            self.is_playing = False
            return True

        if music_type not in self.music_files:
            print(f"错误: 未知的音乐类型 - {music_type}")
            return False

        if self.music_files[music_type] is None:
            print(f"⚠️ {music_type} 音乐未加载，静音运行")
            self.current_music = music_type
            return True

        # 检测是否是 MIDI 文件（可能导致卡死）
        file_path = self.music_files[music_type]
        is_midi = file_path.lower().endswith('.mid') or file_path.lower().endswith('.midi')

        if is_midi and self.silent_mode:
            self.current_music = music_type
            return True

        try:
            if self.is_playing:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass

            # 加载和播放音乐（MIDI 文件可能在此卡死）
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loops=loops)
            pygame.mixer.music.set_volume(self.volume)

            self.current_music = music_type
            self.is_playing = True

            print(f"🎵 开始播放 {music_type} 音乐 (音量: {int(self.volume * 100)}%)")
            return True
        except pygame.error as e:
            print(f"⚠️ 播放音乐失败 (pygame错误): {e}")
            # MIDI 播放失败时，启用静音模式避免后续卡死
            if is_midi:
                print("⚠️ MIDI 播放失败，切换为静音模式")
                self.silent_mode = True
            self.current_music = music_type
            return True  # 返回 True 让游戏继续运行
        except Exception as e:
            print(f"⚠️ 播放音乐失败: {e}")
            self.silent_mode = True  # 任何异常都启用静音模式
            self.current_music = music_type
            return True  # 返回 True 让游戏继续运行
    
    def stop_music(self):
        """停止播放音乐"""
        if not self.mixer_available:
            self.is_playing = False
            self.current_music = None
            return True
        try:
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.current_music = None
                print("🔇 音乐已停止")
                return True
        except Exception:
            pass
        return False

    def pause_music(self):
        """暂停播放音乐"""
        if not self.mixer_available or self.silent_mode:
            return True
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                print("⏸️ 音乐已暂停")
                return True
        except Exception:
            pass
        return False

    def unpause_music(self):
        """恢复播放音乐"""
        if not self.mixer_available or self.silent_mode:
            return True
        try:
            if self.is_playing:
                pygame.mixer.music.unpause()
                print("▶️ 音乐已恢复")
                return True
        except Exception:
            pass
        return False
    
    def set_volume(self, volume):
        """
        设置音量

        参数:
            volume: 音量值 (0.0 到 1.0)
        """
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            if self.mixer_available and not self.silent_mode and self.is_playing:
                try:
                    pygame.mixer.music.set_volume(volume)
                except Exception:
                    pass
            return True
        else:
            print("错误: 音量值必须在 0.0 到 1.0 之间")
            return False

    def get_volume(self):
        """获取当前音量"""
        return self.volume

    def is_music_playing(self):
        """检查音乐是否正在播放"""
        return self.is_playing if self.mixer_available else False

    def get_current_music(self):
        """获取当前播放的音乐类型"""
        return self.current_music

    def cleanup(self):
        """清理音乐资源"""
        try:
            self.stop_music()
            if self.mixer_available:
                pygame.mixer.quit()
        except Exception:
            pass
        print("👋 音乐资源已清理")


class GameInterfaceManager:
    """游戏界面管理器，管理不同界面的音乐播放"""
    
    def __init__(self, music_manager):
        """
        初始化游戏界面管理器
        
        参数:
            music_manager: MusicManager实例
        """
        self.music_manager = music_manager
        self.current_interface = None
        
        # 使用主界面音乐的界面
        self.main_menu_interfaces = [
            'title_screen',       # 标题界面
            'name_input',         # 角色取名界面
            'spiritual_root',     # 灵根抽取界面
            'profession_select',  # 职业选择界面
            'main_menu',          # 主菜单界面
            'character',          # 人物界面
            'inventory',          # 背包界面
            'equipment',          # 装备界面
            'craft_炼丹',         # 炼丹界面
            'craft_炼器',         # 炼器界面
            'craft_绘符',         # 绘符界面
            'settings',           # 设置界面
        ]
        
        # 战斗界面（不使用主界面音乐）
        self.battle_interfaces = [
            'battle_历练之路',    # 历练之路
            'battle_锁妖塔',      # 锁妖塔
            'battle_远古战场',    # 远古战场
            'adventure_map',      # 冒险地图
            'combat_view',        # 战斗界面
            'combat_result',      # 战斗结果
            'combat_death',       # 战斗死亡
        ]
    
    def switch_interface(self, interface_name):
        """
        切换到指定界面，自动处理音乐播放
        
        参数:
            interface_name: 界面名称
        """
        if interface_name == self.current_interface:
            return True
        
        print(f"切换到界面: {interface_name}")
        self.current_interface = interface_name
        
        if interface_name in self.main_menu_interfaces:
            if self.music_manager.get_current_music() != 'main_menu':
                return self.music_manager.play_music('main_menu', loops=-1)
            return True
            
        elif interface_name in self.battle_interfaces:
            if self.music_manager.get_current_music() != 'battle':
                return self.music_manager.play_music('battle', loops=-1)
            return True
            
        else:
            print(f"警告: 未知界面 '{interface_name}'，默认播放主界面音乐")
            if self.music_manager.get_current_music() != 'main_menu':
                return self.music_manager.play_music('main_menu', loops=-1)
            return True
    
    def get_current_interface(self):
        """获取当前界面名称"""
        return self.current_interface