# Screen configuration
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Pixel Clash"

# Design Palette
BACKGROUND_COLOR = (30, 30, 30)   
WALL_COLOR = (70, 75, 90)         
PLAYER_COLOR = (0, 200, 255)      
DUMMY_COLOR = (255, 100, 100)     # Red for target dummy
BULLET_COLOR = (255, 215, 0)      
CROSSHAIR_COLOR = (255, 80, 80)   
UI_COLOR = (255, 255, 255)        # White text

# Player Specifications
PLAYER_SIZE = 40
PLAYER_SPEED = 400
MAX_HEALTH = 100
BULLET_DAMAGE = 20

# Dash Tuning
DASH_SPEED_MULTIPLIER = 3.0       # Dynamic burst acceleration
DASH_DURATION = 0.15              # How long the speed burst lasts (seconds)
DASH_COOLDOWN = 3.0               # Recovery time between dashes

# Weapon Tuning Configuration
FIRE_COOLDOWN = 0.2               
BULLET_SPEED = 800                
BULLET_SIZE = 8                   
BULLET_LIFETIME = 2.0             

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
