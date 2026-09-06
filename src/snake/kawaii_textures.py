"""Procedural cute kawaii baby pastel textures, sprites and animated baby snake face."""

import math
import numpy as np
import pygame
from typing import Dict

TEXTURE_SIZE = 64


def create_wall_texture_candy() -> pygame.Surface:
    """Cute baby pink marshmallow candy wall with white polka dots and soft bevels."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surf.fill((255, 220, 230))  # Soft baby pink base

    # Soft candy blocks grid
    for y in (0, 32):
        for x in (0, 32):
            rect = pygame.Rect(x + 1, y + 1, 30, 30)
            pygame.draw.rect(surf, (255, 234, 242), rect, border_radius=6)
            # Soft inner shadow / bevel
            pygame.draw.rect(surf, (255, 205, 220), rect, width=1, border_radius=6)

    # Cute pastel polka dots
    dots = [(10, 10), (22, 22), (42, 10), (54, 22), (10, 42), (22, 54), (42, 42), (54, 54)]
    for dx, dy in dots:
        pygame.draw.circle(surf, (255, 255, 255), (dx, dy), 2)

    # Little cute pastel yellow stars
    for sx, sy in [(16, 16), (48, 48)]:
        star_pts = [
            (sx, sy - 4), (sx + 1, sy - 1), (sx + 4, sy), (sx + 1, sy + 1),
            (sx, sy + 4), (sx - 1, sy + 1), (sx - 4, sy), (sx - 1, sy - 1),
        ]
        pygame.draw.polygon(surf, (255, 242, 175), star_pts)

    return surf


def create_wall_texture_blocks() -> pygame.Surface:
    """Cute pastel baby mint toy building blocks with soft clouds and hearts."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surf.fill((205, 240, 225))  # Soft baby mint base

    # Brick pattern
    for row_idx, y in enumerate(range(0, TEXTURE_SIZE, 16)):
        offset = 16 if row_idx % 2 == 1 else 0
        for x in range(offset - 16, TEXTURE_SIZE + 16, 32):
            rect = pygame.Rect(x + 1, y + 1, 30, 14)
            pygame.draw.rect(surf, (222, 248, 236), rect, border_radius=4)
            pygame.draw.rect(surf, (190, 230, 212), rect, width=1, border_radius=4)

    # Cute little fluffy white clouds
    for cx, cy in [(18, 24), (50, 40)]:
        pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy), 3)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 4, cy), 3)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy - 2), 4)

    return surf


def create_wall_texture_night() -> pygame.Surface:
    """Theme 1: Cute soft indigo night bricks with crescent moons and gold stars."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surf.fill((45, 48, 75))  # Soft indigo night base

    # Brick pattern
    for row_idx, y in enumerate(range(0, TEXTURE_SIZE, 16)):
        offset = 16 if row_idx % 2 == 1 else 0
        for x in range(offset - 16, TEXTURE_SIZE + 16, 32):
            rect = pygame.Rect(x + 1, y + 1, 30, 14)
            pygame.draw.rect(surf, (58, 62, 92), rect, border_radius=4)
            pygame.draw.rect(surf, (38, 40, 65), rect, width=1, border_radius=4)

    # Cute smiling golden crescent moons
    for mx, my in [(16, 24), (48, 40)]:
        pygame.draw.circle(surf, (255, 225, 120), (mx, my), 5)
        pygame.draw.circle(surf, (58, 62, 92), (mx + 2, my - 1), 4)

    # Cute gold twinkling stars
    for sx, sy in [(32, 10), (14, 50), (52, 12)]:
        pygame.draw.circle(surf, (255, 245, 180), (sx, sy), 2)

    return surf


def create_wall_texture_forest() -> pygame.Surface:
    """Theme 2: Cute pastel forest mint blocks with daisies and clovers."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surf.fill((190, 235, 210))  # Soft sage mint base

    # Wooden / toy plank pattern
    for row_idx, y in enumerate(range(0, TEXTURE_SIZE, 16)):
        offset = 16 if row_idx % 2 == 1 else 0
        for x in range(offset - 16, TEXTURE_SIZE + 16, 32):
            rect = pygame.Rect(x + 1, y + 1, 30, 14)
            pygame.draw.rect(surf, (210, 245, 225), rect, border_radius=4)
            pygame.draw.rect(surf, (170, 220, 195), rect, width=1, border_radius=4)

    # Cute little daisies (white petals with yellow center)
    for dx, dy in [(16, 24), (48, 40)]:
        for angle in (0, 1.57, 3.14, 4.71):
            px = int(dx + math.cos(angle) * 3)
            py = int(dy + math.sin(angle) * 3)
            pygame.draw.circle(surf, (255, 255, 255), (px, py), 2)
        pygame.draw.circle(surf, (255, 220, 100), (dx, dy), 2)

    # Cute 4-leaf clover
    for cx, cy in [(48, 12), (16, 52)]:
        pygame.draw.circle(surf, (130, 215, 160), (cx - 2, cy), 2)
        pygame.draw.circle(surf, (130, 215, 160), (cx + 2, cy), 2)
        pygame.draw.circle(surf, (130, 215, 160), (cx, cy - 2), 2)
        pygame.draw.circle(surf, (130, 215, 160), (cx, cy + 2), 2)

    return surf


