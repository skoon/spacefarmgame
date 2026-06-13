SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
TILE_SIZE = 32
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
SOIL_BROWN = (120, 80, 40)
WATER_BLUE = (60, 100, 180)
GRASS_GREEN = (60, 140, 60)
DARK_GREEN = (30, 100, 30)
SKY_BLUE = (100, 140, 200)
NIGHT_BLUE = (20, 20, 60)
SUNSET_ORANGE = (220, 140, 60)
GOLD = (255, 215, 0)
RED = (200, 50, 50)
PINK = (255, 150, 200)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
SUIT_WHITE = (220, 225, 230)
HELMET_LIGHT = (200, 210, 220)
VISOR_BLUE = (80, 180, 255)
ENERGY_GREEN = (100, 255, 100)

TILLABLE_ROWS = 10
TILLABLE_COLS = 14
FARM_TILES_OFFSET_X = 2
FARM_TILES_OFFSET_Y = 5

CROP_TYPES = {
    "glowroot": {
        "name": "Glowroot",
        "seed_price": 10,
        "sell_price": 30,
        "growth_stages": 3,
        "growth_time": 2,
        "color": (100, 220, 100),
        "desc": "A bioluminescent root vegetable",
        "seed_name": "Glowroot Seeds",
    },
    "zargon_fruit": {
        "name": "Zargon Fruit",
        "seed_price": 25,
        "sell_price": 75,
        "growth_stages": 4,
        "growth_time": 4,
        "color": (180, 60, 220),
        "desc": "A sweet purple alien fruit",
        "seed_name": "Zargon Seeds",
    },
    "cosmic_wheat": {
        "name": "Cosmic Wheat",
        "seed_price": 15,
        "sell_price": 50,
        "growth_stages": 3,
        "growth_time": 3,
        "color": (255, 220, 80),
        "desc": "Golden grain that sparkles",
        "seed_name": "Cosmic Wheat Seeds",
    },
    "starlight_melon": {
        "name": "Starlight Melon",
        "seed_price": 50,
        "sell_price": 150,
        "growth_stages": 5,
        "growth_time": 6,
        "color": (80, 180, 255),
        "desc": "A melon that tastes like starlight",
        "seed_name": "Melon Seeds",
    },
    "nebula_bloom": {
        "name": "Nebula Bloom",
        "seed_price": 40,
        "sell_price": 120,
        "growth_stages": 4,
        "growth_time": 5,
        "color": (255, 100, 200),
        "desc": "A beautiful cosmic flower",
        "seed_name": "Nebula Seeds",
    },
    "quasar_berry": {
        "name": "Quasar Berry",
        "seed_price": 30,
        "sell_price": 40,
        "growth_stages": 4,
        "growth_time": 3,
        "color": (255, 80, 50),
        "desc": "Regrowing berries of pure energy",
        "seed_name": "Berry Seeds",
        "regrows": True,
    },
}

CROP_ORDER = ["glowroot", "zargon_fruit", "cosmic_wheat", "starlight_melon", "nebula_bloom", "quasar_berry"]

