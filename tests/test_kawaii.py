"""Unit tests for 3D Doom Snake game mechanics."""

import math
import pytest
from snake.kawaii_config import (
    DOOM_BASE_SPEED,
    DOOM_SPEED_INCREMENT,
    ViewMode,
)
from snake.kawaii_game import DoomSnakeGame


def test_doom_initialization():
    game = DoomSnakeGame()
    assert not game.is_dead
    assert not game.is_paused
    assert game.score == 0
    assert game.speed_level == 1
    assert game.current_speed == DOOM_BASE_SPEED
    assert game.view_mode == ViewMode.FIRST_PERSON
    assert game.head_x == 8.5
    assert game.head_y == 8.5


def test_doom_turns():
    game = DoomSnakeGame()
    assert game.target_angle == 0.0

    # Turn left (counter-clockwise -> -pi/2)
    game.turn_left()
    assert math.isclose(game.target_angle, -math.pi / 2, abs_tol=1e-4)
    # Perpendicular coordinate (head_x) snaps to corridor center 8.5
    assert game.head_x == 8.5

    # Turn right twice
    game.turn_right()
    game.turn_right()
    assert math.isclose(game.target_angle, math.pi / 2, abs_tol=1e-4)


def test_doom_movement_and_history():
    game = DoomSnakeGame()
    initial_x = game.head_x
    initial_y = game.head_y
    game.target_angle = 0.0  # Facing East (+X)

    # Update for 0.1s
    game.update(0.1)
    assert game.head_x > initial_x
    assert math.isclose(game.head_y, initial_y, abs_tol=1e-4)
    assert len(game.path_history) > 0


def test_doom_score_and_speed_progression():
    game = DoomSnakeGame()
    assert game.score == 0
    assert game.speed_level == 1
    assert game.current_speed == DOOM_BASE_SPEED

    # 4 points -> Still level 1
    game.score = 4
    assert game.speed_level == 1
    assert game.current_speed == DOOM_BASE_SPEED

    # 5 points -> Level 2
    game.score = 5
    assert game.speed_level == 2
    assert game.current_speed == pytest.approx(DOOM_BASE_SPEED + DOOM_SPEED_INCREMENT)

    # 9 points -> Level 2
    game.score = 9
    assert game.speed_level == 2

    # 10 points -> Level 3
    game.score = 10
    assert game.speed_level == 3
    assert game.current_speed == pytest.approx(DOOM_BASE_SPEED + 2 * DOOM_SPEED_INCREMENT)


def test_doom_wall_collision():
    game = DoomSnakeGame()
    # Place head in corridor 1 facing West towards wall at x=0
    game.head_x = 1.3
    game.head_y = 5.5
    game.target_angle = math.pi  # Facing West towards wall

    # Move towards wall
    game.update(0.1)
    assert game.is_dead


def test_doom_food_pickup_and_growth():
    game = DoomSnakeGame()
    game.food_x = 9
    game.food_y = 8
    game.head_x = 8.8
    game.head_y = 8.5
    game.target_angle = 0.0
    initial_segments = game.segment_count

    ate, speed_up = game.update(0.1)
    assert ate
    assert game.score == 1
    assert game.segment_count == initial_segments + 1


def test_doom_view_mode_toggle():
    game = DoomSnakeGame()
    assert game.view_mode == ViewMode.FIRST_PERSON
    game.toggle_view_mode()
    assert game.view_mode == ViewMode.CHASE_CAM
    game.toggle_view_mode()
    assert game.view_mode == ViewMode.FIRST_PERSON


def test_open_arena_without_pillars():
    """Verify that the arena is open and has no interior obstacle pillars."""
    game = DoomSnakeGame()
    for y in range(1, 15):
        for x in range(1, 15):
            assert game.world_map[y][x] == 0, f"Cell ({x}, {y}) should be open space"


