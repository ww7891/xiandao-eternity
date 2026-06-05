"""
仙道永恒 - 开发者调试面板
F2 键切换开关
"""

import pygame
import os
import realm_data
from font_utils import FontManager

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


class DebugPanel:
    def __init__(self, screen_width, screen_height, ling_shi_wallet=None):
        self.visible = False
        self.screen_w = screen_width
        self.screen_h = screen_height

        self.panel_w = 450
        self.panel_h = 420
        self.panel_x = (screen_width - self.panel_w) // 2
        self.panel_y = (screen_height - self.panel_h) // 2

        self.font_manager = FontManager(CONFIG_PATH)
        self.ling_shi_wallet = ling_shi_wallet

        self.toast = ""
        self.toast_timer = 0

        self.selected = 0  # 0=境界, 1=阶数, 2=修为, 3=灵石
        self.edit_value = ""
        self.editing = False

        self._build_options()

    def set_ling_shi_wallet(self, wallet):
        self.ling_shi_wallet = wallet

    def _build_options(self):
        player = realm_data.player
        self.realm_idx = player["realm_index"]
        self.stage = player["current_stage"]
        self.cultivation = player["cultivation"]

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self._build_options()
            self.editing = False
            self.edit_value = ""

    def _show_toast(self, msg):
        self.toast = msg
        self.toast_timer = 120

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.editing:
                    self.editing = False
                    self.edit_value = ""
                else:
                    self.visible = False
                return True

            if self.editing:
                if event.key == pygame.K_RETURN:
                    self._commit_edit()
                    self.editing = False
                    self.edit_value = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.edit_value = self.edit_value[:-1]
                else:
                    if event.unicode.isdigit() or (self.selected == 3 and event.unicode == '-'):
                        self.edit_value += event.unicode
                return True

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % 4
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % 4
            elif event.key == pygame.K_RETURN:
                self.editing = True
                self.edit_value = ""
            elif event.key == pygame.K_s:
                self._apply_and_save()
                self._show_toast("已保存到存档")

    def _commit_edit(self):
        if not self.edit_value:
            return
        try:
            val = int(self.edit_value)
        except ValueError:
            return

        player = realm_data.player
        if self.selected == 0:
            if 0 <= val <= 8:
                player["realm_index"] = val
                player["cultivation"] = 0
                player["current_stage"] = 1
                self._show_toast(f"境界 → {realm_data.get_realm_name(val)}")
        elif self.selected == 1:
            if 1 <= val <= 10:
                player["current_stage"] = val
                player["cultivation"] = self._get_stage_start_cult(player["realm_index"], val)
                self._show_toast(f"阶数 → 第{val}阶")
        elif self.selected == 2:
            if val >= 0:
                player["cultivation"] = val
                self._show_toast(f"修为 → {val}")
        elif self.selected == 3:
            if self.ling_shi_wallet:
                if val >= 0:
                    # 直接用 set_amount 方式
                    current = self.ling_shi_wallet.amount
                    diff = val - current
                    if diff > 0:
                        self.ling_shi_wallet.add(diff)
                    elif diff < 0:
                        # 支持减少：通过 hack 直接设置
                        self.ling_shi_wallet._amount = val
                        self.ling_shi_wallet._save()
                    self._show_toast(f"灵石 → {val}")
                elif val < 0:
                    self.ling_shi_wallet._amount = 0
                    self.ling_shi_wallet._save()
                    self._show_toast("灵石 → 0")

        self._build_options()

    def _get_stage_start_cult(self, realm_idx, stage):
        base = 100 * (10 ** realm_idx)
        total = 0
        for s in range(1, stage):
            total += base * s
        return total

    def _apply_and_save(self):
        from save_manager import SaveManager
        sm = SaveManager()
        game_data = {
            "player": realm_data.player,
            "progress": {"current_screen": "main_menu"},
            "settings": {},
            "meta": {}
        }
        if sm.save_game(1, game_data):
            self._show_toast("已保存到存档位1")
        else:
            self._show_toast("保存失败")

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 25, 18, 245), (0, 0, self.panel_w, self.panel_h), border_radius=12)
        pygame.draw.rect(panel, (180, 160, 100, 200), (0, 0, self.panel_w, self.panel_h), width=2, border_radius=12)

        y = 15

        title = self.font_manager.render_text("开发者调试面板", "medium", (220, 200, 160), 22)
        panel.blit(title, ((self.panel_w - title.get_width()) // 2, y))
        y += 35

        pygame.draw.line(panel, (120, 110, 80, 150), (20, y), (self.panel_w - 20, y), 1)
        y += 15

        player = realm_data.player
        ling_shi = self.ling_shi_wallet.amount if self.ling_shi_wallet else 0
        options = [
            f"境界:  {realm_data.get_realm_name(player['realm_index'])}（{player['realm_index']}）",
            f"阶数:  第{player['current_stage']}阶 / 10",
            f"修为:  {player['cultivation']}",
            f"灵石:  {ling_shi}",
        ]

        for i, opt in enumerate(options):
            is_sel = self.selected == i
            color = (255, 220, 80) if is_sel else (180, 170, 150)
            bg_color = (60, 50, 30, 180) if is_sel else (0, 0, 0, 0)

            if bg_color[3] > 0:
                pygame.draw.rect(panel, bg_color, (18, y - 2, self.panel_w - 36, 28), border_radius=4)

            txt = self.font_manager.render_text(opt, "small", color, 17)
            panel.blit(txt, (28, y))
            y += 35

        if self.editing:
            labels = ['境界(0-8)', '阶数(1-10)', '修为', '灵石']
            edit_label = f"输入 {labels[self.selected]}: {self.edit_value}_"
            el = self.font_manager.render_text(edit_label, "medium", (0, 255, 180), 18)
            panel.blit(el, (28, y + 5))

        y += 45
        pygame.draw.line(panel, (120, 110, 80, 150), (20, y), (self.panel_w - 20, y), 1)
        y += 15

        hints = [
            "↑↓ 选择  |  Enter 修改  |  S 保存",
            "Esc 退出编辑 / 关闭面板",
        ]
        for hint in hints:
            hl = self.font_manager.render_text(hint, "small", (140, 130, 110), 14)
            panel.blit(hl, (28, y))
            y += 22

        if self.toast_timer > 0:
            self.toast_timer -= 1
            ts = self.font_manager.render_text(self.toast, "medium", (0, 255, 180), 18)
            panel.blit(ts, ((self.panel_w - ts.get_width()) // 2, self.panel_h - 40))

        screen.blit(panel, (self.panel_x, self.panel_y))