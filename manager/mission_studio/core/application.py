from __future__ import annotations

import pygame


class MissionStudio:
    """Ciclo principal de MSI Mission Studio."""

    WIDTH = 1280
    HEIGHT = 800
    FPS = 60

    BACKGROUND_COLOR = (248, 248, 250)

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("MSI Mission Studio")

        self.clock = pygame.time.Clock()
        self.running = True

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        """Actualiza la lógica de la aplicación."""
        pass

    def render(self) -> None:
        self.screen.fill(self.BACKGROUND_COLOR)
        pygame.display.flip()

    def run(self) -> None:
        try:
            while self.running:
                self.process_events()
                self.update()
                self.render()
                self.clock.tick(self.FPS)
        finally:
            pygame.quit()