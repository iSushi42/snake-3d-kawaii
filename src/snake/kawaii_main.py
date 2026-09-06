"""Main loop and entry point for 3D Doom-style Snake (uv run snake2)."""

import math
import sys
import pygame
from typing import List, Tuple
from snake.kawaii_audio import KawaiiAudio
from snake.kawaii_config import (
    GameMode,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    MAP_HEIGHT,
    MAP_WIDTH,
    SCALE_FACTOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    THEMES,
    VIEWPORT_HEIGHT,
    ViewMode,
)
from snake.kawaii_game import KawaiiSnakeGame
from snake.kawaii_hud import KawaiiHUD
from snake.kawaii_raycaster import Raycaster
from snake.kawaii_textures import TextureManager


def main():
    pygame.init()
    pygame.display.set_caption("✧ BÉBÉ SNAKE 3D KAWAII ✧")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    audio = KawaiiAudio()
    audio.start_bgm()

    textures = TextureManager()
    raycaster = Raycaster(textures)
    hud = KawaiiHUD(textures)
    game = KawaiiSnakeGame()

    in_start_menu = True
    selected_mode = GameMode.CLASSIC
    was_dead = False
    last_tick_second = -1

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)  # Avoid large frame leaps

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Audio mute toggle (B = Bruit / Musique)
                elif event.key == pygame.K_b:
                    audio.toggle_mute()

                # START MENU CONTROLS
                elif in_start_menu:
                    if event.key == pygame.K_c:
                        game.restart(GameMode.CLASSIC)
                        in_start_menu = False
                        last_tick_second = -1
                    elif event.key == pygame.K_t:
                        game.restart(GameMode.TIME_ATTACK)
                        in_start_menu = False
                        last_tick_second = -1
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        game.restart(selected_mode)
                        in_start_menu = False
                        last_tick_second = -1

                # Restart options when dead
                elif game.is_dead and event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    game.restart()
                    last_tick_second = -1

                elif game.is_dead and event.key == pygame.K_c:
                    game.restart(GameMode.CLASSIC)
                    last_tick_second = -1

                elif game.is_dead and event.key == pygame.K_t:
                    game.restart(GameMode.TIME_ATTACK)
                    last_tick_second = -1

                # Pause toggle
                elif not in_start_menu and not game.is_dead and event.key in (pygame.K_p, pygame.K_SPACE):
                    game.toggle_pause()

                # Camera switch
                elif not in_start_menu and event.key == pygame.K_v:
                    game.toggle_view_mode()

                # Minimap toggle
                elif not in_start_menu and event.key == pygame.K_m:
                    game.toggle_minimap()

                # ZQSD and arrow controls
                elif not in_start_menu and not game.is_dead and not game.is_paused:
                    # Turn Left: Q (AZERTY), A (QWERTY), Left Arrow
                    if event.key in (pygame.K_q, pygame.K_a, pygame.K_LEFT):
                        game.turn_left()

                    # Turn Right: D, Right Arrow
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        game.turn_right()

        # Continuous keys (Boost with Z / W / Up)
        keys = pygame.key.get_pressed()
        if not in_start_menu and not game.is_dead and not game.is_paused:
            game.is_boosting = bool(keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP])

        # Game update (only when in active gameplay)
        if not in_start_menu:
            apple_eaten, speed_increased = game.update(dt)
            if apple_eaten:
                hud.trigger_grin()
                audio.play_eat()
            if speed_increased:
                audio.play_level_up()

            # Audio crash on death
            if game.is_dead and not was_dead:
                audio.play_crash()
            was_dead = game.is_dead

            # Audio tick warning in Time Attack for the last 5 seconds
            if (
                game.game_mode == GameMode.TIME_ATTACK
                and not game.is_dead
                and not game.is_paused
                and game.time_remaining <= 5.0
            ):
                cur_sec = int(game.time_remaining)
                if cur_sec != last_tick_second:
                    last_tick_second = cur_sec
                    audio.play_tick()
            elif game.time_remaining > 5.0:
                last_tick_second = -1

            hud.update(dt)

        # Prepare 3D Sprites for raycaster: (x, y, surface, is_fullbright, world_scale, on_floor)
        sprites = []

        # 1. Food sprite (Fullbright glowing soul-apple, floating at mid-height)
        food_pulse = 1.0 + 0.08 * math.sin(pygame.time.get_ticks() / 200.0)
        sz = max(16, int(64 * food_pulse))
        food_scaled = pygame.transform.scale(textures.sprite_apple, (sz, sz))
        sprites.append((game.food_x + 0.5, game.food_y + 0.5, food_scaled, True, 0.46, False))

        # 2. Body segments (resting on the floor with world_scale 0.40)
        body_positions = game.get_body_segment_positions()
        for bx, by in body_positions:
            sprites.append((bx, by, textures.sprite_segment, False, 0.40, True))

        # 3. If in Chase Cam, render the snake head with cute eyes and blush resting on the floor
        if game.view_mode == ViewMode.CHASE_CAM:
            sprites.append((game.head_x, game.head_y, textures.sprite_snake_head, False, 0.42, True))

        # Determine camera position
        if game.view_mode == ViewMode.FIRST_PERSON:
            cam_x = game.head_x
            cam_y = game.head_y
        else:
            # Chase cam: placed behind head along look vector
            # Trace backwards to prevent clipping into walls
            desired_dist = 2.2
            cos_a = math.cos(game.current_angle)
            sin_a = math.sin(game.current_angle)

            actual_dist = desired_dist
            for step in range(1, int(desired_dist * 10) + 1):
                d = step * 0.1
                test_x = game.head_x - cos_a * d
                test_y = game.head_y - sin_a * d
                tx, ty = int(test_x), int(test_y)
                if (
                    tx < 1 or tx >= MAP_WIDTH - 1
                    or ty < 1 or ty >= MAP_HEIGHT - 1
                    or game.world_map[ty][tx] > 0
                ):
                    actual_dist = max(0.6, d - 0.25)
                    break

            cam_x = game.head_x - cos_a * actual_dist
            cam_y = game.head_y - sin_a * actual_dist

        cam_angle = game.current_angle

        # Render 3D scene onto internal low-res buffer with active theme
        internal_3d = raycaster.render(
            world_map=game.world_map,
            cam_x=cam_x,
            cam_y=cam_y,
            cam_angle=cam_angle,
            view_mode=game.view_mode,
            sprites=sprites,
            bob_time=game.bob_time,
            flash_color=game.flash_color,
            theme_index=game.theme_index,
        )

        # Scale 3D buffer up to high-res viewport
        scaled_viewport = pygame.transform.scale(internal_3d, (SCREEN_WIDTH, VIEWPORT_HEIGHT))
        screen.blit(scaled_viewport, (0, 0))

        # Render Doom bottom status bar
        hud.draw_status_bar(
            surface=screen,
            score=game.score,
            high_score=game.high_score,
            speed_level=game.speed_level,
            current_speed=game.current_speed,
            view_mode=game.view_mode,
            is_dead=game.is_dead,
        )

        # Render Top Badges: Theme & Sound on left, Chrono on right next to map
        active_theme_name = THEMES[game.theme_index]["name"]
        hud.draw_top_badges(
            surface=screen,
            theme_name=active_theme_name,
            game_mode=game.game_mode,
            time_remaining=game.time_remaining,
            is_muted=audio.is_muted,
            show_minimap=game.show_minimap,
        )

        # Render Apple Direction Compass at top center
        hud.draw_apple_compass(
            surface=screen,
            cam_x=cam_x,
            cam_y=cam_y,
            cam_angle=cam_angle,
            food_pos=(game.food_x, game.food_y),
        )

        # Render Automap radar overlay (toggled via M)
        hud.draw_automap_radar(
            surface=screen,
            world_map=game.world_map,
            snake_head=(game.head_x, game.head_y),
            snake_angle=game.current_angle,
            snake_body=body_positions,
            food_pos=(game.food_x, game.food_y),
            show_minimap=game.show_minimap,
        )

        # Render Start Screen, Game Over, or Pause screens
        if in_start_menu:
            hud.draw_start_screen(screen, game.leaderboard, selected_mode)
        elif game.is_dead:
            hud.draw_death_screen(
                surface=screen,
                score=game.score,
                high_score=game.high_score,
                game_mode=game.game_mode,
                death_reason=game.death_reason,
                leaderboard=game.leaderboard,
            )
        elif game.is_paused:
            hud.draw_pause_screen(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