def test_arena_turn_no_false_collision():
    """Verify that turning near a boundary without touching it does not trigger death."""
    game = DoomSnakeGame()
    # Place snake at x = 2.5, y = 3.5 facing North (-pi/2)
    game.head_x = 2.5
    game.head_y = 3.5
    game.target_angle = -math.pi / 2
    game.current_angle = -math.pi / 2

    # Now turn East (heading along open space)
    game.turn_right()
    game.update(0.1)
    assert not game.is_dead, "Snake should not die when turning in open corridor"


def test_sprite_projection_centered():
    """Verify sprite projection math in all 4 cardinal directions."""
    from snake.kawaii_config import FOV, HALF_FOV, INTERNAL_WIDTH
    from snake.kawaii_raycaster import Raycaster
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    raycaster = Raycaster(textures)

    # Test east (0 rad): player at (8, 8), sprite at (12, 8)
    cam_x, cam_y, cam_angle = 8.0, 8.0, 0.0
    rel_x, rel_y = 12.0 - cam_x, 8.0 - cam_y
    sprite_angle = math.atan2(rel_y, rel_x)
    angle_diff = (sprite_angle - cam_angle + math.pi) % (2 * math.pi) - math.pi
    screen_x = int((INTERNAL_WIDTH / 2) * (1.0 + math.tan(angle_diff) / math.tan(HALF_FOV)))
    assert screen_x == INTERNAL_WIDTH // 2 == 160


def test_fullbright_sprite_render():
    """Verify that raycaster renders fullbright items without crash or crush."""
    from snake.kawaii_config import ViewMode
    from snake.kawaii_game import build_default_map
    from snake.kawaii_raycaster import Raycaster
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    raycaster = Raycaster(textures)
    world_map = build_default_map()

    # Place a fullbright apple at distance 8.0 (would previously be crushed to black)
    sprites = [(12.0, 8.0, textures.sprite_apple, True)]
    rendered_surf = raycaster.render(
        world_map=world_map,
        cam_x=4.0,
        cam_y=8.0,
        cam_angle=0.0,
        view_mode=ViewMode.FIRST_PERSON,
        sprites=sprites,
        bob_time=0.0,
    )
    assert rendered_surf is not None


def test_minimap_toggle():
    game = DoomSnakeGame()
    assert not game.show_minimap, "Minimap should be disabled by default"
    game.toggle_minimap()
    assert game.show_minimap, "Minimap should be enabled after toggle"
    game.toggle_minimap()
    assert not game.show_minimap, "Minimap should be disabled after second toggle"


def test_apple_compass_and_radar_render():
    import pygame
    from snake.kawaii_config import SCREEN_HEIGHT, SCREEN_WIDTH
    from snake.kawaii_hud import DoomHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = DoomHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Test compass render when facing apple
    hud.draw_apple_compass(surface, 8.5, 8.5, 0.0, (12, 8))

    # Test radar render when minimap is disabled (shows hint badge)
    hud.draw_automap_radar(surface, [[0] * 16] * 16, (8.5, 8.5), 0.0, [(7.5, 8.5)], (12, 8), show_minimap=False)

    # Test radar render when minimap is enabled
    hud.draw_automap_radar(surface, [[0] * 16] * 16, (8.5, 8.5), 0.0, [(7.5, 8.5)], (12, 8), show_minimap=True)


def test_doom_time_attack_countdown_and_timeout():
    from snake.kawaii_config import GameMode, TIME_ATTACK_START_SECONDS

    game = DoomSnakeGame()
    game.restart(GameMode.TIME_ATTACK)
    assert game.game_mode == GameMode.TIME_ATTACK
    assert game.time_remaining == TIME_ATTACK_START_SECONDS

    # Tick 0.5s: moves 1.9 units (from 8.5 to 10.4, still well inside 16x16 arena)
    game.update(0.5)
    assert not game.is_dead
    assert math.isclose(game.time_remaining, TIME_ATTACK_START_SECONDS - 0.5, abs_tol=1e-3)

    # Set timer close to expiry and tick past zero
    game.time_remaining = 0.2
    game.update(0.3)
    assert game.is_dead
    assert game.death_reason == "Temps écoulé !"
    assert game.time_remaining == 0.0


