import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class WorldSimMixin:
    def add_particles(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append({
                "x": x, "y": y,
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-3, -1),
                "life": random.randint(15, 30),
                "max_life": 30,
                "color": color,
                "size": random.randint(2, 4),
            })

    def update_particles(self):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.1
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def update_weather_particles(self):
        weather = self.current_weather["name"]
        if weather == "Alien Rain":
            if random.random() < 0.3:
                self.weather_particles.append({
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": -10,
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(4, 7),
                    "life": random.randint(30, 60),
                    "max_life": 60,
                    "color": (100, 150, 255),
                    "size": random.randint(1, 3),
                })
        elif weather == "Meteor Shower":
            if random.random() < 0.05:
                start_x = random.randint(0, SCREEN_WIDTH)
                self.weather_particles.append({
                    "x": start_x,
                    "y": -20,
                    "vx": random.uniform(2, 4),
                    "vy": random.uniform(3, 6),
                    "life": random.randint(20, 40),
                    "max_life": 40,
                    "color": (255, 220, 100),
                    "size": random.randint(2, 4),
                })
        elif weather == "Void Fog":
            if random.random() < 0.15:
                self.weather_particles.append({
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": random.randint(0, SCREEN_HEIGHT // 2),
                    "vx": random.uniform(0.3, 1.0),
                    "vy": random.uniform(-0.2, 0.2),
                    "life": random.randint(60, 120),
                    "max_life": 120,
                    "color": (80, 60, 100),
                    "size": random.randint(8, 20),
                })
        for p in self.weather_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0 or p["y"] > SCREEN_HEIGHT + 20:
                self.weather_particles.remove(p)

    def update_weather(self):
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            weights = SEASONAL_MODIFIERS[SEASONS[self.season_index]]["weather_weights"]
            self.current_weather = random.choices(WEATHER_EVENTS, weights=weights)[0]
            self.weather_timer = random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"])
        self.weather_particles = []

    def update_season(self):
        self.day_in_season += 1
        if self.day_in_season >= SEASON_DAY_LENGTH:
            self.day_in_season = 0
            self.season_index = (self.season_index + 1) % len(SEASONS)
            self.set_message(f"Welcome to {SEASONS[self.season_index]} Season!")
