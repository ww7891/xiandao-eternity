"""
仙道永恒 - 角色取名界面
标题界面与灵根抽取之间的过渡界面
"""

import pygame
import random
import math
import time
from font_utils import FontManager

CONFIG_PATH = "config.json"


class NameInputScreen:
    """角色取名界面"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)

        import json
        import os
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_PATH)
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.colors = self.config.get("colors", {})
        self.running = True

        # 输入状态
        self.name_text = ""       # 玩家输入的名字
        self.max_length = 8       # 最大长度（中文4字以内，或英文8字符）
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 0.5

        # 动画
        self.start_time = time.time()
        self.fade_alpha = 0       # 淡入效果

        # 粒子效果（水墨风）
        self.particles = []
        for _ in range(40):
            self.particles.append({
                "x": random.randint(0, screen_width),
                "y": random.randint(0, screen_height),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.8, -0.2),
                "alpha": random.randint(15, 50),
                "size": random.randint(1, 3),
                "life": random.uniform(0, 1),
            })

        # 墨韵飘浮
        self.ink_blots = []
        for _ in range(8):
            self.ink_blots.append({
                "x": random.randint(100, screen_width - 100),
                "y": random.randint(100, screen_height - 200),
                "size": random.randint(100, 250),
                "alpha": random.randint(3, 10),
                "speed": random.uniform(0.1, 0.3),
                "phase": random.uniform(0, math.pi * 2),
            })

        # 启用文本输入以支持中文 IME
        pygame.key.start_text_input()

        print("✅ 角色取名界面初始化完成")

    def handle_events(self, events):
        """处理事件，返回 None 继续 / 'done' 确认 / 'quit' 退出"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"

            if event.type == pygame.TEXTINPUT:
                # 处理文本输入（支持中文 IME）
                if len(self.name_text) < self.max_length:
                    self.name_text += event.text

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if len(self.name_text.strip()) > 0:
                        return "done"
                elif event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_BACKSPACE:
                    self.name_text = self.name_text[:-1]
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    try:
                        clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clipboard:
                            pasted = clipboard.decode("utf-8").strip().replace("\n", "").replace("\r", "")
                            self.name_text = (self.name_text + pasted)[:self.max_length]
                    except:
                        pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 确认按钮
                    btn_rect = pygame.Rect(
                        self.screen_width // 2 - 100,
                        self.screen_height // 2 + 60,
                        200, 50
                    )
                    if btn_rect.collidepoint(event.pos) and len(self.name_text.strip()) > 0:
                        return "done"

                    # 返回按钮（小字，左上）
                    back_rect = pygame.Rect(20, 20, 100, 35)
                    if back_rect.collidepoint(event.pos):
                        return "back"

        return None

    def update(self):
        """更新动画"""
        now = time.time()

        # 淡入
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, (now - self.start_time) * 300)

        # 光标闪烁
        if now - self.cursor_timer > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now

        # 粒子
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.002
            if p["life"] <= 0 or p["y"] < -10:
                p["x"] = random.randint(0, self.screen_width)
                p["y"] = self.screen_height + 10
                p["vx"] = random.uniform(-0.5, 0.5)
                p["vy"] = random.uniform(-0.8, -0.2)
                p["life"] = 1

        # 墨韵
        for blot in self.ink_blots:
            blot["x"] += math.sin(now * blot["speed"] + blot["phase"]) * 0.3
            blot["y"] += math.cos(now * blot["speed"] * 0.7 + blot["phase"]) * 0.2

    def draw(self, screen):
        """绘制界面"""
        bg = self.colors.get("background", [20, 20, 40])
        screen.fill(bg)

        # 墨韵背景
        ink_color = self.colors.get("text_secondary", [180, 180, 200])
        for blot in self.ink_blots:
            s = pygame.Surface((blot["size"] * 2, blot["size"] * 2), pygame.SRCALPHA)
            for r in range(blot["size"], 0, -10):
                a = min(blot["alpha"], max(1, int(blot["alpha"] * (1 - r / blot["size"]))))
                pygame.draw.circle(s, (*ink_color[:3], a),
                                   (blot["size"], blot["size"]), r)
            screen.blit(s, (blot["x"] - blot["size"], blot["y"] - blot["size"]))

        # 粒子
        for p in self.particles:
            alpha = int(p["alpha"] * p["life"])
            color = (*bg[:3], alpha)
            try:
                s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (p["size"], p["size"]), p["size"])
                screen.blit(s, (int(p["x"]), int(p["y"])))
            except:
                pass

        # 遮罩淡入效果
        if self.fade_alpha < 255:
            fade_surf = pygame.Surface((self.screen_width, self.screen_height))
            fade_surf.set_alpha(255 - int(self.fade_alpha))
            fade_surf.fill(bg)
            screen.blit(fade_surf, (0, 0))

        # 标题
        title_font = self.font_manager.get_font("title")
        title_color = self.colors.get("title_gold", [255, 215, 0])
        title = title_font.render("道 号", True, title_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 140))
        screen.blit(title, title_rect)

        # 副标题
        sub_font = self.font_manager.get_font(size=22)
        sub_color = self.colors.get("text_secondary", [180, 180, 200])
        sub_text = sub_font.render("仙途漫漫，道号为先。请输入角色名讳", True, sub_color)
        sub_rect = sub_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
        screen.blit(sub_text, sub_rect)

        # 输入框背景
        input_box_w = 400
        input_box_h = 55
        input_box_rect = pygame.Rect(
            self.screen_width // 2 - input_box_w // 2,
            self.screen_height // 2 - input_box_h // 2 - 5,
            input_box_w, input_box_h
        )

        # 输入框外边框（暗金描边）
        pygame.draw.rect(screen, (80, 60, 30), input_box_rect.inflate(4, 4), border_radius=6)
        # 输入框填充
        pygame.draw.rect(screen, (30, 25, 45), input_box_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 80, 40), input_box_rect, width=2, border_radius=5)

        # 输入文字
        display_text = self.name_text if self.name_text else ""
        name_font = self.font_manager.get_font(size=36)
        text_color = self.colors.get("text_primary", [240, 240, 240])
        name_surf = name_font.render(display_text, True, text_color)
        text_x = input_box_rect.centerx - name_surf.get_width() // 2
        text_y = input_box_rect.centery - name_surf.get_height() // 2
        screen.blit(name_surf, (text_x, text_y))

        # 光标
        if self.cursor_visible:
            cursor_x = text_x + name_surf.get_width() + 2
            cursor_y = input_box_rect.centery - 14
            pygame.draw.line(screen, text_color,
                             (cursor_x, cursor_y),
                             (cursor_x, cursor_y + 28), 2)

        # 占位提示（无输入时）
        if not self.name_text:
            hint_font = self.font_manager.get_font(size=24)
            hint_text = hint_font.render("点击此处输入名号（回车确认）", True, (120, 120, 150))
            hint_rect = hint_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            screen.blit(hint_text, hint_rect)

        # 确认按钮
        btn_rect = pygame.Rect(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 60,
            200, 50
        )

        # 按钮悬停效果
        mouse_pos = pygame.mouse.get_pos()
        btn_hovered = btn_rect.collidepoint(mouse_pos) and len(self.name_text.strip()) > 0
        btn_color = (120, 90, 40) if btn_hovered else (80, 60, 30)
        btn_text_color = (255, 230, 180) if btn_hovered else (200, 170, 120)

        if len(self.name_text.strip()) == 0:
            btn_color = (50, 50, 70)
            btn_text_color = (100, 100, 130)

        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
        pygame.draw.rect(screen, (140, 110, 60), btn_rect, width=2, border_radius=6)

        btn_font = self.font_manager.get_font("button")
        btn_text = btn_font.render("踏入仙途", True, btn_text_color)
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        screen.blit(btn_text, btn_text_rect)

        # 返回提示（左下角小字）
        tip_font = self.font_manager.get_font(size=18)
        tip_color = (120, 120, 160)
        back_tip = tip_font.render("ESC / 点击左上角返回", True, tip_color)
        screen.blit(back_tip, (25, 20))


def run_name_input(screen, ling_shi_amount=0):
    """运行取名界面，返回 (name, action)
    action: "done" → 进入灵根抽取, "back" → 返回标题, "quit" → 退出
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    ni = NameInputScreen(screen_width, screen_height)
    clock = pygame.time.Clock()

    while ni.running:
        dt = clock.tick(60)

        events = pygame.event.get()
        result = ni.handle_events(events)

        if result == "done":
            return ni.name_text.strip()
        elif result == "back":
            return None  # 返回标题界面
        elif result == "quit":
            return "__quit__"

        ni.update()
        ni.draw(screen)
        pygame.display.update()

    return None