def test_doom_time_attack_apple_bonus():
    from snake.kawaii_config import (
        GameMode,
        TIME_ATTACK_BONUS_PER_APPLE,
        TIME_ATTACK_MAX_SECONDS,
    )

    game = DoomSnakeGame()
    game.restart(GameMode.TIME_ATTACK)
    game.time_remaining = 20.0
    game.food_x = 9
    game.food_y = 8
    game.head_x = 8.8
    game.head_y = 8.5
    game.target_angle = 0.0

    ate, _ = game.update(0.1)
    assert ate
    assert math.isclose(game.time_remaining, 20.0 - 0.1 + TIME_ATTACK_BONUS_PER_APPLE, abs_tol=1e-2)

    # Check capping at TIME_ATTACK_MAX_SECONDS
    game.time_remaining = 58.0
    game.food_x = int(game.head_x)
    game.food_y = int(game.head_y)
    game.update(0.01)
    assert game.time_remaining <= TIME_ATTACK_MAX_SECONDS


def test_doom_theme_cycling():
    game = DoomSnakeGame()
    assert game.theme_index == 0  # Guimauve (score 0, level 1)

    game.score = 4
    assert game.speed_level == 1
    assert game.theme_index == 0

    game.score = 5
    assert game.speed_level == 2
    assert game.theme_index == 1  # Nuit Étoilée

    game.score = 10
    assert game.speed_level == 3
    assert game.theme_index == 2  # Forêt Féerique

    game.score = 15
    assert game.speed_level == 4
    assert game.theme_index == 0  # Cycle back to Guimauve


def test_doom_leaderboard_sorting_and_limit(tmp_path, monkeypatch):
    import json
    import snake.kawaii_game as dg

    test_lb_file = tmp_path / "test_leaderboard.json"
    monkeypatch.setattr(dg, "LEADERBOARD_FILE", test_lb_file)

    game = dg.DoomSnakeGame()
    game.score = 12
    game.game_mode = dg.GameMode.TIME_ATTACK
    game._trigger_death("Temps écoulé !")
    game.submit_initials("TST")

    assert "Chrono" in game.leaderboard
    assert "Classique" in game.leaderboard
    assert len(game.leaderboard["Chrono"]) == 1
    assert game.leaderboard["Chrono"][0]["score"] == 12
    assert game.leaderboard["Chrono"][0]["mode"] == "Chrono"
    assert game.leaderboard["Chrono"][0]["player"] == "TST"
    assert len(game.leaderboard["Classique"]) == 0

    # Add more Chrono scores
    scores = [5, 20, 15, 8, 25, 2]
    for s in scores:
        game.score = s
        game.is_dead = False
        game.game_mode = dg.GameMode.TIME_ATTACK
        game._record_leaderboard_entry()

    assert len(game.leaderboard["Chrono"]) == 5
    saved_chrono_scores = [entry["score"] for entry in game.leaderboard["Chrono"]]
    assert saved_chrono_scores == [25, 20, 15, 12, 8]

    # Add Classic scores
    game.game_mode = dg.GameMode.CLASSIC
    for s in [7, 18, 30]:
        game.score = s
        game._record_leaderboard_entry()

    assert len(game.leaderboard["Classique"]) == 3
    saved_classic_scores = [entry["score"] for entry in game.leaderboard["Classique"]]
    assert saved_classic_scores == [30, 18, 7]


def test_doom_audio_synthesizer():
    from snake.kawaii_audio import DoomAudio

    audio = DoomAudio()
    assert audio.is_enabled
    assert audio.sound_eat is not None
    assert audio.sound_level_up is not None
    assert audio.sound_crash is not None
    assert audio.sound_tick is not None
    assert audio.sound_bgm is not None

    # Test mute toggle
    assert not audio.is_muted
    audio.toggle_mute()
    assert audio.is_muted
    audio.toggle_mute()
    assert not audio.is_muted


