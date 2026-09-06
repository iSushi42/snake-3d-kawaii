"""3D Kawaii Baby Snake game engine with grid-corridor alignment and predictable collisions."""

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple
from snake.kawaii_config import (
    DOOM_BASE_SPEED,
    DOOM_MAX_SPEED,
    DOOM_SPEED_INCREMENT,
    KAWAII_BASE_SPEED,
    KAWAII_MAX_SPEED,
    KAWAII_SPEED_INCREMENT,
    GameMode,
    MAP_HEIGHT,
    MAP_WIDTH,
    PACIFIER_LIFETIME,
    PACIFIER_MAX_LEVEL_DROP,
    PACIFIER_SPAWN_MAX_INTERVAL,
    PACIFIER_SPAWN_MIN_INTERVAL,
    THEMES,
    TIME_ATTACK_BONUS_PER_APPLE,
    TIME_ATTACK_MAX_SECONDS,
    TIME_ATTACK_START_SECONDS,
    ViewMode,
)

KAWAII_HIGHSCORE_FILE = Path.home() / ".snake2_kawaii_highscore.json"
DOOM_HIGHSCORE_FILE = KAWAII_HIGHSCORE_FILE
LEADERBOARD_FILE = Path.home() / ".snake2_leaderboard.json"


def build_default_map() -> List[List[int]]:
    """Creates an open 16x16 arena with marshmallow candy perimeter walls."""
    grid = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # Perimeter walls (1 = candy)
    for x in range(MAP_WIDTH):
        grid[0][x] = 1
        grid[MAP_HEIGHT - 1][x] = 1
    for y in range(MAP_HEIGHT):
        grid[y][0] = 1
        grid[y][MAP_WIDTH - 1] = 1

    return grid


