"""Kawaii baby pastel HUD, animated baby snake face, and cute automap radar."""

import math
import pygame
from typing import Dict, List, Tuple, Union
from snake.kawaii_config import (
    COLOR_LED_AMBER,
    COLOR_LED_GREEN,
    COLOR_LED_RED,
    COLOR_STATUS_BAR_BG,
    COLOR_STATUS_BAR_BORDER,
    COLOR_STATUS_BAR_INNER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    GameMode,
    MAP_HEIGHT,
    MAP_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STATUS_BAR_HEIGHT,
    VIEWPORT_HEIGHT,
    ViewMode,
)
from snake.kawaii_textures import TextureManager


class KawaiiHUD:
    def __init__(self, textures: TextureManager):
        self.textures = textures
        if not pygame.font.get_init():
            pygame.font.init()
        font_family = "DejaVu Sans, Arial, Helvetica, sans-serif"
        self.font_title_large = pygame.font.SysFont(font_family, 34, bold=True)
        self.font_logo = pygame.font.SysFont(font_family, 48, bold=True)
        self.font_led_large = pygame.font.SysFont(font_family, 26, bold=True)
        self.font_label = pygame.font.SysFont(font_family, 11, bold=True)
        self.font_sub = pygame.font.SysFont(font_family, 14, bold=True)
        self.font_prompt = pygame.font.SysFont(font_family, 15, bold=True)
        self.font_table = pygame.font.SysFont(font_family, 13, bold=True)
        self.font_table_date = pygame.font.SysFont(font_family, 11, bold=False)

        # Face animation timers
        self.look_timer: float = 0.0
        self.look_direction: str = "center"
        self.grin_timer: float = 0.0

    def trigger_grin(self):
        self.grin_timer = 1.2

    def update(self, dt: float):
        if self.grin_timer > 0:
            self.grin_timer -= dt

        self.look_timer -= dt
        if self.look_timer <= 0:
            self.look_timer = 2.0 + math.sin(pygame.time.get_ticks() / 1000.0) * 1.5
            import random
            self.look_direction = random.choice(["center", "left", "right", "center"])

    def get_current_face(self, is_dead: bool) -> pygame.Surface:
        if is_dead:
            return self.textures.kawaii_faces["dead"]
        if self.grin_timer > 0:
            return self.textures.kawaii_faces["grin"]
        return self.textures.kawaii_faces.get(self.look_direction, self.textures.kawaii_faces["center"])

    def draw_status_bar(
        self,
        surface: pygame.Surface,
        score: int,
        high_score: int,
        speed_level: int,
        current_speed: float,
        view_mode: ViewMode,
        is_dead: bool,
    ):
        bar_y = VIEWPORT_HEIGHT
        bar_rect = pygame.Rect(0, bar_y, SCREEN_WIDTH, STATUS_BAR_HEIGHT)

        # Soft baby pink base plate
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BG, bar_rect)
        pygame.draw.line(surface, COLOR_STATUS_BAR_BORDER, (0, bar_y), (SCREEN_WIDTH, bar_y), 2)
        pygame.draw.line(surface, (255, 255, 255), (0, bar_y + 2), (SCREEN_WIDTH, bar_y + 2), 1)

        # Panels setup
        # Panel 1: POMMES (Score)
        self._draw_pill_panel(surface, 25, bar_y + 12, 175, 66, "POMMES", f"{score}", COLOR_LED_RED, (255, 235, 240))

        # Panel 2: VITESSE
        speed_str = f"Nv.{speed_level}"
        self._draw_pill_panel(surface, 220, bar_y + 12, 175, 66, "VITESSE", speed_str, COLOR_LED_AMBER, (255, 245, 230))

        # Center Panel: KAWAII BABY SNAKE FACE
        face_x = (SCREEN_WIDTH - 64) // 2
        face_y = bar_y + 13
        face_border_rect = pygame.Rect(face_x - 4, face_y - 4, 72, 72)
        pygame.draw.rect(surface, (255, 255, 255), face_border_rect, border_radius=36)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, face_border_rect, 2, border_radius=36)

        current_face = self.get_current_face(is_dead)
        scaled_face = pygame.transform.scale(current_face, (64, 64))
        surface.blit(scaled_face, (face_x, face_y))

        # Panel 3: RECORD
        self._draw_pill_panel(surface, SCREEN_WIDTH - 395, bar_y + 12, 175, 66, "RECORD", f"{high_score}", COLOR_LED_GREEN, (230, 250, 242))

        # Panel 4: CAMERA / VUE
        cam_str = "1ERE" if view_mode == ViewMode.FIRST_PERSON else "3EME"
        self._draw_pill_panel(surface, SCREEN_WIDTH - 200, bar_y + 12, 175, 66, "VUE (V)", cam_str, (160, 130, 215), (242, 236, 255))

    def _draw_pill_panel(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        value: str,
        val_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int],
    ):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, bg_color, rect, border_radius=18)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=18)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, rect, width=1, border_radius=18)

        # Top Label
        lbl_surf = self.font_label.render(label, True, COLOR_TEXT_MUTED)
        surface.blit(lbl_surf, (x + 16, y + 8))

        # Large Value
        val_surf = self.font_led_large.render(value, True, val_color)
        surface.blit(val_surf, (x + 18, y + 26))

    def draw_apple_compass(
        self,
        surface: pygame.Surface,
        cam_x: float,
        cam_y: float,
        cam_angle: float,
        food_pos: Tuple[int, int],
    ):
        """Draws a cute pastel compass at the top of the screen pointing towards the apple."""
        fx = food_pos[0] + 0.5
        fy = food_pos[1] + 0.5
        dx = fx - cam_x
        dy = fy - cam_y
        dist = math.hypot(dx, dy)
        apple_angle = math.atan2(dy, dx)
        rel_angle = (apple_angle - cam_angle + math.pi) % (2 * math.pi) - math.pi

        # Compass pill container at top center
        pw, ph = 210, 40
        px = (SCREEN_WIDTH - pw) // 2
        py = 14

        # Soft shadow
        shadow_rect = pygame.Rect(px + 2, py + 3, pw, ph)
        pygame.draw.rect(surface, (230, 215, 225), shadow_rect, border_radius=ph // 2)

        # White pill card with soft pastel border
        pill_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(surface, (255, 255, 255), pill_rect, border_radius=ph // 2)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, pill_rect, width=2, border_radius=ph // 2)

        # Compass needle circle on the left
        circle_cx = px + 22
        circle_cy = py + ph // 2
        circle_r = 13

        is_facing_apple = abs(rel_angle) < 0.22
        disc_color = (225, 252, 238) if is_facing_apple else (255, 240, 245)
        pygame.draw.circle(surface, disc_color, (circle_cx, circle_cy), circle_r)
        pygame.draw.circle(surface, COLOR_STATUS_BAR_BORDER, (circle_cx, circle_cy), circle_r, width=1)

        # Arrow pointing in rel_angle direction:
        # In screen space, UP (-pi/2) corresponds to rel_angle = 0 (straight ahead)
        arrow_screen_angle = rel_angle - math.pi / 2
        arrow_len = 9.0
        tip_x = circle_cx + math.cos(arrow_screen_angle) * arrow_len
        tip_y = circle_cy + math.sin(arrow_screen_angle) * arrow_len

        base_left_x = circle_cx + math.cos(arrow_screen_angle + 2.5) * 5.5
        base_left_y = circle_cy + math.sin(arrow_screen_angle + 2.5) * 5.5
        base_right_x = circle_cx + math.cos(arrow_screen_angle - 2.5) * 5.5
        base_right_y = circle_cy + math.sin(arrow_screen_angle - 2.5) * 5.5

        arrow_color = (60, 205, 130) if is_facing_apple else (255, 110, 140)
        pygame.draw.polygon(
            surface,
            arrow_color,
            [(int(tip_x), int(tip_y)), (int(base_left_x), int(base_left_y)), (int(base_right_x), int(base_right_y))],
        )

        # Distance & direction text
        if is_facing_apple:
            text = f"Droit devant ! ({dist:.1f}m)"
            txt_color = (60, 175, 110)
        else:
            text = f"Pomme : {dist:.1f} cases"
            txt_color = COLOR_TEXT_MAIN

        txt_surf = self.font_label.render(text, True, txt_color)
        surface.blit(txt_surf, (px + 42, py + 12))

    def draw_automap_radar(
        self,
        surface: pygame.Surface,
        world_map: List[List[int]],
        snake_head: Tuple[float, float],
        snake_angle: float,
        snake_body: List[Tuple[float, float]],
        food_pos: Tuple[int, int],
        show_minimap: bool = False,
        pacifier_pos: Optional[Tuple[int, int]] = None,
    ):
        """Draws cute pastel automap radar in top-right corner if enabled, or hint badge."""
        radar_size = 140
        padding = 15
        rx = SCREEN_WIDTH - radar_size - padding
        ry = padding

        if not show_minimap:
            # Cute small pill badge hint in top-right corner
            btn_w, btn_h = 105, 32
            bx = SCREEN_WIDTH - btn_w - padding
            by = padding
            pill_rect = pygame.Rect(bx, by, btn_w, btn_h)
            pygame.draw.rect(surface, (255, 255, 255, 220), pill_rect, border_radius=16)
            pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, pill_rect, width=1, border_radius=16)
            hint_txt = self.font_label.render("[M] Carte", True, COLOR_TEXT_MUTED)
            t_rect = hint_txt.get_rect(center=pill_rect.center)
            surface.blit(hint_txt, t_rect)
            return

        # Soft pastel translucent backdrop
        radar_surf = pygame.Surface((radar_size, radar_size), pygame.SRCALPHA)
        radar_surf.fill((255, 248, 250, 205))
        pygame.draw.rect(radar_surf, (255, 205, 220, 230), (0, 0, radar_size, radar_size), 2, border_radius=12)

        scale = radar_size / max(MAP_WIDTH, MAP_HEIGHT)

        # Draw map walls (soft pastel candy pink blocks)
        for my in range(MAP_HEIGHT):
            for mx in range(MAP_WIDTH):
                if world_map[my][mx] > 0:
                    px = int(mx * scale)
                    py = int(my * scale)
                    sz = max(1, int(scale))
                    pygame.draw.rect(radar_surf, (255, 190, 205, 220), (px, py, sz, sz))

        # Draw food (cute bouncing strawberry pink dot)
        fx, fy = food_pos
        pulse = 3 + int(abs(math.sin(pygame.time.get_ticks() / 200.0)) * 2)
        pygame.draw.circle(
            radar_surf,
            (255, 100, 130, 255),
            (int((fx + 0.5) * scale), int((fy + 0.5) * scale)),
            pulse,
        )

        # Draw pacifier bonus (cute bouncing pastel cyan/mint dot)
        if pacifier_pos is not None:
            p_pulse = 3 + int(abs(math.sin(pygame.time.get_ticks() / 150.0)) * 2)
            pygame.draw.circle(
                radar_surf,
                (60, 215, 200, 255),
                (int((pacifier_pos[0] + 0.5) * scale), int((pacifier_pos[1] + 0.5) * scale)),
                p_pulse,
            )

        # Draw snake body trail (soft baby mint segments)
        for seg_x, seg_y in snake_body:
            px = int(seg_x * scale)
            py = int(seg_y * scale)
            pygame.draw.circle(radar_surf, (130, 218, 175, 230), (px, py), 3)

        # Draw snake head (cute directional triangle)
        hx = int(snake_head[0] * scale)
        hy = int(snake_head[1] * scale)
        tip_x = hx + int(math.cos(snake_angle) * 8)
        tip_y = hy + int(math.sin(snake_angle) * 8)
        left_x = hx + int(math.cos(snake_angle + 2.5) * 5)
        left_y = hy + int(math.sin(snake_angle + 2.5) * 5)
        right_x = hx + int(math.cos(snake_angle - 2.5) * 5)
        right_y = hy + int(math.sin(snake_angle - 2.5) * 5)

        pygame.draw.polygon(radar_surf, (80, 200, 140, 255), [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

        # Small toggle hint at bottom of radar
        lbl = self.font_label.render("[M] Masquer", True, (150, 140, 160))
        radar_surf.blit(lbl, (radar_size // 2 - lbl.get_width() // 2, radar_size - 18))

        surface.blit(radar_surf, (rx, ry))

    def draw_top_badges(
        self,
        surface: pygame.Surface,
        theme_name: str,
        game_mode: GameMode,
        time_remaining: float,
        is_muted: bool = False,
        show_minimap: bool = False,
    ):
        """Draws clean pastel HUD pills: Theme and Sound on top-left, Chrono on top-right next to map."""
        y = 14
        h = 36

        # --- TOP-LEFT PILLS: Theme and Sound ---
        x = 15
        # 1. Theme pill
        theme_txt = f"Monde : {theme_name}"
        lbl_theme = self.font_label.render(theme_txt, True, (120, 85, 170))
        w1 = lbl_theme.get_width() + 24
        rect1 = pygame.Rect(x, y, w1, h)
        pygame.draw.rect(surface, (255, 255, 255, 230), rect1, border_radius=18)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, rect1, width=1, border_radius=18)
        surface.blit(lbl_theme, (x + 12, y + 10))

        # 2. Audio indicator (placed immediately next to Theme on left, stays well clear of center compass)
        sound_x = x + w1 + 10
        audio_txt = "Son : Off [B]" if is_muted else "Son : On [B]"
        audio_color = (180, 140, 160) if is_muted else (70, 175, 120)
        lbl_audio = self.font_label.render(audio_txt, True, audio_color)
        w_audio = lbl_audio.get_width() + 20
        rect_audio = pygame.Rect(sound_x, y, w_audio, h)
        pygame.draw.rect(surface, (255, 255, 255, 220), rect_audio, border_radius=18)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, rect_audio, width=1, border_radius=18)
        surface.blit(lbl_audio, (sound_x + 10, y + 10))

        # --- TOP-RIGHT PILL: Chrono (placed directly next to Minimap / Map button) ---
        if game_mode == GameMode.TIME_ATTACK:
            map_left = (SCREEN_WIDTH - 140 - 15) if show_minimap else (SCREEN_WIDTH - 105 - 15)
            is_critical = time_remaining <= 5.0
            time_txt = f"Chrono : {time_remaining:.1f}s"
            txt_color = (245, 60, 90) if is_critical else (235, 120, 50)
            bg_color = (255, 230, 235) if is_critical else (255, 248, 235)
            border_color = (255, 140, 160) if is_critical else (255, 205, 150)

            lbl_time = self.font_label.render(time_txt, True, txt_color)
            w_chrono = lbl_time.get_width() + 24
            chrono_x = map_left - w_chrono - 12
            rect_chrono = pygame.Rect(chrono_x, y, w_chrono, h)
            pygame.draw.rect(surface, bg_color, rect_chrono, border_radius=18)
            pygame.draw.rect(surface, border_color, rect_chrono, width=2 if is_critical else 1, border_radius=18)
            surface.blit(lbl_time, (chrono_x + 12, y + 10))

    def draw_pacifier_banner(
        self,
        surface: pygame.Surface,
        time_remaining: float,
        total_time: float = 5.0,
    ):
        """Draws cute top notification banner with countdown bar when the pacifier bonus appears."""
        bw, bh = 510, 38
        bx = (SCREEN_WIDTH - bw) // 2
        by = 56
        rect = pygame.Rect(bx, by, bw, bh)

        # Translucent soft white-cyan pill background
        banner_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        banner_surf.fill((255, 255, 255, 235))
        surface.blit(banner_surf, (bx, by))

        # Pulsing soothing border
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 160.0)
        border_r = int(120 + pulse * 40)
        border_g = int(210 + pulse * 25)
        border_b = int(200 + pulse * 35)
        pygame.draw.rect(surface, (border_r, border_g, border_b), rect, width=2, border_radius=19)

        # Icon and text
        is_urgent = time_remaining <= 1.5
        time_col = (245, 80, 110) if is_urgent else (230, 110, 50)
        lbl_bonus = self.font_prompt.render("✦ TÉTINE APAISANTE (-3 VITESSES) ✦", True, (55, 130, 140))
        lbl_time = self.font_prompt.render(f"{time_remaining:.1f}s", True, time_col)

        surface.blit(lbl_bonus, (bx + 20, by + 9))
        surface.blit(lbl_time, (bx + bw - lbl_time.get_width() - 20, by + 9))

        # Smooth countdown progress gauge along the bottom of the pill
        ratio = max(0.0, min(1.0, time_remaining / total_time))
        gauge_w = int((bw - 36) * ratio)
        gauge_rect = pygame.Rect(bx + 18, by + bh - 5, gauge_w, 3)
        gauge_col = (255, 120, 145) if is_urgent else (90, 205, 175)
        pygame.draw.rect(surface, gauge_col, gauge_rect, border_radius=2)

    def draw_soothe_banner(
        self,
        surface: pygame.Surface,
        levels_dropped: int,
        current_level: int,
    ):
        """Draws confirmation banner after collecting the pacifier bonus."""
        bw, bh = 510, 38
        bx = (SCREEN_WIDTH - bw) // 2
        by = 56
        rect = pygame.Rect(bx, by, bw, bh)

        banner_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        banner_surf.fill((236, 252, 243, 240))
        surface.blit(banner_surf, (bx, by))
        pygame.draw.rect(surface, (100, 215, 160), rect, width=2, border_radius=19)

        if levels_dropped > 0:
            msg = f"✦ BÉBÉ APAISÉ ! Vitesse -{levels_dropped} (Niveau {current_level}) ✦"
        else:
            msg = f"✦ BÉBÉ APAISÉ ! (Vitesse de départ Niveau {current_level}) ✦"

        lbl_msg = self.font_prompt.render(msg, True, (35, 145, 85))
        surface.blit(lbl_msg, (bx + (bw - lbl_msg.get_width()) // 2, by + 9))

    def _draw_mini_table(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str,
        title_color: Tuple[int, int, int],
        entries: List[dict],
        highlight_score: int | None = None,
        is_active: bool = False,
    ):
        """Draws one compact leaderboard table for a specific game mode with proper margins."""
        table_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (255, 250, 252), table_rect, border_radius=16)
        border_color = (255, 140, 165) if is_active else COLOR_STATUS_BAR_BORDER
        border_w = 2 if is_active else 1
        pygame.draw.rect(surface, border_color, table_rect, width=border_w, border_radius=16)

        # Mode title header
        t_surf = self.font_sub.render(title, True, title_color)
        surface.blit(t_surf, (x + (w - t_surf.get_width()) // 2, y + 10))

        # Column headers
        h_y = y + 36
        h_pos = self.font_label.render("RANG", True, COLOR_TEXT_MUTED)
        h_nom = self.font_label.render("NOM", True, COLOR_TEXT_MUTED)
        h_score = self.font_label.render("SCORE", True, COLOR_TEXT_MUTED)
        h_level = self.font_label.render("NIV", True, COLOR_TEXT_MUTED)
        h_date = self.font_label.render("DATE", True, COLOR_TEXT_MUTED)

        surface.blit(h_pos, (x + 14, h_y))
        surface.blit(h_nom, (x + 58, h_y))
        surface.blit(h_score, (x + 110, h_y))
        surface.blit(h_level, (x + 185, h_y))
        surface.blit(h_date, (x + 248, h_y))

        pygame.draw.line(surface, COLOR_STATUS_BAR_BORDER, (x + 10, h_y + 18), (x + w - 10, h_y + 18), 1)

        # Rows
        if not entries:
            empty_msg = self.font_label.render("Aucun score enregistré", True, COLOR_TEXT_MUTED)
            surface.blit(empty_msg, (x + (w - empty_msg.get_width()) // 2, y + 110))
        else:
            highlighted = False
            for idx, entry in enumerate(entries[:5]):
                row_y = h_y + 24 + idx * 30
                e_player = (str(entry.get("player") or "---")).strip().upper()[:3]
                e_score = entry.get("score", 0)
                e_level = entry.get("level", 1)
                e_date = entry.get("date", "")

                # Highlight matching score row
                if not highlighted and highlight_score is not None and e_score == highlight_score:
                    highlighted = True
                    hl_rect = pygame.Rect(x + 6, row_y - 2, w - 12, 26)
                    pygame.draw.rect(surface, (255, 235, 242), hl_rect, border_radius=8)
                    pygame.draw.rect(surface, (255, 195, 212), hl_rect, width=1, border_radius=8)

                rank_txt = self.font_table.render(f"#{idx + 1}", True, (245, 110, 140) if idx == 0 else COLOR_TEXT_MAIN)
                nom_txt = self.font_table.render(f"{e_player}", True, (135, 95, 185))
                score_txt = self.font_table.render(f"{e_score} pts", True, COLOR_LED_RED)
                lvl_txt = self.font_table.render(f"Nv.{e_level}", True, COLOR_LED_AMBER)
                date_txt = self.font_table_date.render(f"{e_date}", True, COLOR_TEXT_MUTED)

                surface.blit(rank_txt, (x + 14, row_y + 2))
                surface.blit(nom_txt, (x + 58, row_y + 2))
                surface.blit(score_txt, (x + 110, row_y + 2))
                surface.blit(lvl_txt, (x + 185, row_y + 2))
                surface.blit(date_txt, (x + 248, row_y + 3))

    def draw_start_screen(
        self,
        surface: pygame.Surface,
        leaderboard: Union[Dict[str, List[dict]], List[dict]],
        selected_mode: GameMode = GameMode.CLASSIC,
        selected_index: int = 0,
        menu_view: str = "main",
    ):
        """Displays redesigned Kawaii title screen with 'Kawaii' logo + snake sprite, 3-item menu, or High Scores."""
        veil = pygame.Surface((SCREEN_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 242, 247, 230))
        surface.blit(veil, (0, 0))

        cw, ch = 780, 470
        cx = (SCREEN_WIDTH - cw) // 2
        cy = (VIEWPORT_HEIGHT - ch) // 2
        card_rect = pygame.Rect(cx, cy, cw, ch)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=24)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, card_rect, width=2, border_radius=24)

        if menu_view == "high_scores":
            # --- HIGH SCORES VIEW: Side-by-side Tables ---
            title = self.font_title_large.render("✧ TABLEAUX DES MEILLEURS SCORES ✧", True, (245, 110, 140))
            tx = (SCREEN_WIDTH - title.get_width()) // 2
            surface.blit(title, (tx, cy + 16))

            sub = self.font_sub.render("Panthéon des Joueurs & Records Arcade", True, (130, 95, 175))
            sx = (SCREEN_WIDTH - sub.get_width()) // 2
            surface.blit(sub, (sx, cy + 54))

            if isinstance(leaderboard, dict):
                classic_lb = leaderboard.get("Classique", [])
                chrono_lb = leaderboard.get("Chrono", [])
            else:
                classic_lb = [e for e in leaderboard if e.get("mode") == "Classique"]
                chrono_lb = [e for e in leaderboard if e.get("mode") == "Chrono"]

            tw, th = 355, 230
            t1_x = cx + 22
            t1_y = cy + 86
            self._draw_mini_table(
                surface=surface,
                x=t1_x,
                y=t1_y,
                w=tw,
                h=th,
                title="✦ MODE CLASSIQUE ✦",
                title_color=(235, 100, 135),
                entries=classic_lb,
                is_active=(selected_mode == GameMode.CLASSIC),
            )

            t2_x = cx + cw - tw - 22
            t2_y = cy + 86
            self._draw_mini_table(
                surface=surface,
                x=t2_x,
                y=t2_y,
                w=tw,
                h=th,
                title="✦ CONTRE-LA-MONTRE ✦",
                title_color=(230, 115, 50),
                entries=chrono_lb,
                is_active=(selected_mode == GameMode.TIME_ATTACK),
            )

            # Return button
            btn_w, btn_h = 520, 46
            bx = cx + (cw - btn_w) // 2
            by = cy + ch - btn_h - 20
            btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
            pygame.draw.rect(surface, (255, 140, 165), btn_rect, border_radius=23)
            ret_txt = self.font_prompt.render("✦ [ Échap ] ou [ Entrée ] Retour au Menu Principal ✦", True, (255, 255, 255))
            surface.blit(ret_txt, (bx + (btn_w - ret_txt.get_width()) // 2, by + 13))

        else:
            # --- MAIN TITLE SCREEN: Logo "Kawaii" + Snake Sprite & 3-item Menu ---
            txt_kawaii = self.font_logo.render("Kawaii", True, (248, 100, 140))
            shadow_kawaii = self.font_logo.render("Kawaii", True, (255, 205, 220))

            # Mascot snake composition
            snake_sz = 52
            snake_mascot = pygame.transform.scale(self.textures.sprite_snake_head, (snake_sz, snake_sz))
            segment_mascot = pygame.transform.scale(self.textures.sprite_segment, (30, 30))
            apple_mascot = pygame.transform.scale(self.textures.sprite_apple, (24, 24))

            mascot_w = 76
            logo_gap = 16
            total_logo_w = txt_kawaii.get_width() + logo_gap + mascot_w
            start_logo_x = cx + (cw - total_logo_w) // 2
            logo_y = cy + 18

            bob_y = int(math.sin(pygame.time.get_ticks() / 240.0) * 3.5)

            # Draw Logo text
            surface.blit(shadow_kawaii, (start_logo_x + 2, logo_y + 2))
            surface.blit(txt_kawaii, (start_logo_x, logo_y))

            # Draw Snake mascot next to "Kawaii"
            mascot_x = start_logo_x + txt_kawaii.get_width() + logo_gap
            surface.blit(segment_mascot, (mascot_x + 36, logo_y + 14 + bob_y))
            surface.blit(apple_mascot, (mascot_x + 48, logo_y + 2 + bob_y))
            surface.blit(snake_mascot, (mascot_x, logo_y + 2 + bob_y))

            # Subtitle
            sub = self.font_sub.render("✧ BÉBÉ SNAKE 3D ✧", True, (135, 95, 180))
            surface.blit(sub, (cx + (cw - sub.get_width()) // 2, cy + 76))

            # Menu Options: 1. Classique, 2. Contre la montre, 3. High score
            menu_items = [
                {
                    "title": "Mode Classique",
                    "sub": "Vitesse progressive tous les 5 points  •  3 Mondes cycliques",
                    "key": "[ C ]",
                },
                {
                    "title": "Contre-la-montre",
                    "sub": "10s chrono initiales  •  +5s par pomme ramassée",
                    "key": "[ T ]",
                },
                {
                    "title": "Meilleurs Scores",
                    "sub": "Consulter les tableaux des records & initiales (High Score)",
                    "key": "[ H ]",
                },
            ]

            mw, mh = 540, 64
            mx = cx + (cw - mw) // 2
            start_my = cy + 116
            gap = 14

            for idx, item in enumerate(menu_items):
                iy = start_my + idx * (mh + gap)
                item_rect = pygame.Rect(mx, iy, mw, mh)
                is_sel = (idx == selected_index)

                if is_sel:
                    pygame.draw.rect(surface, (255, 138, 165), item_rect, border_radius=20)
                    pygame.draw.rect(surface, (245, 95, 125), item_rect, width=2, border_radius=20)

                    pulse = int(math.sin(pygame.time.get_ticks() / 150.0) * 3)
                    cursor_txt = self.font_prompt.render("▶", True, (255, 255, 255))
                    surface.blit(cursor_txt, (mx + 18 + pulse, iy + 14))

                    t_surf = self.font_prompt.render(item["title"], True, (255, 255, 255))
                    s_surf = self.font_label.render(item["sub"], True, (255, 238, 245))

                    k_surf = self.font_label.render(item["key"], True, (250, 100, 135))
                    k_rect = pygame.Rect(mx + mw - 58, iy + 19, 44, 26)
                    pygame.draw.rect(surface, (255, 255, 255), k_rect, border_radius=13)
                    surface.blit(k_surf, (k_rect.x + (k_rect.width - k_surf.get_width()) // 2, k_rect.y + 6))
                else:
                    pygame.draw.rect(surface, (255, 250, 252), item_rect, border_radius=20)
                    pygame.draw.rect(surface, (245, 215, 225), item_rect, width=1, border_radius=20)

                    dot_txt = self.font_prompt.render("✦", True, (220, 180, 205))
                    surface.blit(dot_txt, (mx + 18, iy + 14))

                    t_surf = self.font_prompt.render(item["title"], True, (85, 75, 95))
                    s_surf = self.font_label.render(item["sub"], True, (155, 145, 170))

                    k_surf = self.font_label.render(item["key"], True, (155, 145, 170))
                    k_rect = pygame.Rect(mx + mw - 58, iy + 19, 44, 26)
                    pygame.draw.rect(surface, (252, 242, 247), k_rect, border_radius=13)
                    surface.blit(k_surf, (k_rect.x + (k_rect.width - k_surf.get_width()) // 2, k_rect.y + 6))

                surface.blit(t_surf, (mx + 46, iy + 12))
                surface.blit(s_surf, (mx + 46, iy + 36))

            # Footer
            footer_w, footer_h = 580, 36
            fx = cx + (cw - footer_w) // 2
            fy = cy + ch - footer_h - 22
            footer_rect = pygame.Rect(fx, fy, footer_w, footer_h)
            pygame.draw.rect(surface, (255, 242, 247), footer_rect, border_radius=18)
            pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, footer_rect, width=1, border_radius=18)

            hint_txt = self.font_label.render("Utilisez [ ↑ / ↓ ] pour naviguer  •  [ Entrée ] pour valider  •  [ B ] Son", True, (140, 110, 165))
            surface.blit(hint_txt, (fx + (footer_w - hint_txt.get_width()) // 2, fy + 10))

    def draw_death_screen(
        self,
        surface: pygame.Surface,
        score: int,
        high_score: int,
        game_mode: GameMode,
        death_reason: str,
        leaderboard: Union[Dict[str, List[dict]], List[dict]],
        player_initials: str = "",
        initials_submitted: bool = False,
    ):
        """Displays cozy death screen with side-by-side Leaderboards (Classique & Chrono) and initials input."""
        veil = pygame.Surface((SCREEN_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 238, 245, 220))
        surface.blit(veil, (0, 0))

        # Cute Card in center
        cw, ch = 780, 470
        cx = (SCREEN_WIDTH - cw) // 2
        cy = (VIEWPORT_HEIGHT - ch) // 2
        card_rect = pygame.Rect(cx, cy, cw, ch)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=24)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, card_rect, width=2, border_radius=24)

        # Title
        if death_reason == "Temps écoulé !":
            title_text = "Temps écoulé ! Bébé s'endort"
        else:
            title_text = "Oups ! Bébé s'est cogné"
        title = self.font_title_large.render(title_text, True, (245, 110, 140))
        tx = (SCREEN_WIDTH - title.get_width()) // 2
        surface.blit(title, (tx, cy + 16))

        # Subtitle
        sub_text = f"Pommes : {score}   •   Mode : {game_mode.value}   •   Record : {high_score}"
        sub_surf = self.font_sub.render(sub_text, True, COLOR_TEXT_MAIN)
        sx = (SCREEN_WIDTH - sub_surf.get_width()) // 2
        surface.blit(sub_surf, (sx, cy + 54))

        # Split leaderboards
        if isinstance(leaderboard, dict):
            classic_lb = leaderboard.get("Classique", [])
            chrono_lb = leaderboard.get("Chrono", [])
        else:
            classic_lb = [e for e in leaderboard if e.get("mode") == "Classique"]
            chrono_lb = [e for e in leaderboard if e.get("mode") == "Chrono"]

        tw, th = 355, 230
        t1_x = cx + 22
        t1_y = cy + 86
        self._draw_mini_table(
            surface=surface,
            x=t1_x,
            y=t1_y,
            w=tw,
            h=th,
            title="✦ MODE CLASSIQUE ✦",
            title_color=(235, 100, 135),
            entries=classic_lb,
            highlight_score=(score if game_mode == GameMode.CLASSIC else None),
            is_active=(game_mode == GameMode.CLASSIC),
        )

        t2_x = cx + cw - tw - 22
        t2_y = cy + 86
        self._draw_mini_table(
            surface=surface,
            x=t2_x,
            y=t2_y,
            w=tw,
            h=th,
            title="✦ CONTRE-LA-MONTRE ✦",
            title_color=(230, 115, 50),
            entries=chrono_lb,
            highlight_score=(score if game_mode == GameMode.TIME_ATTACK else None),
            is_active=(game_mode == GameMode.TIME_ATTACK),
        )

        # Initials entry / Confirmation area (between tables and bottom prompt bar)
        btn_w, btn_h = 736, 44
        bx = cx + (cw - btn_w) // 2
        by = cy + ch - btn_h - 14
        btn_rect = pygame.Rect(bx, by, btn_w, btn_h)

        if not initials_submitted:
            # Header prompt for 3 initials
            hint_surf = self.font_label.render("✦ Tapez 3 lettres pour inscrire votre nom au classement ✦", True, (135, 95, 185))
            surface.blit(hint_surf, (cx + (cw - hint_surf.get_width()) // 2, cy + 324))

            # 3 letter boxes
            box_w, box_h = 42, 38
            box_gap = 10
            total_boxes_w = 3 * box_w + 2 * box_gap
            start_bx = cx + (cw - total_boxes_w) // 2
            box_y = cy + 346

            for i in range(3):
                bx_i = start_bx + i * (box_w + box_gap)
                b_rect = pygame.Rect(bx_i, box_y, box_w, box_h)

                if i < len(player_initials):
                    # Letter entered
                    pygame.draw.rect(surface, (255, 238, 245), b_rect, border_radius=10)
                    pygame.draw.rect(surface, (255, 130, 165), b_rect, width=2, border_radius=10)
                    char_surf = self.font_led_large.render(player_initials[i], True, (245, 90, 130))
                    surface.blit(char_surf, (bx_i + (box_w - char_surf.get_width()) // 2, box_y + (box_h - char_surf.get_height()) // 2))
                elif i == len(player_initials):
                    # Active cursor box
                    blink = (pygame.time.get_ticks() // 350) % 2 == 0
                    border_col = (255, 120, 150) if blink else (230, 180, 205)
                    bg_col = (255, 255, 255) if blink else (255, 248, 250)
                    pygame.draw.rect(surface, bg_col, b_rect, border_radius=10)
                    pygame.draw.rect(surface, border_col, b_rect, width=2, border_radius=10)
                    if blink:
                        cursor_surf = self.font_led_large.render("_", True, (245, 100, 135))
                        surface.blit(cursor_surf, (bx_i + (box_w - cursor_surf.get_width()) // 2, box_y + (box_h - cursor_surf.get_height()) // 2 - 4))
                else:
                    # Empty awaiting box
                    pygame.draw.rect(surface, (250, 248, 252), b_rect, border_radius=10)
                    pygame.draw.rect(surface, (225, 215, 230), b_rect, width=1, border_radius=10)
                    dot_surf = self.font_led_large.render("·", True, (210, 200, 220))
                    surface.blit(dot_surf, (bx_i + (box_w - dot_surf.get_width()) // 2, box_y + (box_h - dot_surf.get_height()) // 2 - 4))

            # Bottom action bar for entry mode
            pygame.draw.rect(surface, (255, 130, 160), btn_rect, border_radius=22)
            prompt_text = "[ Entrée ] Valider vos 3 lettres   •   [ Effacer ] Corriger   •   [ Echap ] Passer"
            p_surf = self.font_prompt.render(prompt_text, True, (255, 255, 255))
            surface.blit(p_surf, (cx + (cw - p_surf.get_width()) // 2, by + 12))
        else:
            # Confirmed pill banner
            pill_w, pill_h = 440, 40
            pill_x = cx + (cw - pill_w) // 2
            pill_y = cy + 342
            pill_rect = pygame.Rect(pill_x, pill_y, pill_w, pill_h)
            pygame.draw.rect(surface, (236, 252, 242), pill_rect, border_radius=20)
            pygame.draw.rect(surface, (110, 210, 150), pill_rect, width=2, border_radius=20)

            display_name = player_initials or "AAA"
            c_txt = f"✦ Score enregistré pour [ {display_name} ] ! ✦"
            c_surf = self.font_sub.render(c_txt, True, (40, 140, 80))
            surface.blit(c_surf, (pill_x + (pill_w - c_surf.get_width()) // 2, pill_y + 11))

            # Bottom action bar for replay mode
            pygame.draw.rect(surface, (255, 140, 165), btn_rect, border_radius=22)
            prompt_text = "[ R ] Rejouer   •   [ C ] Mode Classique   •   [ T ] Contre-la-montre"
            p_surf = self.font_prompt.render(prompt_text, True, (255, 255, 255))
            surface.blit(p_surf, (cx + (cw - p_surf.get_width()) // 2, by + 12))

    def draw_pause_screen(self, surface: pygame.Surface, selected_index: int = 0):
        """Displays cozy Pause modal offering to Continue (resume) or Quit (to Title Screen)."""
        veil = pygame.Surface((SCREEN_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        veil.fill((250, 244, 252, 195))
        surface.blit(veil, (0, 0))

        cw, ch = 500, 270
        cx = (SCREEN_WIDTH - cw) // 2
        cy = (VIEWPORT_HEIGHT - ch) // 2
        card_rect = pygame.Rect(cx, cy, cw, ch)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=24)
        pygame.draw.rect(surface, COLOR_STATUS_BAR_BORDER, card_rect, width=2, border_radius=24)

        # Title
        title = self.font_title_large.render("✧ PAUSE DODO ✧", True, (160, 130, 215))
        tx = (SCREEN_WIDTH - title.get_width()) // 2
        surface.blit(title, (tx, cy + 22))

        # Subtitle
        sub = self.font_sub.render("Partie suspendue • Bébé fait un petit somme", True, (150, 140, 165))
        sx = (SCREEN_WIDTH - sub.get_width()) // 2
        surface.blit(sub, (sx, cy + 62))

        # Two interactive buttons: 0 = Continuer, 1 = Quitter vers le Title Screen
        pause_items = [
            {"title": "Continuer la partie", "key": "[ Échap ]"},
            {"title": "Quitter vers l'Écran Titre", "key": "[ Q ]"},
        ]

        bw, bh = 420, 48
        bx = cx + (cw - bw) // 2
        start_by = cy + 100
        gap = 14

        for idx, item in enumerate(pause_items):
            by = start_by + idx * (bh + gap)
            b_rect = pygame.Rect(bx, by, bw, bh)
            is_sel = (idx == selected_index)

            if is_sel:
                pygame.draw.rect(surface, (255, 138, 165), b_rect, border_radius=18)
                pygame.draw.rect(surface, (245, 95, 125), b_rect, width=2, border_radius=18)

                pulse = int(math.sin(pygame.time.get_ticks() / 150.0) * 3)
                cursor = self.font_prompt.render("▶", True, (255, 255, 255))
                surface.blit(cursor, (bx + 18 + pulse, by + 13))

                t_surf = self.font_prompt.render(item["title"], True, (255, 255, 255))
                k_surf = self.font_label.render(item["key"], True, (250, 100, 135))

                k_rect = pygame.Rect(bx + bw - 82, by + 12, 68, 24)
                pygame.draw.rect(surface, (255, 255, 255), k_rect, border_radius=12)
                surface.blit(k_surf, (k_rect.x + (k_rect.width - k_surf.get_width()) // 2, k_rect.y + 5))
            else:
                pygame.draw.rect(surface, (255, 250, 252), b_rect, border_radius=18)
                pygame.draw.rect(surface, (245, 215, 225), b_rect, width=1, border_radius=18)

                dot = self.font_prompt.render("✦", True, (220, 180, 205))
                surface.blit(dot, (bx + 18, by + 13))

                t_surf = self.font_prompt.render(item["title"], True, (85, 75, 95))
                k_surf = self.font_label.render(item["key"], True, (155, 145, 170))

                k_rect = pygame.Rect(bx + bw - 82, by + 12, 68, 24)
                pygame.draw.rect(surface, (252, 242, 247), k_rect, border_radius=12)
                surface.blit(k_surf, (k_rect.x + (k_rect.width - k_surf.get_width()) // 2, k_rect.y + 5))

            surface.blit(t_surf, (bx + 46, by + 13))

        # Helper hint centered inside bottom of card
        hint = self.font_label.render("[ ↑ / ↓ ] Choisir   •   [ Entrée ] Valider   •   [ Échap ] Reprendre", True, (150, 140, 165))
        surface.blit(hint, (cx + (cw - hint.get_width()) // 2, cy + ch - 26))


# Backwards compatibility alias
DoomHUD = KawaiiHUD