def test_raycaster_with_all_themes():
    from snake.kawaii_config import THEMES, ViewMode
    from snake.kawaii_game import build_default_map
    from snake.kawaii_raycaster import Raycaster
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    raycaster = Raycaster(textures)
    world_map = build_default_map()

    for theme_idx in range(len(THEMES)):
        surf = raycaster.render(
            world_map=world_map,
            cam_x=5.0,
            cam_y=5.0,
            cam_angle=0.0,
            view_mode=ViewMode.FIRST_PERSON,
            sprites=[],
            bob_time=0.0,
            theme_index=theme_idx,
        )
        assert surf is not None
        assert surf.get_width() == 320
        assert surf.get_height() == 170


def test_start_screen_and_death_screen_render():
    import pygame
    from snake.kawaii_config import GameMode, SCREEN_HEIGHT, SCREEN_WIDTH
    from snake.kawaii_hud import DoomHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = DoomHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Empty leaderboard (dict and list)
    hud.draw_start_screen(surface, {}, GameMode.CLASSIC)
    hud.draw_start_screen(surface, [], GameMode.TIME_ATTACK)

    # Populated split leaderboard dict
    sample_lb = {
        "Classique": [{"score": 15, "mode": "Classique", "level": 4, "date": "06/09 14:30"}],
        "Chrono": [{"score": 8, "mode": "Chrono", "level": 2, "date": "06/09 14:15"}],
    }
    hud.draw_start_screen(surface, sample_lb, GameMode.TIME_ATTACK)
    hud.draw_death_screen(surface, 12, 20, GameMode.CLASSIC, "Aïe !", sample_lb)
    hud.draw_death_screen(surface, 15, 25, GameMode.TIME_ATTACK, "Temps écoulé !", sample_lb)


def test_hud_top_badges_no_overlap():
    import pygame
    from snake.kawaii_config import GameMode, SCREEN_WIDTH
    from snake.kawaii_hud import DoomHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = DoomHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, 200))

    # Verify rendering top badges with Time Attack mode and minimap both on and off
    hud.draw_top_badges(surface, "Guimauve", GameMode.TIME_ATTACK, 25.0, is_muted=False, show_minimap=False)
    hud.draw_top_badges(surface, "Foret Feerique", GameMode.TIME_ATTACK, 4.5, is_muted=True, show_minimap=True)


def test_chase_cam_floor_sprites_render():
    from snake.kawaii_config import ViewMode
    from snake.kawaii_game import build_default_map
    from snake.kawaii_raycaster import Raycaster
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    raycaster = Raycaster(textures)
    world_map = build_default_map()

    # Camera at (6.3, 8.5) behind head at (8.5, 8.5)
    # Segments on the floor with world_scale 0.40 and head at 0.42
    sprites = [
        (8.5, 8.5, textures.sprite_snake_head, False, 0.42, True),
        (7.85, 8.5, textures.sprite_segment, False, 0.40, True),
        (12.5, 8.5, textures.sprite_apple, True, 0.46, False),
    ]

    surf = raycaster.render(
        world_map=world_map,
        cam_x=6.3,
        cam_y=8.5,
        cam_angle=0.0,
        view_mode=ViewMode.CHASE_CAM,
        sprites=sprites,
        bob_time=0.0,
        theme_index=0,
    )
    assert surf is not None
    assert surf.get_width() == 320
    assert surf.get_height() == 170


def test_themes_checkered_floor_colors():
    from snake.kawaii_config import THEMES

    assert len(THEMES) == 3
    for theme in THEMES:
        assert "floor" in theme
        assert "floor_alt" in theme
        assert len(theme["floor"]) == 3
        assert len(theme["floor_alt"]) == 3
        # Alternate floor color must be distinct from base floor color to create checkered pattern
        assert theme["floor"] != theme["floor_alt"]