def create_apple_sprite() -> pygame.Surface:
    """Kawaii baby apple/strawberry with smiling face, big shiny eyes and blushing cheeks."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    cx, cy = 32, 35
    radius = 21

    # Soft glowing pastel halo
    for r in range(radius + 8, radius, -2):
        alpha = int(75 * (1.0 - (r - radius) / 8.0))
        pygame.draw.circle(surf, (255, 180, 200, alpha), (cx, cy), r)

    # Cute round apple body (soft pastel raspberry pink)
    pygame.draw.circle(surf, (255, 125, 150), (cx, cy), radius)
    pygame.draw.circle(surf, (255, 150, 172), (cx - 2, cy - 2), radius - 3)
    pygame.draw.circle(surf, (255, 185, 202), (cx - 5, cy - 5), radius - 8)

    # Cute soft stem & mint leaf
    pygame.draw.line(surf, (175, 140, 120), (cx, cy - radius + 1), (cx + 2, cy - radius - 6), 3)
    leaf_pts = [(cx + 2, cy - radius - 5), (cx + 11, cy - radius - 10), (cx + 12, cy - radius - 2)]
    pygame.draw.polygon(surf, (140, 225, 170), leaf_pts)
    pygame.draw.polygon(surf, (195, 250, 215), [(cx + 3, cy - radius - 5), (cx + 9, cy - radius - 8), (cx + 10, cy - radius - 3)])

    # Big Kawaii Anime Eyes
    eye_y = cy - 2
    lx, rx = cx - 7, cx + 7

    for ex in (lx, rx):
        # Eye base (soft dark chocolate)
        pygame.draw.ellipse(surf, (60, 50, 55), (ex - 3, eye_y - 4, 7, 9))
        # Big shiny anime highlight
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, eye_y - 2), 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex + 1, eye_y + 2), 1)

    # Rosy Blushing Cheeks
    cheek_y = cy + 5
    pygame.draw.circle(surf, (255, 170, 185, 220), (cx - 11, cheek_y), 4)
    pygame.draw.circle(surf, (255, 170, 185, 220), (cx + 11, cheek_y), 4)

    # Sweet little smile
    pygame.draw.arc(surf, (60, 50, 55), (cx - 3, cy + 2, 6, 6), 3.14, 0, 2)

    return surf


def create_snake_segment_sprite() -> pygame.Surface:
    """Cute baby pastel mint candy sphere with rosy blush spots and soft reflections."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    cx, cy = 32, 36
    radius = 20

    # Soft glowing halo
    for r in range(radius + 6, radius, -2):
        alpha = int(60 * (1.0 - (r - radius) / 6.0))
        pygame.draw.circle(surf, (170, 235, 205, alpha), (cx, cy), r)

    # Pastel mint round body
    pygame.draw.circle(surf, (140, 218, 180), (cx, cy), radius)
    pygame.draw.circle(surf, (168, 232, 200), (cx - 2, cy - 2), radius - 3)
    pygame.draw.circle(surf, (198, 245, 222), (cx - 4, cy - 4), radius - 7)

    # Cute white shine reflection
    pygame.draw.circle(surf, (255, 255, 255), (cx - 7, cy - 7), 4)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 10), 2)

    # Little rosy blush freckles
    pygame.draw.circle(surf, (255, 185, 195, 190), (cx - 8, cy + 5), 3)
    pygame.draw.circle(surf, (255, 185, 195, 190), (cx + 8, cy + 5), 3)

    return surf


