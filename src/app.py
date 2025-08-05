import pygame
import json
import sys
import os
import random
import math

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

        #Inicialización del jugador
        self.pos = [0.0, 0.0]
        self.angle = 0.0
        self.speed = 2.0
        self.turn_speed = 2.5

    def _config_data(self, _config):
        self.config = _config
        self.debug = _config.get("debug", False)
        self.width = _config.get("width",800)
        self.height = _config.get("height",600)
        self.bg_color = tuple(_config.get("background_color", [0, 0, 0]))
        self.line_color = tuple(_config.get("line_color", [0, 255, 0]))
        self.fps = _config.get("fps", 60)
        self.background_spacing = _config.get("background_spacing", 40)
        self.max_mountains = _config.get("max_mountains", 8)
        self.mountains_min_width = _config.get("mountains_min_width", 60)
        self.mountains_max_width = _config.get("mountains_max_width", 150)

    def _generate_mountains(self):
        mountains = []
        for _ in range(self.max_mountains):
            depth = random.randint(100, 600)  # distancia hacia adelante (eje Y)
            width = random.randint(self.mountains_min_width, self.mountains_max_width)
            height = random.randint(40, int(self.horizon_line * 0.33))  # altura real visual

            x = random.randint(-500, 500)
            peak_x = x + width // 2

            # OJO: aquí la altura se representa con coordenadas más ALTAS en pantalla (menor Y)
            base_y = depth
            peak_y = depth  # misma profundidad que la base, pero se elevará visualmente

            # Guardamos altura visual por separado
            mountains.append(((x, base_y), (peak_x, peak_y), (x + width, base_y), height))

        return mountains



    def _world_to_player_view(self, x, y):
        dx = x - self.pos[0]
        dy = y - self.pos[1]
        rad = math.radians(-self.angle)
        view_x = dx * math.cos(rad) - dy * math.sin(rad)
        view_y = dx * math.sin(rad) + dy * math.cos(rad)
        return view_x, view_y

    def _project_point(self, x, y):
        if y <= 1:
            return None
        scale = 300 / y
        screen_x = int(self.width / 2 + x * scale)
        screen_y = int(self.horizon_line + scale * -1)
        if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
            return screen_x, screen_y
        return None

    def draw_ground(self):
        spacing = self.background_spacing
        ground_lines = []

        for x in range(-1000, 1000, spacing):
            for y in range(0, 1000, spacing):
                # Posición en el mundo
                world_start = (x, y)
                world_end = (x + spacing, y)

                # Transformar al sistema de coordenadas del jugador
                start = self._world_to_player_view(*world_start)
                end = self._world_to_player_view(*world_end)

                # Proyección simple (sin 3D real)
                screen_start = self._project_point(*start)
                screen_end = self._project_point(*end)

                if screen_start and screen_end:
                    pygame.draw.line(self.screen, self.line_color, screen_start, screen_end, 1)

    def draw_mountains(self):
        for base1, peak, base2, height in self.mountains:
            # Transformar las 3 posiciones al sistema del jugador
            p1 = self._world_to_player_view(*base1)
            p2 = self._world_to_player_view(*peak)
            p3 = self._world_to_player_view(*base2)

            # Proyectar en pantalla
            s1 = self._project_point(*p1)
            s2 = self._project_point(*p2)
            s3 = self._project_point(*p3)

            if s1 and s2 and s3:
                # Elevar el pico restando la altura (en píxeles)
                s2 = (s2[0], s2[1] - height)
                pygame.draw.polygon(self.screen, self.line_color, [s1, s2, s3], 1)
                if self.debug:
                    print(f"Mountain world coords: {p1}, {p2}, {p3}")
                    print(f"Screen coords: {s1}, {s2}, {s3}")

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.angle -= self.turn_speed
            if self.debug: print(f"Turning left: {self.angle} degrees")
        if keys[pygame.K_d]:
            self.angle += self.turn_speed
            if self.debug: print(f"Turning left: {self.angle} degrees")
        if keys[pygame.K_w]:
            rad = math.radians(self.angle)
            self.pos[0] += math.cos(rad) * self.speed
            self.pos[1] += math.sin(rad) * self.speed
            if self.debug: print(f"Moving forward: {self.pos[0]}, {self.pos[1]}")
        if keys[pygame.K_s]:
            rad = math.radians(self.angle)
            self.pos[0] -= math.cos(rad) * self.speed
            self.pos[1] -= math.sin(rad) * self.speed
            if self.debug: print(f"Moving backward: {self.pos[0]}, {self.pos[1]}")


    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()

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