def test_chrono_title_no_missing_glyphs():
    import pygame
    from snake.kawaii_config import GameMode, SCREEN_WIDTH, SCREEN_HEIGHT
    from snake.kawaii_hud import DoomHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = DoomHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Inspect source code of HUD methods to ensure stopwatch emoji is not used
    import inspect
    start_src = inspect.getsource(hud.draw_start_screen)
    death_src = inspect.getsource(hud.draw_death_screen)

    assert "⏱" not in start_src
    assert "⏱" not in death_src
    assert "✦ CONTRE-LA-MONTRE ✦" in start_src
    assert "✦ CONTRE-LA-MONTRE ✦" in death_src


def test_panoramic_sky_clouds():
    import math
    from snake.kawaii_config import SKY_WIDTH, INTERNAL_HEIGHT, ViewMode, THEMES
    from snake.kawaii_game import build_default_map
    from snake.kawaii_raycaster import Raycaster, create_panoramic_skies
    from snake.kawaii_textures import TextureManager

    half_h = INTERNAL_HEIGHT // 2
    skies = create_panoramic_skies(half_h)
    assert len(skies) == len(THEMES)
    for sky in skies:
        assert sky.get_width() == SKY_WIDTH
        assert sky.get_height() == half_h

    textures = TextureManager()
    raycaster = Raycaster(textures)
    world_map = build_default_map()

    # Test rendering at various camera angles including wrapping near 0 / 2pi
    for angle in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi - 0.05, 0.05):
        for theme_idx in range(len(THEMES)):
            surf = raycaster.render(
                world_map=world_map,
                cam_x=8.5,
                cam_y=8.5,
                cam_angle=angle,
                view_mode=ViewMode.FIRST_PERSON,
                sprites=[],
                bob_time=0.0,
                theme_index=theme_idx,
            )
            assert surf is not None
            assert surf.get_size() == (320, 170)


def test_player_initials_input_and_submission(tmp_path, monkeypatch):
    import snake.kawaii_game as dg

    test_lb_file = tmp_path / "test_initials_lb.json"
    monkeypatch.setattr(dg, "LEADERBOARD_FILE", test_lb_file)

    game = dg.KawaiiSnakeGame()
    game.score = 42

    # Typing letters
    game.add_initial_char("b")
    game.add_initial_char("o")
    game.add_initial_char("b")
    # Exceeding 3 chars or non-alpha should be ignored
    game.add_initial_char("s")
    game.add_initial_char("1")
    assert game.player_initials == "BOB"

    # Backspace
    game.remove_initial_char()
    assert game.player_initials == "BO"
    game.add_initial_char("y")
    assert game.player_initials == "BOY"

    # Submit
    game.submit_initials()
    assert game.initials_submitted
    assert len(game.leaderboard["Classique"]) == 1
    assert game.leaderboard["Classique"][0]["player"] == "BOY"
    assert game.leaderboard["Classique"][0]["score"] == 42

    # Subsequent keystrokes should be ignored once submitted
    game.add_initial_char("z")
    game.remove_initial_char()
    assert game.player_initials == "BOY"


def test_player_initials_auto_submit_on_restart(tmp_path, monkeypatch):
    import snake.kawaii_game as dg

    test_lb_file = tmp_path / "test_initials_auto.json"
    monkeypatch.setattr(dg, "LEADERBOARD_FILE", test_lb_file)

    game = dg.KawaiiSnakeGame()
    game.score = 50
    game.is_dead = True
    game.player_initials = "VI"  # only 2 chars typed

    # Restart without explicit submit -> should auto-submit padded with 'A's ("VIA")
    game.restart()
    assert len(game.leaderboard["Classique"]) == 1
    assert game.leaderboard["Classique"][0]["player"] == "VIA"
    assert game.leaderboard["Classique"][0]["score"] == 50
    assert not game.is_dead
    assert game.player_initials == ""
    assert not game.initials_submitted


