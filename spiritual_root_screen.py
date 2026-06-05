"""
仙道永恒 - 灵根抽取界面
标题界面与主菜单之间的过渡界面
"""

import pygame
import random
import math
import time
from font_utils import FontManager
import gongfa_data
import realm_data

CONFIG_PATH = "config.json"


class SpiritualRootScreen:
    """灵根抽取界面"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = FontManager(CONFIG_PATH)

        import json
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.colors = self.config.get("colors", {})
        self.running = True

        # 动画状态
        self.phase = "rolling"      # rolling → reveal → result
        self.roll_start_time = 0
        self.roll_duration = 2.5    # 滚动动画时长
        self.reveal_duration = 0.8  # 揭示动画时长
        self.phase_start = 0

        # 滚动显示的临时文字
        self.rolling_texts = []
        self.rolling_index = 0
        self.rolling_switch_interval = 0.08

        # 抽取结果
        self.root_type = None
        self.elements = []
        self.bonus = 0.0

        # 粒子效果
        self.particles = []
        for _ in range(60):
            self.particles.append({
                "x": random.randint(0, screen_width),
                "y": random.randint(0, screen_height),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-2, -0.5),
                "alpha": random.randint(30, 80),
                "size": random.randint(1, 4),
                "life": random.uniform(0, 1),
            })

        # 五色光点（代表五行）
        self.element_dots = []
        element_colors_list = [
            gongfa_data.ELEMENT_COLORS[e] for e in gongfa_data.ELEMENTS
        ]
        for _ in range(30):
            self.element_dots.append({
                "x": random.randint(0, screen_width),
                "y": random.randint(0, screen_height),
                "color": random.choice(element_colors_list),
                "size": random.randint(1, 2),
                "speed": random.uniform(0.3, 1.2),
            })

        print("✅ 灵根抽取界面初始化完成")

    def start_draw(self):
        """开始抽取灵根"""
        self.root_type, self.elements, self.bonus = gongfa_data.draw_spiritual_root()

        # 滚动候选（所有灵根类型名轮转）
        self.rolling_texts = list(gongfa_data.SPIRITUAL_ROOT_CONFIG.keys()) * 6
        random.shuffle(self.rolling_texts)
        # 确保最后一个是真实结果
        self.rolling_texts.append(self.root_type)

        self.phase = "rolling"
        self.phase_start = time.time()

    def handle_events(self, events):
        """处理事件"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"

            if event.type == pygame.KEYDOWN:
                if self.phase == "result":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        return "done"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.phase == "result":
                    if event.button == 1:
                        # 按钮实际位置与 draw_result_phase 中一致
                        panel_y = 140
                        panel_h = 350
                        btn_y = panel_y + panel_h + 30
                        btn_rect = pygame.Rect(
                            self.screen_width // 2 - 90,
                            btn_y,
                            180, 50
                        )
                        if btn_rect.collidepoint(event.pos):
                            return "done"

        return None

    def update(self):
        """更新动画"""
        now = time.time()

        # 更新粒子
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.003
            if p["life"] <= 0 or p["y"] < -10:
                p["x"] = random.randint(0, self.screen_width)
                p["y"] = self.screen_height + 10
                p["vx"] = random.uniform(-1, 1)
                p["vy"] = random.uniform(-2, -0.5)
                p["life"] = 1

        # 更新五色光点
        for d in self.element_dots:
            d["y"] -= d["speed"]
            if d["y"] < -10:
                d["y"] = self.screen_height + 10
                d["x"] = random.randint(0, self.screen_width)

        # 阶段切换
        if self.phase == "rolling":
            elapsed = now - self.phase_start
            if elapsed >= self.roll_duration:
                self.phase = "reveal"
                self.phase_start = now
                self.rolling_index = len(self.rolling_texts) - 1
        elif self.phase == "reveal":
            elapsed = now - self.phase_start
            if elapsed >= self.reveal_duration:
                self.phase = "result"
                # 结果阶段的粒子爆发
                self.spawn_result_particles()

    def spawn_result_particles(self):
        """结果展示时的粒子爆发"""
        cx, cy = self.screen_width // 2, self.screen_height // 2 - 60
        element_colors_list = [
            gongfa_data.ELEMENT_COLORS[e] for e in self.elements
        ]
        for _ in range(80):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self.particles.append({
                "x": cx,
                "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "alpha": random.randint(150, 255),
                "size": random.randint(2, 6),
                "life": 1.5,
                "color": random.choice(element_colors_list),
            })

    def draw(self, screen):
        """绘制界面"""
        # 水墨背景
        bg = pygame.Surface((self.screen_width, self.screen_height))
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(245 * (1 - ratio * 0.2))
            g = int(240 * (1 - ratio * 0.15))
            b = int(228 * (1 - ratio * 0.25))
            pygame.draw.line(bg, (r, g, b), (0, y), (self.screen_width, y))
        screen.blit(bg, (0, 0))

        # 五色光点（背景）
        for d in self.element_dots:
            if d["y"] < self.screen_height * 0.7:
                alpha = int(80 * (1 - d["y"] / (self.screen_height * 0.7)))
                c = (*d["color"], alpha)
                pygame.draw.circle(screen, c[:3],
                                 (int(d["x"]), int(d["y"])), d["size"])

        if self.phase == "rolling":
            self.draw_rolling_phase(screen)
        elif self.phase == "reveal":
            self.draw_reveal_phase(screen)
        elif self.phase == "result":
            self.draw_result_phase(screen)

    def draw_rolling_phase(self, screen):
        """滚动阶段"""
        now = time.time()
        elapsed = now - self.phase_start

        # 标题
        title = "灵根觉醒"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 56)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 80))

        # 副标题
        sub = "天地灵气汇聚，灵根即将显现..."
        ss = self.font_manager.render_text(sub, "medium", (100, 90, 75), 24)
        screen.blit(ss, ((self.screen_width - ss.get_width()) // 2, 155))

        # 滚动效果
        visible_count = 5
        item_height = 55
        cy = self.screen_height // 2 - item_height * 2

        total_items = len(self.rolling_texts)
        scroll_speed = total_items / self.roll_duration

        # 减慢速度，最后定格
        if elapsed > self.roll_duration * 0.85:
            # 接近结束时减速
            remaining = self.roll_duration - elapsed
            if remaining < 0.3:
                scroll_speed *= remaining / 0.3

        offset = int(elapsed * scroll_speed) % total_items

        for i in range(visible_count + 1):
            idx = (offset + i) % total_items
            text = self.rolling_texts[idx]
            y = cy + i * item_height

            # 越靠近中间越亮、越大
            dist_from_center = abs(i - visible_count // 2)
            alpha = 255 - dist_from_center * 50
            scale = 1.0 - dist_from_center * 0.12

            if dist_from_center == 0:
                color = (40, 25, 15)
            elif dist_from_center == 1:
                color = (80, 60, 40)
            else:
                color = (140, 120, 100)

            surf = self.font_manager.render_text(text, "large", color, int(36 * scale))
            screen.blit(surf, ((self.screen_width - surf.get_width()) // 2, y))

        # 滚动指示光效
        highlight_y = cy + (visible_count // 2) * item_height + item_height // 2
        for a in range(3):
            alpha = 40 - a * 12
            r = pygame.Rect(
                self.screen_width // 2 - 200 - a * 30,
                highlight_y - 20 - a * 5,
                400 + a * 60,
                40 + a * 10
            )
            s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            s.fill((180, 160, 120, alpha))
            screen.blit(s, (r.x, r.y))

    def draw_reveal_phase(self, screen):
        """揭示阶段 - 放大显示结果"""
        now = time.time()
        elapsed = now - self.phase_start
        progress = min(elapsed / self.reveal_duration, 1.0)

        # 标题
        title = "灵根觉醒"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 56)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 80))

        # 放大动画
        scale = 0.5 + progress * 0.9  # 0.5 → 1.4
        alpha = int(progress * 255)

        # 灵根名称（放大显示）
        name_surf = self.font_manager.render_text(
            self.root_type, "title", (30, 20, 10),
            int(48 * scale)
        )
        name_surf.set_alpha(alpha)
        cx = self.screen_width // 2
        cy = self.screen_height // 2 - 40
        screen.blit(name_surf,
                   (cx - name_surf.get_width() // 2,
                    cy - name_surf.get_height() // 2))

        # 闪光效果
        if progress > 0.5:
            flash_alpha = int((progress - 0.5) * 2 * 120)
            flash = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            flash.fill((255, 240, 200, flash_alpha))
            screen.blit(flash, (0, 0))

    def draw_result_phase(self, screen):
        """结果阶段 - 完整展示灵根信息"""
        # 粒子效果
        for p in self.particles[:]:
            if p["life"] <= 0:
                continue
            alpha = int(min(p["alpha"], 255) * min(p["life"], 1))
            if "color" in p:
                color = (*p["color"][:3], alpha)
            else:
                color = (160, 140, 100, alpha)
            if len(color) == 4:
                s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (p["size"], p["size"]), p["size"])
                screen.blit(s, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))
            else:
                pygame.draw.circle(screen, color[:3],
                                 (int(p["x"]), int(p["y"])), p["size"])

        # 标题
        title = "灵根觉醒"
        ts = self.font_manager.render_text(title, "title", (50, 40, 25), 56)
        screen.blit(ts, ((self.screen_width - ts.get_width()) // 2, 50))

        # 结果面板
        panel_w, panel_h = 500, 350
        panel_x = (self.screen_width - panel_w) // 2
        panel_y = 140

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (232, 227, 214, 230),
                        (0, 0, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(panel, (80, 70, 55, 180),
                        (0, 0, panel_w, panel_h), width=2, border_radius=12)

        # 灵根类型（大字）
        rt = self.font_manager.render_text(self.root_type, "large", (30, 20, 10), 48)
        panel.blit(rt, ((panel_w - rt.get_width()) // 2, 25))

        # 分隔线
        pygame.draw.line(panel, (120, 110, 95, 100),
                        (80, 90), (panel_w - 80, 90), 1)

        # 威力加成
        bonus_text = f"功法威力加成: +{int(self.bonus * 100)}%"
        bonus_color = (200, 80, 30) if self.bonus >= 0.6 else \
                      (120, 60, 180) if self.bonus >= 0.4 else \
                      (40, 120, 40) if self.bonus >= 0.2 else (100, 90, 80)
        bt = self.font_manager.render_text(bonus_text, "medium", bonus_color, 30)
        panel.blit(bt, ((panel_w - bt.get_width()) // 2, 105))

        # 元素显示
        elem_y = 160
        elem_label = self.font_manager.render_text("灵根属性：", "medium", (80, 65, 45), 26)
        panel.blit(elem_label, (80, elem_y))

        elem_start_x = 80 + elem_label.get_width() + 15
        for i, elem in enumerate(self.elements):
            ecolor = gongfa_data.ELEMENT_COLORS[elem]
            elem_text = self.font_manager.render_text(elem, "large", ecolor, 32)
            panel.blit(elem_text, (elem_start_x + i * 55, elem_y - 3))

        # 描述
        desc_y = 215
        config = gongfa_data.SPIRITUAL_ROOT_CONFIG[self.root_type]
        desc_text = config["desc"]
        dt = self.font_manager.render_text(desc_text, "small", (100, 90, 75), 20)
        panel.blit(dt, ((panel_w - dt.get_width()) // 2, desc_y))

        # 可修炼提示
        hint_y = 260
        cultivatable = "、".join(self.elements)
        hint = f"可修炼功法属性: {cultivatable}"
        ht = self.font_manager.render_text(hint, "small", (60, 50, 35), 20)
        panel.blit(ht, ((panel_w - ht.get_width()) // 2, hint_y))

        screen.blit(panel, (panel_x, panel_y))

        # 继续按钮
        btn_w, btn_h = 180, 50
        btn_x = (self.screen_width - btn_w) // 2
        btn_y = panel_y + panel_h + 30

        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (45, 38, 28, 220),
                        (0, 0, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(btn_surf, (80, 70, 55, 180),
                        (0, 0, btn_w, btn_h), width=1, border_radius=8)

        continue_text = self.font_manager.render_text(
            "踏入仙途", "medium", (210, 200, 180), 28
        )
        btn_surf.blit(continue_text,
                     ((btn_w - continue_text.get_width()) // 2,
                      (btn_h - continue_text.get_height()) // 2))
        screen.blit(btn_surf, (btn_x, btn_y))

        # 提示
        hint2 = "点击按钮或按空格键继续"
        h2 = self.font_manager.render_text(hint2, "small", (140, 130, 110), 16)
        screen.blit(h2, ((self.screen_width - h2.get_width()) // 2, btn_y + btn_h + 10))


def run_spiritual_root_screen(screen, ling_shi_amount=0):
    """运行灵根抽取界面，返回灵根数据"""
    root_screen = SpiritualRootScreen(screen.get_width(), screen.get_height())
    root_screen.start_draw()
    clock = pygame.time.Clock()

    while root_screen.running:
        events = pygame.event.get()
        result = root_screen.handle_events(events)
        root_screen.update()
        root_screen.draw(screen)
        
        # 绘制灵石
        from ling_shi_renderer import draw_ling_shi_count
        draw_ling_shi_count(screen, ling_shi_amount)
        
        pygame.display.flip()
        clock.tick(60)

        if result == "done":
            return {
                "root_type": root_screen.root_type,
                "elements": root_screen.elements,
                "bonus": root_screen.bonus,
            }
        elif result == "quit":
            return None

    return None