def create_snake_head_sprite() -> pygame.Surface:
    """Cute baby pastel mint snake head sprite for 3rd person chase camera."""
    surf = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE), pygame.SRCALPHA)
    cx, cy = 32, 34
    radius = 22

    # Glowing halo
    for r in range(radius + 6, radius, -2):
        alpha = int(50 * (1.0 - (r - radius) / 6.0))
        pygame.draw.circle(surf, (180, 240, 215, alpha), (cx, cy), r)

    # Pastel mint round head
    pygame.draw.circle(surf, (135, 218, 178), (cx, cy), radius)
    pygame.draw.circle(surf, (165, 232, 198), (cx - 2, cy - 2), radius - 3)
    pygame.draw.circle(surf, (195, 245, 220), (cx - 4, cy - 4), radius - 7)

    # Big cute anime eyes
    eye_y = cy - 4
    for ex in (cx - 8, cx + 8):
        pygame.draw.ellipse(surf, (55, 45, 52), (ex - 4, eye_y - 5, 8, 10))
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, eye_y - 3), 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex + 1, eye_y + 1), 1)

    # Blushing pink cheeks
    pygame.draw.circle(surf, (255, 175, 190, 220), (cx - 13, cy + 4), 5)
    pygame.draw.circle(surf, (255, 175, 190, 220), (cx + 13, cy + 4), 5)

    # Tiny cute pink tongue sticking out
    pygame.draw.ellipse(surf, (255, 140, 165), (cx - 3, cy + 12, 6, 8))

    return surf


def create_first_person_fangs() -> pygame.Surface:
    """Cute baby snake nose and blushing cheeks peek visible at bottom of screen in 1st person."""
    surf = pygame.Surface((180, 70), pygame.SRCALPHA)
    cx = 90
    cy = 60

    # Soft pastel mint head base
    pygame.draw.ellipse(surf, (145, 222, 185), (cx - 45, cy - 35, 90, 70))
    pygame.draw.ellipse(surf, (175, 238, 205), (cx - 40, cy - 32, 80, 58))

    # Cute rosy cheeks
    pygame.draw.circle(surf, (255, 175, 190, 210), (cx - 28, cy - 5), 8)
    pygame.draw.circle(surf, (255, 175, 190, 210), (cx + 28, cy - 5), 8)

    # Tiny cute pink tongue sticking out playfully
    pygame.draw.ellipse(surf, (255, 140, 165), (cx - 5, cy - 2, 10, 16))
    pygame.draw.line(surf, (230, 110, 135), (cx, cy - 2), (cx, cy + 10), 2)

    # Tiny cute nostrils
    pygame.draw.circle(surf, (110, 180, 150), (cx - 6, cy - 14), 2)
    pygame.draw.circle(surf, (110, 180, 150), (cx + 6, cy - 14), 2)

    return surf


