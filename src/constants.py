# Screen configuration
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Pixel Clash"

# Design Palette
BACKGROUND_COLOR = (30, 30, 30)   
WALL_COLOR = (70, 75, 90)         
PLAYER_COLOR = (0, 200, 255)      
DUMMY_COLOR = (255, 100, 100)     
BULLET_COLOR = (255, 215, 0)      
CROSSHAIR_COLOR = (255, 80, 80)   
UI_COLOR = (255, 255, 255)        
CRATE_COLOR = (139, 69, 19)        # Saddle Brown
GRENADE_COLOR = (34, 139, 34)      # Forest Green
EXPLOSION_COLOR = (255, 69, 0)     # Red-Orange

# Pickup Colors
PICKUP_COLORS = {
    "HEALTH": (50, 205, 50),       # Lime Green
    "SPEED": (255, 165, 0),        # Orange
    "SHIELD": (30, 144, 255),      # Dodger Blue
    "DAMAGE": (220, 20, 60)        # Crimson
}

# Player & Gameplay Specifications
PLAYER_SIZE = 40
PLAYER_SPEED = 400
MAX_HEALTH = 100
BULLET_SIZE = 8

# Fixed Map Spawn Positions
SPAWN_POINTS = [
    (100, 100),    
    (1140, 100),   
    (100, 580),    
    (1140, 580)    
]

# Static Arena Geometry Layout
WALL_LAYOUTS = [
    (0, 0, WIDTH, 20),               
    (0, HEIGHT - 20, WIDTH, 20),     
    (0, 0, 20, HEIGHT),              
    (WIDTH - 20, 0, 20, HEIGHT),     
    (300, 150, 200, 40),             
    (780, 150, 200, 40),             
    (300, 530, 200, 40),             
    (780, 530, 200, 40),             
    (200, 280, 40, 160),             
    (1040, 280, 40, 160),            
    (540, 335, 200, 50),             
    (615, 240, 50, 240)              
]

# Destructible Crate Coordinates: (x, y)
CRATE_LAYOUTS = [
    (400, 250), (450, 250),
    (830, 250), (780, 250),
    (400, 430), (450, 430),
    (830, 430), (780, 430)
]
CRATE_SIZE = 40

# Authoritative Weapon Profiles
WEAPON_PROFILES = {
    1: {"name": "Pistol", "damage": 20, "fire_rate": 0.25, "max_ammo": 12, "reload_time": 1.5, "bullet_speed": 800, "spread": 0},
    2: {"name": "SMG",    "damage": 10, "fire_rate": 0.08, "max_ammo": 30, "reload_time": 2.0, "bullet_speed": 950, "spread": 0},
    3: {"name": "Shotgun","damage": 12, "fire_rate": 0.80, "max_ammo": 5,  "reload_time": 2.5, "bullet_speed": 700, "spread": 15}
}
