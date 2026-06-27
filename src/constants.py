# Screen configuration
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Pixel Clash"

# Design Palette
BACKGROUND_COLOR = (30, 30, 30)   
WALL_COLOR = (70, 75, 90)         
PLAYER_COLOR = (0, 200, 255)      
BULLET_COLOR = (255, 215, 0)      # Gold Projectiles
CROSSHAIR_COLOR = (255, 80, 80)   # Light Red Crosshair

# Player Specifications
PLAYER_SIZE = 40
PLAYER_SPEED = 400

# Weapon Tuning Configuration
FIRE_COOLDOWN = 0.2               # Minimum seconds between shots
BULLET_SPEED = 800                # Pixels per second
BULLET_SIZE = 8                   # Bounding box size
BULLET_LIFETIME = 2.0             # Max seconds before despawning

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
