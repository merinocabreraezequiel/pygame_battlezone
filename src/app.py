import pygame
import json
import sys
import os
import random

class Game:
    def __init__(self, config):
        pygame.init()
        self._config_data(config)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(config["title"])
        self.clock = pygame.time.Clock()
        self.running = True

        self.horizon_line = self.height // 2
        self.mountains = self._generate_mountains()

    def _config_data(self, _config):
        self.config = _config
        self.width = _config.get("width",800)
        self.height = _config.get("height",600)
        self.bg_color = tuple(_config.get("background_color", [0, 0, 0]))
        self.line_color = tuple(_config.get("line_color", [0, 255, 0]))
        self.fps = _config.get("fps", 60)
        self.background_spacing = _config.get("background_spacing", 40)
        self.max_mountains = _config.get("max_mountains", 8)

    def _generate_mountains(self):
        max_height = self.horizon_line // 3
        min_width = 60
        max_width = 150

        mountains = []
        x = 0
        count = 0

        while count < self.max_mountains and x < self.width:
            # Espacio opcional antes de la montaña
            x += random.randint(10, 40)

            # Ancho aleatorio de la montaña
            width = random.randint(min_width, max_width)
            if x + width > self.width:
                break  # No cabe, salimos

            peak_x = x + width // 2
            peak_y = self.horizon_line - random.randint(20, max_height)

            mountains.append((x, self.horizon_line))              # base izquierda
            mountains.append((peak_x, peak_y))                 # pico
            mountains.append((x + width, self.horizon_line))      # base derecha

            x += width + random.randint(10, 30)  # espacio después
            count += 1

        return mountains



    def draw_ground(self):
        for x in range(-self.width, self.width * 2, self.background_spacing):
            pygame.draw.line(self.screen, self.line_color, (x, self.height), (x + self.width, self.height // 2), 1)
        for y in range(self.height // 2, self.height, self.background_spacing):
            pygame.draw.line(self.screen, self.line_color, (0, y), (self.width, y), 1)

    def draw_mountains(self):
#        points = [
#            (100, self.height // 2),
#            (200, 300),
#            (300, self.height // 2),
#            (400, 250),
#            (500, self.height // 2),
#            (600, 280),
#            (700, self.height // 2),
#        ]
#        pygame.draw.lines(self.screen, self.line_color, False, points, 1)
        for i in range(0, len(self.mountains), 3):
            pygame.draw.polygon(self.screen, self.line_color, self.mountains[i:i+3], 1)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(self.bg_color)
            self.draw_ground()
            self.draw_mountains()
            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()

def load_config(path="config.json"):
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo de configuración {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()
    game = Game(config)
    game.run()
