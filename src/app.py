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
        radius_min = 100
        radius_max = 1000

        for _ in range(self.max_mountains):
            angle_deg = random.uniform(0, 360)
            angle_rad = math.radians(angle_deg)

            dist = random.randint(radius_min, radius_max)

            base_x = math.cos(angle_rad) * dist
            base_y = math.sin(angle_rad) * dist

            width = random.randint(self.mountains_min_width, self.mountains_max_width)
            height = random.randint(40, int(self.horizon_line * 0.33))

            peak_x = base_x + width / 2
            peak_y = base_y

            right_x = base_x + width
            right_y = base_y

            mountains.append(((base_x, base_y), (peak_x, peak_y), (right_x, right_y), height))

        return mountains

    def _world_to_player_view(self, x, y):
        dx = x - self.pos[0]
        dy = y - self.pos[1]
        rad = math.radians(self.angle)

        view_x = dx * math.cos(rad) + dy * math.sin(rad)
        view_y = -dx * math.sin(rad) + dy * math.cos(rad)
        return view_x, view_y

    def _project_point(self, x, y):
        if y <= 0.1:
            return None

        scale = 300 / y  # Cuanto más cerca (y pequeño), mayor escala
        screen_x = int(self.width / 2 + x * scale)
        screen_y = int(self.horizon_line - scale * 1.5)  # Aquí usamos la escala para "elevar" el punto

        if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
            return screen_x, screen_y
        return None

    def draw_ground(self):
        num_lines = 60  # número de líneas horizontales
        horizon_y = self.horizon_line
        bottom_y = self.height

        # Líneas horizontales en perspectiva
        for i in range(1, num_lines):
            t = i / num_lines
            y = int(horizon_y + (bottom_y - horizon_y) * t * t)  # cuadrática para más compresión arriba
            pygame.draw.line(self.screen, self.line_color, (0, y), (self.width, y), 1)

        # Líneas verticales que convergen al centro (punto de fuga)
        center_x = self.width // 2
        step = 40
        for x in range(0, self.width, step):
            pygame.draw.line(self.screen, self.line_color, (x, self.height), (center_x, horizon_y), 1)

    def draw_mountains(self):
        for base_left, peak, base_right, visual_height in self.mountains:
            # Transformar al espacio del jugador
            p1 = self._world_to_player_view(*base_left)
            p2 = self._world_to_player_view(*peak)
            p3 = self._world_to_player_view(*base_right)

            # Proyectar base izquierda y derecha
            s1 = self._project_point(*p1)
            s3 = self._project_point(*p3)

            # Proyectar el pico con su altura visual
            # ↓↓↓ Aquí está la clave: restamos altura proporcional a la profundidad
            peak_proj = self._project_point(p2[0], p2[1])
            if peak_proj:
                screen_peak_x, screen_peak_y = peak_proj
                screen_peak_y -= int(visual_height * (300 / p2[1]))  # altura en perspectiva
                s2 = (screen_peak_x, screen_peak_y)
            else:
                s2 = None

            # Dibujar si todo está dentro de la pantalla
            if s1 and s2 and s3:
                #pygame.draw.polygon(self.screen, self.line_color, [s1, s2, s3], 1) # El uno del final indica el grosor del contorno, si no tiene, es solido
                pygame.draw.polygon(self.screen, self.line_color, [s1, s2, s3]) # Sin grosor para ser solido


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.angle += self.turn_speed
            if self.debug: print(f"Turning left: {self.angle} degrees")
        if keys[pygame.K_d]:
            self.angle -= self.turn_speed
            if self.debug: print(f"Turning left: {self.angle} degrees")
        if keys[pygame.K_w]:
            rad = math.radians(self.angle)
            self.pos[0] += math.sin(rad) * self.speed
            self.pos[1] += math.cos(rad) * self.speed
            if self.debug: print(f"Moving forward: {self.pos[0]}, {self.pos[1]}")
        if keys[pygame.K_s]:
            rad = math.radians(self.angle)
            self.pos[0] -= math.sin(rad) * self.speed
            self.pos[1] -= math.cos(rad) * self.speed
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
