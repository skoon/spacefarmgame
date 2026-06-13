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
GREEN = (80, 220, 80)

SAVE_SLOT_COUNT = 3

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
        "schedule": [(0, 10, 10), (2, 10, 8), (4, 12, 10), (6, 10, 10)],
        "romanceable": True,
        "bio": "Runs the General Store. Friendly and always has a deal.",
        "likes": ["glowroot", "starlight_melon"],
        "loves": ["nebula_bloom"],
        "dialogues": {
            "intro": [
                "Welcome to Zara's General Store! Best prices this side of Andromeda.",
                "Just restocked the shelves. Take a look around!",
                "You're the new farmer, right? Welcome to the port!",
            ],
            "neutral": [
                "The soil's been feeling extra cosmic lately. Your crops should thrive!",
                "I got a shipment of rare crystals in. Not for sale, but nice to look at.",
                "You're making a name for yourself, farmer!",
                "Business is good. Space farmers spend more than miners!",
            ],
            "friendly": [
                "I love seeing new farmers try their hand at alien agriculture!",
                "You're my favorite customer! Don't tell the others, heh.",
                "The stars aligned when you landed on this planet!",
                "Come by anytime. I always have something interesting in stock.",
            ],
            "gift_like": "Oh, this is nice! I'll put it on the counter. Thank you!",
            "gift_love": "Wow, a nebula bloom! These are so rare! You're the sweetest!",
            "gift_neutral": "Thanks... I'll find a use for it.",
        },
    },
    {
        "id": "blip",
        "name": "Blip",
        "color": (100, 200, 255),
        "color2": (50, 150, 200),
        "species": "Floatan",
        "location": "bar",
        "schedule": [(0, 16, 10), (3, 14, 10), (5, 16, 10)],
        "romanceable": False,
        "bio": "Bartender at the Cosmic Comet. Makes the best nebula nectar.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": [
                "Hey there, space farmer! Welcome to the Cosmic Comet!",
                "First drink's on the house for all new arrivals!",
                "Pull up a chair and tell me your story!",
            ],
            "neutral": [
                "Rough day on the farm? We've got the galaxy's best glow-ale.",
                "I've been experimenting with new cocktails. Want to be my taste tester?",
                "Did you hear about the asteroid miners? They found a crystal the size of a ship!",
                "One part nebula dust, two parts starlight... perfect!",
            ],
            "friendly": [
                "You're becoming a regular! That calls for a drink on the house!",
                "Best customer in the galaxy! Well, top three at least!",
                "I'd give you the secret recipe, but then I'd have to space you.",
                "You know, you're alright. Most farmers don't have your spark.",
            ],
            "gift_like": "Hey, thanks! I'll add this to my collection!",
            "gift_love": "No way! Where did you find this?! This is incredible!",
            "gift_neutral": "Uh, thanks. I'll just put this over here.",
        },
    },
    {
        "id": "nova",
        "name": "Nova",
        "color": (220, 150, 255),
        "color2": (180, 80, 220),
        "species": "Lunari",
        "location": "house1",
        "schedule": [(0, 6, 17), (2, 8, 15), (4, 6, 17), (6, 4, 15)],
        "romanceable": True,
        "bio": "A retired space pilot who now tends a small garden. Stargazer at heart.",
        "likes": ["cosmic_wheat", "zargon_fruit"],
        "loves": ["starlight_melon"],
        "dialogues": {
            "intro": [
                "Oh, a new farmer? How lovely! I used to explore the stars too, you know.",
                "Welcome! I was just tending my garden. The soil here has a special glow.",
                "Another soul drawn to this little planet. The cosmos works in mysterious ways.",
            ],
            "neutral": [
                "The stars were especially bright last night. Did you see them?",
                "I've been charting a new constellation. I think it's shaped like a space cow!",
                "My garden is doing well this season. The alien worms are helping aerate the soil.",
                "I used to pilot freighters across the galaxy. Now I just watch the sky and miss it.",
            ],
            "friendly": [
                "You remind me of myself when I was young. Full of wonder and stardust.",
                "I look forward to our talks. Not many people understand a star-pilot's heart.",
                "The nebula is particularly beautiful tonight. I'd love to show you my favorite view.",
                "You have a good soul. I can sense it in the way you treat the land.",
            ],
            "gift_like": "Oh, how thoughtful! This will go great in my garden.",
            "gift_love": "A starlight melon! They remind me of my travels! You have no idea how much this means!",
            "gift_neutral": "Thanks. That's very kind of you.",
        },
    },
    {
        "id": "pip",
        "name": "Pip",
        "color": (150, 255, 150),
        "color2": (80, 200, 80),
        "species": "Spriggan",
        "location": "house2",
        "schedule": [(0, 13, 17), (1, 11, 15), (3, 13, 17), (5, 15, 15), (7, 13, 17)],
        "romanceable": False,
        "bio": "A young and energetic alien who loves helping on other people's farms.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": [
                "Hi hi hi! Are you the new farmer? I'm Pip! I love farming!",
                "Wow, a real farmer! Can I visit your farm? Please please please!",
                "I'm Pip! I'm gonna be the best farmer in the galaxy someday!",
            ],
            "neutral": [
                "I've been growing space flowers! They glow in the dark! Wanna see?",
                "I tried to grow a cosmic wheat plant in my room but it got too big!",
                "Do you think aliens eat the same food as us? Wait, I'm an alien. Nevermind!",
                "My plants are the happiest plants on the whole planet! I sing to them!",
            ],
            "friendly": [
                "You're my favorite farmer! Teach me everything!",
                "When I grow up, I want a farm just like yours! With bots and everything!",
                "I drew a picture of your farm! See, you're right there with a giant carrot!",
                "You're the coolest person on the whole planet! And I've met everyone!",
            ],
            "gift_like": "Ooh, a present! Thank you thank you thank you!",
            "gift_love": "THIS IS THE BEST DAY EVER!! I'm gonna treasure this forever!",
            "gift_neutral": "Hmm, okay! I'll take it!",
        },
    },
    {
        "id": "luna",
        "name": "Luna",
        "color": (255, 200, 255),
        "color2": (200, 100, 200),
        "species": "Ethereal",
        "location": "house3",
        "schedule": [(0, 20, 17), (2, 22, 15), (4, 20, 17), (6, 18, 12)],
        "romanceable": True,
        "bio": "A mystical being who communes with the cosmos. She tends a garden of starlight.",
        "likes": ["nebula_bloom", "glowroot"],
        "loves": ["quasar_berry"],
        "dialogues": {
            "intro": [
                "I sensed you would come. The cosmos has brought a new gardener to our little world.",
                "Your aura shimmers with potential. I've been expecting you.",
                "Welcome, traveler. The stars whispered your name to me last night.",
            ],
            "neutral": [
                "The plants whisper to me. They say you have a kind touch.",
                "I meditated under the triple moons last night. The energy was intense.",
                "There is a storm in the nebula. Can you feel it? It will pass by morning.",
                "The cosmic currents are shifting. Your crops will feel it too.",
            ],
            "friendly": [
                "Your energy is beautiful. Like a warm nebula on a quiet night.",
                "I see great things in your future. A harvest unlike any this planet has seen.",
                "When you're near, the plants sing a little louder. They adore you.",
                "Our souls resonate on the same frequency. It is... pleasant.",
            ],
            "gift_like": "I accept this gift with gratitude. It will serve a purpose.",
            "gift_love": "A quasar berry! The energy radiates perfectly. You understand me.",
            "gift_neutral": "I receive this. It carries your energy.",
        },
    },
    {
        "id": "rex",
        "name": "Rex",
        "color": (200, 180, 140),
        "color2": (160, 140, 100),
        "species": "Terrus",
        "location": "house4",
        "schedule": [(0, 26, 17), (2, 24, 15), (4, 26, 17), (6, 28, 15)],
        "romanceable": False,
        "bio": "Old-timer who's been farming on this planet for 50 cycles. Seen it all.",
        "likes": [],
        "loves": [],
        "dialogues": {
            "intro": [
                "Hmph. New farmer, huh? This planet'll test you. But it's worth it.",
                "Another one chasing the farming dream. You've got grit, I'll give you that.",
                "I've seen a hundred farmers come and go. You might last longer than most.",
            ],
            "neutral": [
                "Back in my day, we had to scare off void-beasts with our bare hands!",
                "The soil used to be richer before the spaceport expanded. Still good, though.",
                "I don't trust those fancy bots. A real farmer uses their own two hands!",
                "You ever try farming during a meteor shower? Now THAT is an experience.",
            ],
            "friendly": [
                "You're doing alright, kid. The planet likes you.",
                "Alright, I'll admit it. You're not half bad at this farming thing.",
                "I've been watching your progress. You've got the touch. Don't waste it.",
                "If you ever need advice, come find me. I've forgotten more than most know.",
            ],
            "gift_like": "Huh. Thanks. I'll put it with my other stuff.",
            "gift_love": "Now THIS is quality! You've got good taste, kid!",
            "gift_neutral": "Eh, it's alright. Not my thing but I appreciate the thought.",
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

SHIP_TIERS = [
    {"name": "Scout Pod",     "fuel_capacity": 50,  "cargo_capacity": 4,  "cost": 0},
    {"name": "Hauler MK2",    "fuel_capacity": 120, "cargo_capacity": 10, "cost": 2000},
    {"name": "Star Cruiser",  "fuel_capacity": 300, "cargo_capacity": 20, "cost": 8000},
]

PLANETS = [
    {"name": "Xylos Prime", "desc": "Crystal caves with glowing gems",  "fuel_cost": 15, "color": (180, 100, 255), "finds": ["Glowroot Seeds", "Nebula Seeds"]},
    {"name": "Magma-7",     "desc": "Volcanic world of fire and ash",   "fuel_cost": 25, "color": (255, 80, 80),   "finds": ["Zargon Seeds", "Berry Seeds"]},
    {"name": "Aquaris",     "desc": "Endless ocean under alien suns",   "fuel_cost": 10, "color": (60, 150, 255),  "finds": ["Cosmic Wheat Seeds", "Melon Seeds"]},
    {"name": "Verdantia",   "desc": "Lush jungle with alien flora",    "fuel_cost": 20, "color": (80, 220, 100),  "finds": ["Nebula Seeds", "Starlight Melon Seeds"]},
]

PLANET_EXCLUSIVE_SEEDS = {
    "Xylos Prime": ["Starlight Melon Seeds"],
    "Magma-7":     ["Quasar Berry Seeds"],
    "Aquaris":     ["Nebula Seeds"],
    "Verdantia":   ["Zargon Seeds"],
}

SEASONS = ["Nebula", "Void", "Bloom", "Solar"]
SEASON_DAY_LENGTH = 14

WEATHER_EVENTS = [
    {"name": "Clear",       "crop_bonus": 0,   "energy_cost": 0,  "color": None},
    {"name": "Meteor Shower","crop_bonus": 0.5,"energy_cost": 0,  "color": (255, 200, 100)},
    {"name": "Solar Flare", "crop_bonus": 0.25,"energy_cost": 15,"color": (255, 100, 50)},
    {"name": "Alien Rain",  "crop_bonus": 0,   "energy_cost": 0,  "color": (100, 150, 255)},
    {"name": "Void Fog",    "crop_bonus": -0.5,"energy_cost": 5,  "color": (80, 60, 100)},
]

SEASONAL_MODIFIERS = {
    "Nebula": {"weather_weights": [30, 20, 10, 30, 10], "growth_mod": 1.5,  "sky_tint": (200, 180, 255)},
    "Void":   {"weather_weights": [20, 10, 5,  20, 45], "growth_mod": 0.5,  "sky_tint": (60, 60, 80)},
    "Bloom":  {"weather_weights": [40, 15, 25, 15, 5],  "growth_mod": 1.25, "sky_tint": (180, 255, 200)},
    "Solar":  {"weather_weights": [25, 10, 45, 10, 10], "growth_mod": 1.0,  "sky_tint": (255, 230, 150)},
}

WEATHER_DURATION = {"min": 2, "max": 4}

FESTIVALS = {
    "nebula": {
        "name": "Harvest Moon Feast",
        "season": "Nebula",
        "day": 7,
        "type": "crop_tasting",
        "reward_item": "Nebula Seeds",
        "reward_gold": 500,
    },
    "bloom": {
        "name": "Alien Flower Show",
        "season": "Bloom",
        "day": 7,
        "type": "flower_arrange",
        "reward_item": "Starlight Melon Seeds",
        "reward_gold": 300,
    },
    "solar": {
        "name": "Starlight Dance",
        "season": "Solar",
        "day": 10,
        "type": "rhythm",
        "reward_item": "Quasar Berry Seeds",
        "reward_gold": 200,
    },
}

BAR_ITEMS = [
    {"name": "Nebula Nectar", "price": 15, "energy": 20, "color": (180, 100, 255)},
    {"name": "Glow-Ale",      "price": 10, "energy": 10, "color": (100, 220, 100)},
    {"name": "Cosmic Coffee", "price": 20, "energy": 30, "color": (80, 60, 30)},
    {"name": "Alien Snacks",  "price": 8,  "energy": 5,  "color": (255, 200, 80)},
]
