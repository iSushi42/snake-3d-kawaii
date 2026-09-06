"""High performance raycasting engine with DDA, distance fog and 3D sprite billboards."""

import math
import numpy as np
import pygame
from typing import List, Tuple
from snake.kawaii_config import (
    COLOR_CEILING,
    COLOR_FLOOR,
    COLOR_FOG,
    DELTA_ANGLE,
    DIST_TO_PROJ_PLANE,
    FOV,
    HALF_FOV,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    MAP_HEIGHT,
    MAP_WIDTH,
    MAX_DEPTH,
    NUM_RAYS,
    THEMES,
    ViewMode,
)
from snake.kawaii_textures import TEXTURE_SIZE, TextureManager


class Raycaster:
    def __init__(self, textures: TextureManager):
        self.textures = textures
        self.depth_buffer = np.zeros(NUM_RAYS, dtype=np.float32)
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        # Pre-generate backgrounds for all 3 cyclical themes
        self.theme_bg_surfaces = []
        half_h = INTERNAL_HEIGHT // 2
        for t_info in THEMES:
            bg_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
            cr, cg, cb = t_info["ceiling"]
            fr, fg, fb = t_info["floor"]
            for y in range(half_h):
                factor = y / half_h
                r = min(255, int(cr * (0.94 + factor * 0.06)))
                g = min(255, int(cg * (0.94 + factor * 0.06)))
                b = min(255, int(cb * (0.94 + factor * 0.06)))
                pygame.draw.line(bg_surf, (r, g, b), (0, y), (INTERNAL_WIDTH, y))
            for y in range(half_h, INTERNAL_HEIGHT):
                factor = (y - half_h) / half_h
                r = max(0, int(fr * (1.0 - factor * 0.06)))
                g = max(0, int(fg * (1.0 - factor * 0.06)))
                b = max(0, int(fb * (1.0 - factor * 0.06)))
                pygame.draw.line(bg_surf, (r, g, b), (0, y), (INTERNAL_WIDTH, y))
            self.theme_bg_surfaces.append(bg_surf)

        # Checkered floor precomputations (sol en damier)
        self.num_floor_rows = INTERNAL_HEIGHT - half_h
        self.floor_surface = pygame.Surface((INTERNAL_WIDTH, self.num_floor_rows))

        # Precompute ray angle tangents for floor casting
        ray_angles = -HALF_FOV + np.arange(NUM_RAYS, dtype=np.float32) * DELTA_ANGLE
        self.floor_tan_alpha = np.tan(ray_angles).reshape(1, NUM_RAYS)

        # Precompute row distances for floor rows (1 to num_floor_rows)
        p = np.arange(1, self.num_floor_rows + 1, dtype=np.float32).reshape(self.num_floor_rows, 1)
        self.floor_row_dist = ((0.5 * DIST_TO_PROJ_PLANE) / p).astype(np.float32)

        # Distance fog factor for floor rows
        row_fog = np.clip((self.floor_row_dist / MAX_DEPTH) ** 1.3, 0.0, 1.0).reshape(self.num_floor_rows, 1, 1).astype(np.float32)

        # Precompute fog-shaded colors for both checker tiles per theme
        self.theme_floor_colors = []
        for t_info in THEMES:
            c0 = np.array(t_info["floor"], dtype=np.float32)
            c1 = np.array(t_info.get("floor_alt", t_info["floor"]), dtype=np.float32)
            fog = np.array(t_info["fog"], dtype=np.float32)

            col0_by_row = (c0 * (1.0 - row_fog) + fog * row_fog).astype(np.uint8)
            col1_by_row = (c1 * (1.0 - row_fog) + fog * row_fog).astype(np.uint8)
            self.theme_floor_colors.append((col0_by_row, col1_by_row))

    def render(
        self,
        world_map: List[List[int]],
        cam_x: float,
        cam_y: float,
        cam_angle: float,
        view_mode: ViewMode,
        sprites: List[Tuple],
        bob_time: float,
        flash_color: Tuple[int, int, int, int] | None = None,
        theme_index: int = 0,
    ) -> pygame.Surface:
        theme = THEMES[theme_index % len(THEMES)]
        fog_color = theme["fog"]
        half_h = INTERNAL_HEIGHT // 2

        # 1. Reset buffer with active theme ceiling/floor
        bg_surface = self.theme_bg_surfaces[theme_index % len(self.theme_bg_surfaces)]
        self.internal_surface.blit(bg_surface, (0, 0))

        # 1b. Render checkered floor (sol en damier)
        col0_by_row, col1_by_row = self.theme_floor_colors[theme_index % len(self.theme_floor_colors)]
        dir_x = math.cos(cam_angle)
        dir_y = math.sin(cam_angle)

        ray_dir_x = dir_x - dir_y * self.floor_tan_alpha
        ray_dir_y = dir_y + dir_x * self.floor_tan_alpha

        fx = cam_x + self.floor_row_dist * ray_dir_x
        fy = cam_y + self.floor_row_dist * ray_dir_y

        checker = (np.floor(fx).astype(np.int32) + np.floor(fy).astype(np.int32)) & 1
        floor_rgb = np.where(checker[:, :, None] == 0, col0_by_row, col1_by_row)
        pygame.surfarray.blit_array(self.floor_surface, np.transpose(floor_rgb, (1, 0, 2)))
        self.internal_surface.blit(self.floor_surface, (0, half_h))

        # 2. Cast rays across FOV using DDA
        ray_angle = cam_angle - HALF_FOV

        # Fast DDA loop
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # Avoid division by zero
            sin_a = sin_a if sin_a != 0 else 0.00001
            cos_a = cos_a if cos_a != 0 else 0.00001

            # Grid step coordinates
            map_x = int(cam_x)
            map_y = int(cam_y)

            # Delta distances
            delta_dist_x = abs(1.0 / cos_a)
            delta_dist_y = abs(1.0 / sin_a)

            if cos_a < 0:
                step_x = -1
                side_dist_x = (cam_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - cam_x) * delta_dist_x

            if sin_a < 0:
                step_y = -1
                side_dist_y = (cam_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - cam_y) * delta_dist_y

            # DDA Step
            hit = False
            side = 0
            wall_type = 1

            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                    hit = True
                    wall_type = 1
                    break
                elif world_map[map_y][map_x] > 0:
                    hit = True
                    wall_type = world_map[map_y][map_x]

            if side == 0:
                perp_wall_dist = (map_x - cam_x + (1 - step_x) / 2) / cos_a
                wall_x = cam_y + perp_wall_dist * sin_a
            else:
                perp_wall_dist = (map_y - cam_y + (1 - step_y) / 2) / sin_a
                wall_x = cam_x + perp_wall_dist * cos_a

            wall_x -= math.floor(wall_x)

            # Correct fisheye
            corrected_dist = perp_wall_dist * math.cos(cam_angle - ray_angle)
            corrected_dist = max(0.05, corrected_dist)
            self.depth_buffer[ray] = corrected_dist

            # Projected line height
            line_height = int((1.0 / corrected_dist) * DIST_TO_PROJ_PLANE)
            draw_start = half_h - line_height // 2
            draw_end = draw_start + line_height

            # Texture mapping
            tex_x = int(wall_x * TEXTURE_SIZE)
            if side == 0 and cos_a > 0:
                tex_x = TEXTURE_SIZE - tex_x - 1
            if side == 1 and sin_a < 0:
                tex_x = TEXTURE_SIZE - tex_x - 1

            # Select wall texture according to theme
            theme_walls = self.textures.theme_walls
            src_tex = theme_walls[theme_index % len(theme_walls)]
            tex_col = src_tex.subsurface((tex_x, 0, 1, TEXTURE_SIZE))

            # Scale and slice
            scaled_col = pygame.transform.scale(tex_col, (1, line_height))

            # Fog shading
            fog_factor = min(1.0, (corrected_dist / MAX_DEPTH) ** 1.3)
            if side == 1:
                fog_factor = min(1.0, fog_factor + 0.12)  # Side wall shadowing

            if fog_factor > 0.05:
                shade_surf = pygame.Surface((1, line_height), pygame.SRCALPHA)
                shade_surf.fill((fog_color[0], fog_color[1], fog_color[2], int(fog_factor * 255)))
                scaled_col.blit(shade_surf, (0, 0))

            # Clip vertical slice
            y_dest = draw_start
            src_rect = pygame.Rect(0, 0, 1, line_height)
            if y_dest < 0:
                src_rect.y = -y_dest
                src_rect.height += y_dest
                y_dest = 0
            if y_dest + src_rect.height > INTERNAL_HEIGHT:
                src_rect.height = INTERNAL_HEIGHT - y_dest

            if src_rect.height > 0:
                self.internal_surface.blit(scaled_col, (ray, y_dest), src_rect)

            ray_angle += DELTA_ANGLE

        # 3. Render 3D Billboard Sprites (sorted back to front)
        self._render_sprites(cam_x, cam_y, cam_angle, sprites)

        # 4. First-Person Fangs Overlay
        if view_mode == ViewMode.FIRST_PERSON:
            fang_bob = math.sin(bob_time * 9.0) * 3.5
            fx = (INTERNAL_WIDTH - self.textures.fangs_overlay.get_width()) // 2
            fy = INTERNAL_HEIGHT - self.textures.fangs_overlay.get_height() + int(fang_bob) + 12
            self.internal_surface.blit(self.textures.fangs_overlay, (fx, fy))

        # 5. Screen flash overlay (Damage or Apple collection)
        if flash_color:
            flash_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill(flash_color)
            self.internal_surface.blit(flash_surf, (0, 0))

        return self.internal_surface

    def _render_sprites(
        self,
        cam_x: float,
        cam_y: float,
        cam_angle: float,
        sprites: List[Tuple],
    ):
        """Draws billboard sprites sorted by distance with depth buffer check."""
        if not sprites:
            return

        half_h = INTERNAL_HEIGHT // 2

        # Sort back to front by Euclidean distance
        sorted_sprites = []
        for item in sprites:
            sx, sy, img = item[0], item[1], item[2]
            is_fullbright = item[3] if len(item) > 3 else False
            world_scale = item[4] if len(item) > 4 else 1.0
            on_floor = item[5] if len(item) > 5 else False
            dist = math.hypot(sx - cam_x, sy - cam_y)
            sorted_sprites.append((dist, sx, sy, img, is_fullbright, world_scale, on_floor))
        sorted_sprites.sort(key=lambda s: s[0], reverse=True)

        for dist, sx, sy, img, is_fullbright, world_scale, on_floor in sorted_sprites:
            min_allowed_dist = 0.35 if on_floor else 0.15
            if dist < min_allowed_dist:
                continue

            rel_x = sx - cam_x
            rel_y = sy - cam_y

            # Angle to sprite
            sprite_angle = math.atan2(rel_y, rel_x)
            angle_diff = (sprite_angle - cam_angle + math.pi) % (2 * math.pi) - math.pi

            # Perpendicular distance along camera view direction (eliminates fisheye)
            perp_dist = dist * math.cos(angle_diff)

            # Skip if behind camera or too close/far
            if perp_dist <= 0.25 or perp_dist > MAX_DEPTH:
                continue

            # Skip if completely outside field of view (with generous margin for sprite size)
            if abs(angle_diff) > HALF_FOV + 0.5:
                continue

            # Screen X projection (exact match with ray angles)
            screen_x = int((INTERNAL_WIDTH / 2) * (1.0 + math.tan(angle_diff) / math.tan(HALF_FOV)))
            sprite_size = int((world_scale / perp_dist) * DIST_TO_PROJ_PLANE)

            if sprite_size <= 2 or sprite_size > 700:
                continue

            half_sz = sprite_size // 2
            start_x = screen_x - half_sz
            end_x = screen_x + half_sz

            line_height = int((1.0 / perp_dist) * DIST_TO_PROJ_PLANE)
            if on_floor:
                # Rest on the floor for snake body and head!
                floor_y = half_h + line_height // 2
                start_y = floor_y - sprite_size + int(sprite_size * 0.05)
            else:
                # Floating object (e.g. apple)
                center_y = half_h + int(line_height * 0.10)
                start_y = center_y - half_sz

            # Check if anywhere on screen
            if end_x < 0 or start_x >= INTERNAL_WIDTH:
                continue

            # Scale sprite
            scaled_img = pygame.transform.scale(img, (sprite_size, sprite_size))

            # Apply lighting / distance shading:
            # Fullbright items (like Doom radioactive apples) are completely immune to darkness!
            if not is_fullbright:
                brightness = max(0.35, 1.0 - (perp_dist / MAX_DEPTH) * 0.75)
                if brightness < 0.96:
                    b_val = int(brightness * 255)
                    dim_surf = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
                    dim_surf.fill((b_val, b_val, b_val, 255))
                    scaled_img.blit(dim_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Draw column slices that pass depth buffer test
            x_min = max(0, start_x)
            x_max = min(INTERNAL_WIDTH, end_x)

            for x in range(x_min, x_max):
                if perp_dist < self.depth_buffer[x]:
                    sub_x = x - start_x
                    slice_rect = pygame.Rect(sub_x, 0, 1, sprite_size)
                    self.internal_surface.blit(scaled_img, (x, start_y), slice_rect)
