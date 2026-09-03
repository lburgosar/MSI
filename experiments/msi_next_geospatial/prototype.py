"""Runnable adaptive-grid UX experiment. It does not invoke Mission Runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pygame

from .adaptive_grid import AdaptiveGrid, GeographicPoint, SpatialSelection


WIDTH, HEIGHT = 1280, 760
CENTER = GeographicPoint(-34.602, -58.402)


class GridPrototype:
    def __init__(self) -> None:
        self.zoom = 14.0
        self.selection = SpatialSelection()
        self.painting = False
        self.erasing = False
        self.font = pygame.font.SysFont("Segoe UI", 15)
        self.title_font = pygame.font.SysFont("Segoe UI", 23, bold=True)
        self.map_rect = pygame.Rect(260, 70, WIDTH - 280, HEIGHT - 105)

    def bounds(self) -> tuple[float, float, float, float]:
        factor = 2 ** (14 - self.zoom)
        latitude_span = .030 * factor
        longitude_span = .045 * factor
        return (
            CENTER.latitude - latitude_span / 2,
            CENTER.longitude - longitude_span / 2,
            CENTER.latitude + latitude_span / 2,
            CENTER.longitude + longitude_span / 2,
        )

    def screen_to_geo(self, position: tuple[int, int]) -> GeographicPoint:
        south, west, north, east = self.bounds()
        x = min(1.0, max(0.0, (position[0] - self.map_rect.left) / self.map_rect.width))
        y = min(1.0, max(0.0, (position[1] - self.map_rect.top) / self.map_rect.height))
        return GeographicPoint(north - y * (north - south), west + x * (east - west))

    def geo_to_screen(self, point: GeographicPoint) -> tuple[int, int]:
        south, west, north, east = self.bounds()
        return (
            self.map_rect.left + int((point.longitude - west) / (east - west) * self.map_rect.width),
            self.map_rect.top + int((north - point.latitude) / (north - south) * self.map_rect.height),
        )

    def apply_at(self, position: tuple[int, int]) -> None:
        if not self.map_rect.collidepoint(position):
            return
        cell = AdaptiveGrid.cell_at(self.screen_to_geo(position), self.zoom)
        self.selection.erase(cell) if self.erasing else self.selection.paint(cell)

    def process(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.MOUSEWHEEL:
            self.zoom = min(19.0, max(10.0, self.zoom + event.y))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            self.painting = event.button == 1
            self.erasing = event.button == 3
            self.apply_at(event.pos)
        elif event.type == pygame.MOUSEMOTION and (self.painting or self.erasing):
            self.apply_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.painting = self.erasing = False
        elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
            self.painting = True
            self.erasing = False
            self.apply_at((int(event.x * WIDTH), int(event.y * HEIGHT)))
        elif event.type == pygame.FINGERUP:
            self.painting = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.selection.clear()
            elif event.key == pygame.K_e:
                target = Path(__file__).with_name("selection.geojson")
                target.write_text(json.dumps(self.selection.to_geojson(), indent=2), encoding="utf-8")
        return True

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((7, 14, 16))
        pygame.draw.rect(screen, (12, 24, 26), (0, 0, 245, HEIGHT))
        screen.blit(self.title_font.render("MSI NEXT", True, (244, 248, 246)), (22, 22))
        screen.blit(self.font.render("SPATIAL INTENT PROTOTYPE", True, (63, 207, 107)), (22, 54))
        items = [
            "GRID PAINT", "Arrastrar: seleccionar", "Click derecho: quitar", "Rueda: zoom", "C: limpiar", "E: exportar GeoJSON",
            "", f"Zoom: {self.zoom:.0f}", f"Resolución: {AdaptiveGrid.resolution_m(self.zoom):.0f} m", f"Geometrías: {len(self.selection.polygons)}",
            "", "BASEMAP", "Placeholder offline", "Sin tiles públicos", "Sin Runtime conectado",
        ]
        y = 105
        for item in items:
            color = (226, 234, 230) if item else (85, 104, 99)
            screen.blit(self.font.render(item, True, color), (22, y)); y += 28

        pygame.draw.rect(screen, (62, 81, 63), self.map_rect)
        # Terrain-like context is deliberately labelled as placeholder.
        for index in range(7):
            inset = index * 42
            pygame.draw.rect(screen, (73 + index * 2, 91 + index * 2, 68), self.map_rect.inflate(-inset, -inset), 1)
        self._draw_grid(screen)
        for polygon in self.selection.polygons.values():
            points = [self.geo_to_screen(point) for point in polygon]
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(overlay, (48, 214, 103, 105), points)
            pygame.draw.polygon(overlay, (80, 245, 130, 230), points, 2)
            screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (120, 145, 128), self.map_rect, 1)
        screen.blit(self.font.render("BASEMAP PLACEHOLDER · GEOGRAPHIC GEOMETRY · WGS84", True, (224, 235, 226)), (self.map_rect.left + 14, self.map_rect.top + 12))

    def _draw_grid(self, screen: pygame.Surface) -> None:
        center_cell = AdaptiveGrid.cell_at(CENTER, self.zoom)
        p0, p1, _, p3 = center_cell.polygon
        cell_w = abs(self.geo_to_screen(p1)[0] - self.geo_to_screen(p0)[0])
        cell_h = abs(self.geo_to_screen(p3)[1] - self.geo_to_screen(p0)[1])
        cell_w, cell_h = max(8, cell_w), max(8, cell_h)
        anchor = self.geo_to_screen(p0)
        x = anchor[0]
        while x > self.map_rect.left: x -= cell_w
        while x < self.map_rect.right:
            pygame.draw.line(screen, (136, 161, 141), (x, self.map_rect.top), (x, self.map_rect.bottom), 1); x += cell_w
        y = anchor[1]
        while y > self.map_rect.top: y -= cell_h
        while y < self.map_rect.bottom:
            pygame.draw.line(screen, (136, 161, 141), (self.map_rect.left, y), (self.map_rect.right, y), 1); y += cell_h


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("MSI NEXT · Adaptive Grid Prototype")
    prototype = GridPrototype()
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            running = prototype.process(event)
        prototype.render(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