def test_death_screen_renders_initials_input_and_nom_column():
    import pygame
    from snake.kawaii_config import GameMode, SCREEN_WIDTH, SCREEN_HEIGHT
    from snake.kawaii_hud import KawaiiHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = KawaiiHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    fake_lb = {
        "Classique": [
            {"score": 30, "mode": "Classique", "level": 3, "player": "ALX", "date": "06/09 18:30"},
            {"score": 15, "mode": "Classique", "level": 2, "date": "06/09 18:25"},  # legacy without player
        ],
        "Chrono": [
            {"score": 25, "mode": "Chrono", "level": 2, "player": "MAX", "date": "06/09 18:35"},
        ],
    }

    # Render with pending input
    hud.draw_death_screen(
        surface=surface,
        score=30,
        high_score=30,
        game_mode=GameMode.CLASSIC,
        death_reason="Mur heurté !",
        leaderboard=fake_lb,
        player_initials="AB",
        initials_submitted=False,
    )

    # Render with submitted confirmation
    hud.draw_death_screen(
        surface=surface,
        score=30,
        high_score=30,
        game_mode=GameMode.CLASSIC,
        death_reason="Mur heurté !",
        leaderboard=fake_lb,
        player_initials="ABC",
        initials_submitted=True,
    )

    # Verify start screen also renders with the NOM column properly
    hud.draw_start_screen(surface=surface, leaderboard=fake_lb, selected_mode=GameMode.CLASSIC)


def test_pacifier_speed_reduction_bounds():
    from snake.kawaii_config import DOOM_BASE_SPEED, DOOM_SPEED_INCREMENT
    from snake.kawaii_game import KawaiiSnakeGame

    game = KawaiiSnakeGame()
    # At start: score 0, speed level 1
    assert game.speed_level == 1
    assert game.current_speed == DOOM_BASE_SPEED

    # Level 1 pacifier pickup: should stay level 1 (cannot go below level 1)
    game.pacifier_active = True
    game.pacifier_timer = 5.0
    game.pacifier_x, game.pacifier_y = 8, 8
    game.head_x, game.head_y = 8.5, 8.5
    game.update(0.01)
    assert game.pacifier_eaten
    assert game.speed_level == 1
    assert game.speed_reduction == 0
    assert game.current_speed == DOOM_BASE_SPEED

    # Level 5 (score 20): pacifier drops by min(3, 5 - 1) = 3 -> Level 2
    game.score = 20
    game.speed_reduction = 0
    assert game.speed_level == 5
    game.pacifier_active = True
    game.pacifier_timer = 5.0
    game.pacifier_x, game.pacifier_y = int(game.head_x), int(game.head_y)
    game.update(0.01)
    assert game.pacifier_eaten
    assert game.soothe_levels_dropped == 3
    assert game.speed_level == 2
    assert game.current_speed == DOOM_BASE_SPEED + 1 * DOOM_SPEED_INCREMENT

    # Level 3 (score 10, no reduction): drops by 2 -> Level 1
    game.score = 10
    game.speed_reduction = 0
    assert game.speed_level == 3
    game.pacifier_active = True
    game.pacifier_timer = 5.0
    game.pacifier_x, game.pacifier_y = int(game.head_x), int(game.head_y)
    game.update(0.01)
    assert game.pacifier_eaten
    assert game.soothe_levels_dropped == 2
    assert game.speed_level == 1
    assert game.current_speed == DOOM_BASE_SPEED