class KawaiiSnakeGame:
    def __init__(self):
        self.world_map = build_default_map()
        self.view_mode = ViewMode.FIRST_PERSON

        # Snake state: ALWAYS centered on corridor line (col + 0.5, row + 0.5)
        self.head_x: float = 8.5
        self.head_y: float = 8.5
        self.target_angle: float = 0.0      # Target orientation (0: East, -pi/2: North, pi: West, pi/2: South)
        self.current_angle: float = 0.0     # Smoothly interpolated camera angle

        # Path history for smooth trailing body
        self.path_history: List[Tuple[float, float]] = []
        self.segment_count: int = 3
        self.segment_spacing: float = 0.65  # Distance between segments

        # Pre-fill initial path
        for i in range(150):
            dist = i * 0.08
            self.path_history.append((self.head_x - dist, self.head_y))

        # Food position: cell (12, 8) -> center is (12.5, 8.5)
        self.food_x: int = 12
        self.food_y: int = 8

        # Game mode & Time Attack
        self.game_mode: GameMode = GameMode.CLASSIC
        self.time_remaining: float = TIME_ATTACK_START_SECONDS
        self.death_reason: str = ""

        # Game progression & Leaderboard
        self.score: int = 0
        self.high_score: int = self._load_high_score()
        self.leaderboard: List[dict] = self._load_leaderboard()
        self.player_initials: str = ""
        self.initials_submitted: bool = False
        self.last_player_name: str = "AAA"
        self.is_dead: bool = False
        self.is_paused: bool = False

        # Pacifier (Tétine) Calming Bonus state
        self.speed_reduction: int = 0
        self.pacifier_active: bool = False
        self.pacifier_timer: float = 0.0
        self.pacifier_spawn_timer: float = random.uniform(PACIFIER_SPAWN_MIN_INTERVAL, PACIFIER_SPAWN_MAX_INTERVAL)
        self.pacifier_x: int = 0
        self.pacifier_y: int = 0
        self.pacifier_just_spawned: bool = False
        self.pacifier_eaten: bool = False
        self.soothe_message_timer: float = 0.0
        self.soothe_levels_dropped: int = 0

        # Visuals & juice
        self.bob_time: float = 0.0
        self.flash_timer: float = 0.0
        self.flash_color: Tuple[int, int, int, int] | None = None
        self.is_boosting: bool = False
        self.show_minimap: bool = False  # Disabled by default, press M to toggle

        self._respawn_food()

    @property
    def theme_index(self) -> int:
        return (self.speed_level - 1) % len(THEMES)

    @property
    def speed_level(self) -> int:
        raw = 1 + (self.score // 5) - self.speed_reduction
        return max(1, raw)

    @property
    def current_speed(self) -> float:
        base = DOOM_BASE_SPEED + (self.speed_level - 1) * DOOM_SPEED_INCREMENT
        if self.is_boosting:
            base *= 1.45
        return min(base, DOOM_MAX_SPEED)

    def toggle_view_mode(self):
        if self.view_mode == ViewMode.FIRST_PERSON:
            self.view_mode = ViewMode.CHASE_CAM
        else:
            self.view_mode = ViewMode.FIRST_PERSON

    def toggle_minimap(self):
        self.show_minimap = not self.show_minimap

    def turn_left(self):
        if not self.is_dead and not self.is_paused:
            self.target_angle -= math.pi / 2
            self._snap_to_grid_corridor()

    def turn_right(self):
        if not self.is_dead and not self.is_paused:
            self.target_angle += math.pi / 2
            self._snap_to_grid_corridor()

    def set_absolute_direction(self, angle_target: float):
        """Sets direction if it's not a direct 180° reverse of current facing."""
        diff = (angle_target - self.target_angle) % (2 * math.pi)
        if not math.isclose(diff, math.pi, abs_tol=0.1):
            self.target_angle = angle_target
            self._snap_to_grid_corridor()

    def _snap_to_grid_corridor(self):
        """Snaps the perpendicular coordinate to the exact corridor center line.
        Guarantees the player is never 'between two cells'.
        """
        norm_angle = self.target_angle % (2 * math.pi)
        # Check if facing horizontal (East ~ 0.0 or West ~ pi)
        is_horizontal = (abs(norm_angle - 0.0) < 0.2) or (abs(norm_angle - math.pi) < 0.2) or (abs(norm_angle - 2 * math.pi) < 0.2)

        if is_horizontal:
            # Moving along X: lock Y to center of row (row + 0.5)
            self.head_y = math.floor(self.head_y) + 0.5
        else:
            # Moving along Y: lock X to center of column (col + 0.5)
            self.head_x = math.floor(self.head_x) + 0.5

    def toggle_pause(self):
        if not self.is_dead:
            self.is_paused = not self.is_paused

    def add_initial_char(self, char: str):
        """Appends one uppercase letter if fewer than 3 characters."""
        if not self.initials_submitted and len(self.player_initials) < 3 and char.isalpha():
            self.player_initials += char.upper()

    def remove_initial_char(self):
        """Deletes the last typed initial character."""
        if not self.initials_submitted and len(self.player_initials) > 0:
            self.player_initials = self.player_initials[:-1]

    def submit_initials(self, default_name: str | None = None):
        """Submits player initials and records the score in the leaderboard."""
        if not self.initials_submitted:
            name = self.player_initials.strip().upper()
            if not name:
                name = default_name.strip().upper() if default_name else (self.last_player_name or "AAA")
            name = (name + "AAA")[:3]
            self.player_initials = name
            self.last_player_name = name
            self._record_leaderboard_entry(player_name=name)
            self.initials_submitted = True

    def restart(self, mode: GameMode | None = None):
        if self.is_dead and not self.initials_submitted:
            self.submit_initials(default_name=self.last_player_name or "AAA")
        self.player_initials = ""
        self.initials_submitted = False
        self.speed_reduction = 0
        self.pacifier_active = False
        self.pacifier_timer = 0.0
        self.pacifier_spawn_timer = random.uniform(PACIFIER_SPAWN_MIN_INTERVAL, PACIFIER_SPAWN_MAX_INTERVAL)
        self.pacifier_just_spawned = False
        self.pacifier_eaten = False
        self.soothe_message_timer = 0.0
        self.soothe_levels_dropped = 0
        if mode is not None:
            self.game_mode = mode
        self.head_x = 8.5
        self.head_y = 8.5
        self.target_angle = 0.0
        self.current_angle = 0.0
        self.segment_count = 3
        self.path_history.clear()
        for i in range(150):
            dist = i * 0.08
            self.path_history.append((self.head_x - dist, self.head_y))
        self.score = 0
        self.time_remaining = TIME_ATTACK_START_SECONDS
        self.death_reason = ""
        self.is_dead = False
        self.is_paused = False
        self.flash_timer = 0.0
        self.flash_color = None
        self._respawn_food()

    def get_body_segment_positions(self) -> List[Tuple[float, float]]:
        """Samples the coordinates along path_history for each segment."""
        positions = []
        if not self.path_history:
            return positions

        accum_dist = 0.0
        target_dist = self.segment_spacing
        prev_pt = (self.head_x, self.head_y)

        for pt in self.path_history:
            d = math.hypot(pt[0] - prev_pt[0], pt[1] - prev_pt[1])
            accum_dist += d
            prev_pt = pt

            if accum_dist >= target_dist:
                positions.append(pt)
                target_dist += self.segment_spacing
                if len(positions) >= self.segment_count:
                    break

        return positions

    def update(self, dt: float) -> Tuple[bool, bool]:
        """Updates snake physics, time attack timer, and collisions.
        Returns (apple_eaten, speed_increased).
        """
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_color = None

        if self.soothe_message_timer > 0:
            self.soothe_message_timer -= dt
            if self.soothe_message_timer <= 0:
                self.soothe_message_timer = 0.0

        self.pacifier_just_spawned = False
        self.pacifier_eaten = False

        if self.is_dead or self.is_paused:
            return False, False

        # Time attack countdown
        if self.game_mode == GameMode.TIME_ATTACK:
            self.time_remaining -= dt
            if self.time_remaining <= 0.0:
                self.time_remaining = 0.0
                self._trigger_death("Temps écoulé !")
                return False, False

        # Pacifier (Tétine) bonus lifecycle & spawn update
        if not self.pacifier_active:
            self.pacifier_spawn_timer -= dt
            if self.pacifier_spawn_timer <= 0:
                self._respawn_pacifier()
                self.pacifier_active = True
                self.pacifier_timer = PACIFIER_LIFETIME
                self.pacifier_just_spawned = True
        else:
            self.pacifier_timer -= dt
            if self.pacifier_timer <= 0:
                self.pacifier_active = False
                self.pacifier_timer = 0.0
                self.pacifier_spawn_timer = random.uniform(PACIFIER_SPAWN_MIN_INTERVAL, PACIFIER_SPAWN_MAX_INTERVAL)

        # Fast responsive camera rotation towards target 90-degree angle
        angle_diff = (self.target_angle - self.current_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) < 0.03:
            self.current_angle = self.target_angle
        else:
            self.current_angle += angle_diff * min(1.0, 24.0 * dt)

        # Move forward along corridor center line
        speed = self.current_speed
        norm_angle = self.target_angle % (2 * math.pi)
        is_horizontal = (abs(norm_angle - 0.0) < 0.2) or (abs(norm_angle - math.pi) < 0.2) or (abs(norm_angle - 2 * math.pi) < 0.2)

        if is_horizontal:
            dir_x = 1.0 if abs(norm_angle - 0.0) < 0.2 or abs(norm_angle - 2 * math.pi) < 0.2 else -1.0
            new_x = self.head_x + dir_x * speed * dt
            new_y = math.floor(self.head_y) + 0.5  # Locked to row center
            front_check_x = int(new_x + dir_x * 0.38)
            front_check_y = int(new_y)
        else:
            dir_y = 1.0 if abs(norm_angle - math.pi / 2) < 0.2 else -1.0
            new_x = math.floor(self.head_x) + 0.5  # Locked to column center
            new_y = self.head_y + dir_y * speed * dt
            front_check_x = int(new_x)
            front_check_y = int(new_y + dir_y * 0.38)

        # Predictable corridor wall collision: check cell directly ahead in movement lane
        if (
            front_check_x < 0
            or front_check_x >= MAP_WIDTH
            or front_check_y < 0
            or front_check_y >= MAP_HEIGHT
            or self.world_map[front_check_y][front_check_x] > 0
        ):
            self._trigger_death("Mur heurté !")
            return False, False

        self.head_x = new_x
        self.head_y = new_y
        self.bob_time += dt * (speed / DOOM_BASE_SPEED)

        # Update path history
        if not self.path_history or math.hypot(new_x - self.path_history[0][0], new_y - self.path_history[0][1]) >= 0.04:
            self.path_history.insert(0, (new_x, new_y))
            max_history_len = int((self.segment_count + 4) * (self.segment_spacing / 0.04))
            if len(self.path_history) > max_history_len:
                self.path_history = self.path_history[:max_history_len]

        # Self-collision check with body segments (skip neck segments)
        body_segments = self.get_body_segment_positions()
        for seg_idx, (sx, sy) in enumerate(body_segments):
            if seg_idx >= 3:
                if math.hypot(new_x - sx, new_y - sy) < 0.42:
                    self._trigger_death("Corps heurté !")
                    return False, False

        # Food pickup check
        apple_eaten = False
        speed_increased = False

        dist_to_food = math.hypot(new_x - (self.food_x + 0.5), new_y - (self.food_y + 0.5))
        if dist_to_food < 0.60:
            apple_eaten = True
            self.score += 1
            self.segment_count += 1
            if self.game_mode == GameMode.TIME_ATTACK:
                self.time_remaining = min(
                    TIME_ATTACK_MAX_SECONDS,
                    self.time_remaining + TIME_ATTACK_BONUS_PER_APPLE,
                )
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()

            # Sweet pastel pink sparkle flash
            self.flash_color = (255, 195, 215, 60)
            self.flash_timer = 0.22

            # Check if this fruit triggers a speed level increase (multiple of 5)
            if self.score > 0 and self.score % 5 == 0:
                speed_increased = True
                self.flash_color = (255, 230, 160, 85)
                self.flash_timer = 0.35

            self._respawn_food()

        # Pacifier collision check
        if self.pacifier_active:
            dist_to_pacifier = math.hypot(new_x - (self.pacifier_x + 0.5), new_y - (self.pacifier_y + 0.5))
            if dist_to_pacifier < 0.65:
                self.pacifier_eaten = True
                self.pacifier_active = False
                self.pacifier_timer = 0.0
                self.pacifier_spawn_timer = random.uniform(PACIFIER_SPAWN_MIN_INTERVAL, PACIFIER_SPAWN_MAX_INTERVAL)

                cur_lvl = self.speed_level
                levels_dropped = min(PACIFIER_MAX_LEVEL_DROP, cur_lvl - 1)
                self.speed_reduction += levels_dropped
                self.soothe_levels_dropped = levels_dropped
                self.soothe_message_timer = 2.5
                self.flash_color = (180, 245, 235, 80)
                self.flash_timer = 0.35

        return apple_eaten, speed_increased

    def _trigger_death(self, reason: str = "Aïe !"):
        if self.is_dead:
            return
        self.is_dead = True
        self.death_reason = reason
        self.flash_color = (255, 175, 195, 110)
        self.flash_timer = 0.45
        self._save_high_score()
        self.player_initials = ""
        self.initials_submitted = False

    def _load_leaderboard(self) -> Dict[str, List[dict]]:
        default_lb = {"Classique": [], "Chrono": []}
        try:
            if LEADERBOARD_FILE.exists():
                data = json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return {
                        "Classique": data.get("Classique", [])[:5],
                        "Chrono": data.get("Chrono", [])[:5],
                    }
                elif isinstance(data, list):
                    # Migrate legacy flat list
                    res = {"Classique": [], "Chrono": []}
                    for entry in data:
                        m = entry.get("mode", "Classique")
                        if m in res:
                            res[m].append(entry)
                    res["Classique"] = sorted(res["Classique"], key=lambda x: x.get("score", 0), reverse=True)[:5]
                    res["Chrono"] = sorted(res["Chrono"], key=lambda x: x.get("score", 0), reverse=True)[:5]
                    return res
        except Exception:
            pass
        return default_lb

    def _record_leaderboard_entry(self, player_name: str = "AAA"):
        from datetime import datetime
        mode_key = self.game_mode.value  # "Classique" or "Chrono"
        entry = {
            "score": self.score,
            "mode": mode_key,
            "level": self.speed_level,
            "player": (player_name.strip().upper() + "AAA")[:3],
            "date": datetime.now().strftime("%d/%m %H:%M"),
        }
        if mode_key not in self.leaderboard:
            self.leaderboard[mode_key] = []
        self.leaderboard[mode_key].append(entry)
        self.leaderboard[mode_key].sort(key=lambda item: item.get("score", 0), reverse=True)
        self.leaderboard[mode_key] = self.leaderboard[mode_key][:5]
        try:
            LEADERBOARD_FILE.write_text(json.dumps(self.leaderboard, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        except Exception:
            pass

    def _respawn_food(self):
        """Spawns food away from walls and snake body."""
        body = set((int(bx), int(by)) for bx, by in self.get_body_segment_positions())
        body.add((int(self.head_x), int(self.head_y)))

        valid_positions = [
            (x, y)
            for y in range(1, MAP_HEIGHT - 1)
            for x in range(1, MAP_WIDTH - 1)
            if self.world_map[y][x] == 0 and (x, y) not in body
        ]
        if valid_positions:
            self.food_x, self.food_y = random.choice(valid_positions)

    def _respawn_pacifier(self):
        """Spawns pacifier away from walls, snake body, and food."""
        body = set((int(bx), int(by)) for bx, by in self.get_body_segment_positions())
        body.add((int(self.head_x), int(self.head_y)))
        body.add((self.food_x, self.food_y))

        valid_positions = [
            (x, y)
            for y in range(1, MAP_HEIGHT - 1)
            for x in range(1, MAP_WIDTH - 1)
            if self.world_map[y][x] == 0 and (x, y) not in body
        ]
        if valid_positions:
            self.pacifier_x, self.pacifier_y = random.choice(valid_positions)

    def _load_high_score(self) -> int:
        try:
            if DOOM_HIGHSCORE_FILE.exists():
                data = json.loads(DOOM_HIGHSCORE_FILE.read_text())
                return int(data.get("high_score", 0))
        except Exception:
            pass
        return 0

    def _save_high_score(self):
        try:
            KAWAII_HIGHSCORE_FILE.write_text(json.dumps({"high_score": self.high_score}))
        except Exception:
            pass


# Backwards compatibility alias
DoomSnakeGame = KawaiiSnakeGame
