# Screen configuration
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Pixel Clash"

# Design Palette
BACKGROUND_COLOR = (30, 30, 30)   # Dark Charcoal
WALL_COLOR = (70, 75, 90)         # Steel Slate Grey
PLAYER_COLOR = (0, 200, 255)      # Cyan

# Player Specifications
PLAYER_SIZE = 40
PLAYER_SPEED = 400

# Fixed Map Spawn Positions (Vector indices for multi-player staging)
SPAWN_POINTS = [
    (100, 100),    # Top Left (Spawn A)
    (1140, 100),   # Top Right (Spawn B)
    (100, 580),    # Bottom Left (Spawn C)
    (1140, 580)    # Bottom Right (Spawn D)
]

# Static Arena Geometry Layout: (x, y, width, height)
# 4 Border walls + 8 strategic internal cover blocks
WALL_LAYOUTS = [
    # ─── OUTER ARENA BOUNDARIES ───
    (0, 0, WIDTH, 20),               # Top Border
    (0, HEIGHT - 20, WIDTH, 20),     # Bottom Border
    (0, 0, 20, HEIGHT),              # Left Border
    (WIDTH - 20, 0, 20, HEIGHT),     # Right Border

    # ─── INTERNAL TACTICAL COVER ───
    (300, 150, 200, 40),             # Top-Left Horizontal Barrier
    (780, 150, 200, 40),             # Top-Right Horizontal Barrier
    (300, 530, 200, 40),             # Bottom-Left Horizontal Barrier
    (780, 530, 200, 40),             # Bottom-Right Horizontal Barrier
    (200, 280, 40, 160),             # Left Flank Vertical Post
    (1040, 280, 40, 160),            # Right Flank Vertical Post
    (540, 335, 200, 50),             # Center Objective Centerpiece
    (615, 240, 50, 240)              # Central Vertical Pillar Split
]