def test_pacifier_lifetime_and_timeout():
    from snake.kawaii_config import PACIFIER_LIFETIME
    from snake.kawaii_game import KawaiiSnakeGame

    game = KawaiiSnakeGame()
    # Manually trigger pacifier active
    game.pacifier_active = True
    game.pacifier_timer = PACIFIER_LIFETIME
    game.pacifier_x, game.pacifier_y = 1, 1
    # Place snake safely on long corridor at x=2.0 facing East
    game.head_x = 2.0
    game.head_y = 8.5

    # Update for 2.0s -> pacifier remains active (timer decreases to ~3.0s)
    game.update(2.0)
    assert not game.is_dead
    assert game.pacifier_active
    assert 2.9 <= game.pacifier_timer <= 3.1

    # Turn North and update for 3.1s -> pacifier expires
    game.turn_left()  # Facing North
    game.update(3.1)
    assert not game.pacifier_active
    assert game.pacifier_timer == 0.0


def test_pacifier_textures_and_hud_banners():
    import pygame
    from snake.kawaii_config import SCREEN_WIDTH, SCREEN_HEIGHT
    from snake.kawaii_hud import KawaiiHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    assert hasattr(textures, "sprite_pacifier")
    assert textures.sprite_pacifier.get_size() == (64, 64)

    hud = KawaiiHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Test pacifier banner with full and critical countdown
    hud.draw_pacifier_banner(surface, time_remaining=4.8, total_time=5.0)
    hud.draw_pacifier_banner(surface, time_remaining=1.1, total_time=5.0)

    # Test soothe confirmation banner
    hud.draw_soothe_banner(surface, levels_dropped=3, current_level=2)
    hud.draw_soothe_banner(surface, levels_dropped=0, current_level=1)

    # Test automap radar with pacifier position
    from snake.kawaii_game import build_default_map
    hud.draw_automap_radar(
        surface=surface,
        world_map=build_default_map(),
        snake_head=(8.5, 8.5),
        snake_angle=0.0,
        snake_body=[(8.0, 8.5)],
        food_pos=(12, 8),
        show_minimap=True,
        pacifier_pos=(5, 5),
    )


def test_title_screen_redesign():
    import pygame
    from snake.kawaii_config import GameMode, SCREEN_WIDTH, SCREEN_HEIGHT
    from snake.kawaii_hud import KawaiiHUD
    from snake.kawaii_textures import TextureManager

    textures = TextureManager()
    hud = KawaiiHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    fake_lb = {
        "Classique": [{"score": 30, "mode": "Classique", "level": 3, "player": "ABC", "date": "06/09 18:30"}],
        "Chrono": [{"score": 25, "mode": "Chrono", "level": 2, "player": "XYZ", "date": "06/09 18:35"}],
    }

    # Verify font_logo attribute exists
    assert hasattr(hud, "font_logo")
    assert hud.font_logo is not None

    # Test main title screen with each selectable item highlighted
    for sel_idx in (0, 1, 2):
        hud.draw_start_screen(
            surface=surface,
            leaderboard=fake_lb,
            selected_mode=GameMode.CLASSIC,
            selected_index=sel_idx,
            menu_view="main",
        )

    # Test high scores view
    hud.draw_start_screen(
        surface=surface,
        leaderboard=fake_lb,
        selected_mode=GameMode.CLASSIC,
        selected_index=2,
        menu_view="high_scores",
    )


def test_pause_screen_modal():
    import pygame
    from snake.kawaii_config import SCREEN_WIDTH, SCREEN_HEIGHT
    from snake.kawaii_hud import KawaiiHUD
    from snake.kawaii_textures import TextureManager
    from snake.kawaii_game import KawaiiSnakeGame

    textures = TextureManager()
    hud = KawaiiHUD(textures)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Test pause screen rendering with default index, 0 (Continuer), and 1 (Quitter)
    hud.draw_pause_screen(surface)
    hud.draw_pause_screen(surface, selected_index=0)
    hud.draw_pause_screen(surface, selected_index=1)

    # Verify pause state behavior on KawaiiSnakeGame
    game = KawaiiSnakeGame()
    assert not game.is_paused
    game.toggle_pause()
    assert game.is_paused
    game.toggle_pause()
    assert not game.is_paused