def create_kawaii_faces() -> Dict[str, pygame.Surface]:
    """Kawaii Baby Snake animated face frames for HUD status bar."""
    faces = {}
    size = 48

    for name in ("center", "left", "right", "grin", "dead"):
        surf = pygame.Surface((size, size))
        surf.fill((255, 244, 248))  # Soft baby pink backdrop

        cx, cy = 24, 24
        radius = 18

        # Baby snake head (soft pastel mint)
        head_color = (150, 225, 188) if name != "dead" else (205, 220, 215)
        pygame.draw.circle(surf, head_color, (cx, cy), radius)
        pygame.draw.circle(surf, (180, 240, 210), (cx - 2, cy - 2), radius - 3)

        # Rosy blushing cheeks
        pygame.draw.circle(surf, (255, 180, 195, 220), (cx - 9, cy + 4), 4)
        pygame.draw.circle(surf, (255, 180, 195, 220), (cx + 9, cy + 4), 4)

        if name == "dead":
            # Cute anime crying face ( T ﹏ T ) with baby tears and little band-aid
            # Eyes closed crying lines
            pygame.draw.line(surf, (70, 75, 85), (cx - 10, cy - 3), (cx - 4, cy - 3), 2)
            pygame.draw.line(surf, (70, 75, 85), (cx + 4, cy - 3), (cx + 10, cy - 3), 2)
            # Anime teardrops
            pygame.draw.circle(surf, (130, 205, 255), (cx - 7, cy + 7), 3)
            pygame.draw.circle(surf, (130, 205, 255), (cx + 7, cy + 7), 3)
            # Wavy sad mouth
            pygame.draw.arc(surf, (70, 75, 85), (cx - 4, cy + 4, 8, 7), 0, 3.14, 2)
            # Little pastel band-aid on forehead
            pygame.draw.rect(surf, (255, 225, 185), (cx - 6, cy - 14, 12, 5), border_radius=2)
            pygame.draw.rect(surf, (255, 170, 160), (cx - 2, cy - 13, 4, 3))

        elif name == "grin":
            # Happy smiling eyes ( > ‿ < ) when eating apple
            # Left happy eye arc
            pygame.draw.arc(surf, (60, 50, 60), (cx - 10, cy - 6, 7, 8), 0, 3.14, 2)
            # Right happy eye arc
            pygame.draw.arc(surf, (60, 50, 60), (cx + 3, cy - 6, 7, 8), 0, 3.14, 2)
            # Open happy mouth with tongue
            pygame.draw.arc(surf, (60, 50, 60), (cx - 4, cy + 1, 8, 8), 3.14, 0, 2)
            pygame.draw.circle(surf, (255, 140, 165), (cx, cy + 5), 2)
            # Little floating heart on side
            pygame.draw.circle(surf, (255, 130, 160), (cx + 14, cy - 8), 2)

        else:
            # Big Innocent Kawaii Anime Eyes
            eye_y = cy - 2
            lx, rx = cx - 6, cx + 6
            pupil_off_x = 0
            if name == "left":
                pupil_off_x = -2
            elif name == "right":
                pupil_off_x = 2

            for ex in (lx, rx):
                # Big soft dark pupil
                pygame.draw.ellipse(surf, (55, 48, 55), (ex - 3, eye_y - 4, 7, 9))
                # Big anime sparkle highlights
                pygame.draw.circle(surf, (255, 255, 255), (ex - 1 + pupil_off_x, eye_y - 2), 2)
                pygame.draw.circle(surf, (255, 255, 255), (ex + 1 + pupil_off_x, eye_y + 2), 1)

            # Little sweet smile
            pygame.draw.arc(surf, (60, 50, 60), (cx - 3, cy + 4, 6, 5), 3.14, 0, 2)

        faces[name] = surf

    return faces


# Backwards compatibility alias
create_doom_faces = create_kawaii_faces


class TextureManager:
    """Caches surfaces and raw numpy pixel arrays for rapid raycasting."""

    def __init__(self):
        self.wall_candy = create_wall_texture_candy()
        self.wall_night = create_wall_texture_night()
        self.wall_forest = create_wall_texture_forest()
        self.wall_brick = create_wall_texture_blocks()

        # Backward compatibility
        self.wall_metal = self.wall_candy

        # 3 Cyclical Theme Wall Textures
        self.theme_walls = [self.wall_candy, self.wall_night, self.wall_forest]

        self.sprite_apple = create_apple_sprite()
        self.sprite_segment = create_snake_segment_sprite()
        self.sprite_snake_head = create_snake_head_sprite()
        self.fangs_overlay = create_first_person_fangs()
        self.kawaii_faces = create_kawaii_faces()
        self.doom_faces = self.kawaii_faces


# Backwards compatibility alias
KawaiiTextures = TextureManager
DoomTextures = TextureManager

