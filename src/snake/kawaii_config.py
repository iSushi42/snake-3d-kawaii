"""Configuration and metrics for Kawaii Baby 3D Snake."""

from enum import Enum
import math

# Display & Resolution
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 170
SCALE_FACTOR = 3

SCREEN_WIDTH = INTERNAL_WIDTH * SCALE_FACTOR          # 960
VIEWPORT_HEIGHT = INTERNAL_HEIGHT * SCALE_FACTOR      # 510
STATUS_BAR_HEIGHT = 90
SCREEN_HEIGHT = VIEWPORT_HEIGHT + STATUS_BAR_HEIGHT   # 600

# Raycasting Settings
FOV = math.pi / 3  # 60 degrees Field of View
HALF_FOV = FOV / 2
NUM_RAYS = INTERNAL_WIDTH
DELTA_ANGLE = FOV / NUM_RAYS
DIST_TO_PROJ_PLANE = (INTERNAL_WIDTH / 2) / math.tan(HALF_FOV)
MAX_DEPTH = 24.0

# Map Settings
MAP_WIDTH = 16
MAP_HEIGHT = 16

# Gameplay Speeds
KAWAII_BASE_SPEED = 3.8       # Grid units per second
KAWAII_SPEED_INCREMENT = 0.55 # Added per 5 points
KAWAII_MAX_SPEED = 12.0

DOOM_BASE_SPEED = KAWAII_BASE_SPEED
DOOM_SPEED_INCREMENT = KAWAII_SPEED_INCREMENT
DOOM_MAX_SPEED = KAWAII_MAX_SPEED

# Time Attack Settings
TIME_ATTACK_START_SECONDS = 10.0
TIME_ATTACK_BONUS_PER_APPLE = 5.0
TIME_ATTACK_MAX_SECONDS = 60.0

# Cute & Kawaii Pastel Baby Color Palette
COLOR_CEILING = (235, 240, 253)       # Soft baby blue / lavender sky
COLOR_FLOOR = (254, 247, 240)         # Warm vanilla baby cream floor
COLOR_FOG = (248, 238, 246)           # Dreamy pastel marshmallow haze

COLOR_STATUS_BAR_BG = (255, 243, 247)     # Baby pink / cream status bar
COLOR_STATUS_BAR_BORDER = (245, 215, 225) # Soft pastel rose border
COLOR_STATUS_BAR_INNER = (255, 255, 255)  # Clean white pill card
COLOR_LED_RED = (255, 115, 145)           # Soft sweet strawberry pink
COLOR_LED_AMBER = (255, 165, 95)          # Soft baby peach
COLOR_LED_GREEN = (90, 205, 155)          # Soft baby mint
COLOR_TEXT_MAIN = (85, 80, 95)            # Soft dark plum text
COLOR_TEXT_MUTED = (165, 160, 180)        # Lavender gray text


class ViewMode(Enum):
    FIRST_PERSON = 1
    CHASE_CAM = 2


class GameMode(Enum):
    CLASSIC = "Classique"
    TIME_ATTACK = "Chrono"


# 3 Cyclical Kawaii Themes (changes every 5 points)
THEMES = [
    {
        "name": "Guimauve",
        "ceiling": (235, 242, 255),
        "floor": (254, 247, 240),
        "floor_alt": (240, 226, 235),
        "fog": (248, 238, 246),
        "wall_id": 0,
    },
    {
        "name": "Nuit Etoilee",
        "ceiling": (40, 42, 68),
        "floor": (72, 68, 102),
        "floor_alt": (48, 45, 72),
        "fog": (52, 54, 80),
        "wall_id": 1,
    },
    {
        "name": "Foret Feerique",
        "ceiling": (255, 236, 230),
        "floor": (226, 248, 228),
        "floor_alt": (195, 226, 202),
        "fog": (232, 248, 236),
        "wall_id": 2,
    },
]

