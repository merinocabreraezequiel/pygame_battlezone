import pygame
import json
import sys
import os

class Game:
    def __init__(self, config):
        pygame.init()
        self._config_data(config)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(config["title"])
        self.clock = pygame.time.Clock()
        self.running = True

    def _config_data(self, _config):
        self.config = _config
        self.width = _config.get("width",800)
        self.height = _config.get("height",600)
        self.bg_color = tuple(_config.get("background_color", [0, 0, 0]))
        self.line_color = tuple(_config.get("line_color", [0, 255, 0]))
        self.fps = _config.get("fps", 60)
        self.background_spacing = _config.get("background_spacing", 40)
    
    def draw_ground(self):
        for x in range(-self.width, self.width * 2, self.background_spacing):
            pygame.draw.line(self.screen, self.line_color, (x, self.height), (x + self.width, self.height // 2), 1)
        for y in range(self.height // 2, self.height, self.background_spacing):
            pygame.draw.line(self.screen, self.line_color, (0, y), (self.width, y), 1)

    def draw_mountains(self):
        points = [
            (100, self.height // 2),
            (200, 300),
            (300, self.height // 2),
            (400, 250),
            (500, self.height // 2),
            (600, 280),
            (700, self.height // 2),
        ]
        pygame.draw.lines(self.screen, self.line_color, False, points, 1)

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