NPC_DEFS = [
    {
        "id": "zara",
        "name": "Zara",
        "color": (255, 180, 100),
        "color2": (200, 100, 50),
        "species": "Zenorian",
        "location": "shop",
        "schedule": ["shop"],
        "romanceable": True,
        "bio": "Runs the General Store. Friendly and always has a deal.",
        "likes": ["glowroot", "starlight_melon"],
        "loves": ["nebula_bloom"],
        "dialogues": {
            "intro": "Welcome to Zara's General Store! Best prices this side of Andromeda.",
            "neutral": "The soil's been feeling extra cosmic lately. Your crops should thrive!",
            "friendly": "I love seeing new farmers try their hand at alien agriculture!",
        },
    },
    {
        "id": "blip",
        "name": "Blip",
        "color": (100, 200, 255),
        "color2": (50, 150, 200),
        "species": "Floatan",
        "location": "bar",
        "schedule": ["bar"],
        "romanceable": False,
        "bio": "Bartender at the Cosmic Comet. Makes the best nebula nectar.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": "Hey there, space farmer! Welcome to the Cosmic Comet!",
            "neutral": "Rough day on the farm? We've got the galaxy's best glow-ale.",
            "friendly": "You're becoming a regular! That calls for a drink on the house!",
        },
    },
    {
        "id": "nova",
        "name": "Nova",
        "color": (220, 150, 255),
        "color2": (180, 80, 220),
        "species": "Lunari",
        "location": "house1",
        "schedule": ["house1"],
        "romanceable": True,
        "bio": "A retired space pilot who now tends a small garden. Stargazer at heart.",
        "likes": ["cosmic_wheat", "zargon_fruit"],
        "loves": ["starlight_melon"],
        "dialogues": {
            "intro": "Oh, a new farmer? How lovely! I used to explore the stars, now I watch them from my window.",
            "neutral": "The stars were especially bright last night. Did you see them?",
            "friendly": "You remind me of myself when I was young. Full of wonder and stardust.",
        },
    },
    {
        "id": "pip",
        "name": "Pip",
        "color": (150, 255, 150),
        "color2": (80, 200, 80),
        "species": "Spriggan",
        "location": "house2",
        "schedule": ["house2"],
        "romanceable": False,
        "bio": "A young and energetic alien who loves helping on other people's farms.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": "Hi hi hi! Are you the new farmer? I'm Pip! I love farming!",
            "neutral": "I've been growing space flowers! They glow in the dark! Wanna see?",
            "friendly": "You're my favorite farmer! Teach me everything!",
        },
    },
    {
        "id": "luna",
        "name": "Luna",
        "color": (255, 200, 255),
        "color2": (200, 100, 200),
        "species": "Ethereal",
        "location": "house3",
        "schedule": ["house3"],
        "romanceable": True,
        "bio": "A mystical being who communes with the cosmos. She tends a garden of starlight.",
        "likes": ["nebula_bloom", "glowroot"],
        "loves": ["quasar_berry"],
        "dialogues": {
            "intro": "I sensed you would come. The cosmos has brought a new gardener to our little world.",
            "neutral": "The plants whisper to me. They say you have a kind touch.",
            "friendly": "Your energy is beautiful. Like a warm nebula on a quiet night.",
        },
    },
    {
        "id": "rex",
        "name": "Rex",
        "color": (200, 180, 140),
        "color2": (160, 140, 100),
        "species": "Terrus",
        "location": "house4",
        "schedule": ["house4"],
        "romanceable": False,
        "bio": "Old-timer who's been farming on this planet for 50 cycles. Seen it all.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": "Hmph. New farmer, huh? This planet'll test you. But it's worth it.",
            "neutral": "Back in my day, we had to scare off void-beasts with our bare hands!",
            "friendly": "You're doing alright, kid. The planet likes you.",
        },
    },
]

TIME_NAMES = ["Dawn", "Morning", "Midday", "Afternoon", "Evening", "Sunset", "Dusk", "Night"]

FARM_TILES_X = 30
FARM_TILES_Y = 20
SPACEPORT_TILES_X = 30
SPACEPORT_TILES_Y = 20

BOT_TYPES = {
    "water_bot": {
        "name": "Water-Bot",
        "action": "water",
        "range": 2,
        "cost": 300,
        "upkeep": 2,
        "color": (80, 180, 255),
    },
    "sprout_bot": {
        "name": "Sprout-Bot",
        "action": "water",
        "range": 3,
        "cost": 500,
        "upkeep": 5,
        "color": (100, 200, 255),
    },
    "harvest_bot": {
        "name": "Harvest-Bot",
        "action": "harvest",
        "range": 2,
        "cost": 1200,
        "upkeep": 10,
        "color": (255, 200, 100),
    },
}
