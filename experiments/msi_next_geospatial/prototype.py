"""Functional map-first MSI NEXT UX experiment, isolated from Mission Runtime."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "manager"))

from msi_next.workflow import MissionPhase, OperatorWorkflow
from .adaptive_grid import AdaptiveGrid, GeographicPoint, SpatialSelection

CENTER = GeographicPoint(-34.602, -58.402)
INK, PANEL, LINE = (6, 13, 15), (12, 24, 26), (43, 62, 64)
TEXT, MUTED, GREEN = (238, 244, 241), (151, 169, 164), (54, 210, 104)


class NextExperience:
    def __init__(self) -> None:
        self.zoom = 15.0
        self.selection = SpatialSelection()
        self.workflow = OperatorWorkflow()
        self.painting = self.erasing = False
        self.font = pygame.font.SysFont("Segoe UI", 15)
        self.small = pygame.font.SysFont("Segoe UI", 12)
        self.title = pygame.font.SysFont("Segoe UI", 23, bold=True)
        self.heading = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.layout(1440, 900)

    def layout(self, width: int, height: int) -> None:
        self.width, self.height = max(1040, width), max(680, height)
        left = 248 if self.width > 1180 else 205
        right = 290 if self.width > 1250 else 245
        self.left_rect = pygame.Rect(0, 64, left, self.height - 64)
        self.right_rect = pygame.Rect(self.width - right, 64, right, self.height - 64)
        self.map_rect = pygame.Rect(left, 64, self.width - left - right, self.height - 140)
        self.bottom_rect = pygame.Rect(left, self.height - 76, self.map_rect.width, 76)
        self.primary_rect = pygame.Rect(self.right_rect.left - 260, 12, 245, 40)
        self.wind_rect = pygame.Rect(self.right_rect.left + 15, self.height - 58, right - 30, 40)
        self.advanced_rect = pygame.Rect(15, self.height - 52, left - 30, 36)

    def bounds(self) -> tuple[float, float, float, float]:
        factor = 2 ** (14 - self.zoom)
        lat, lon = .030 * factor, .045 * factor
        return CENTER.latitude-lat/2, CENTER.longitude-lon/2, CENTER.latitude+lat/2, CENTER.longitude+lon/2

    def screen_to_geo(self, pos: tuple[int, int]) -> GeographicPoint:
        south, west, north, east = self.bounds()
        x = min(1, max(0, (pos[0]-self.map_rect.left)/self.map_rect.width))
        y = min(1, max(0, (pos[1]-self.map_rect.top)/self.map_rect.height))
        return GeographicPoint(north-y*(north-south), west+x*(east-west))

    def geo_to_screen(self, point: GeographicPoint) -> tuple[int, int]:
        south, west, north, east = self.bounds()
        x = self.map_rect.left + int((point.longitude-west)/(east-west)*self.map_rect.width)
        y = self.map_rect.top + int((north-point.latitude)/(north-south)*self.map_rect.height)
        return x, y

    def apply_at(self, pos: tuple[int, int]) -> None:
        editable = self.workflow.phase in (MissionPhase.DEFINE, MissionPhase.CORRECTION)
        if editable and self.map_rect.collidepoint(pos):
            cell = AdaptiveGrid.cell_at(self.screen_to_geo(pos), self.zoom)
            self.selection.erase(cell) if self.erasing else self.selection.paint(cell)

    def process(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.VIDEORESIZE:
            self.layout(event.w, event.h)
        elif event.type == pygame.MOUSEWHEEL and self.map_rect.collidepoint(pygame.mouse.get_pos()):
            self.zoom = min(19, max(10, self.zoom + event.y))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.primary_rect.collidepoint(event.pos):
                self.workflow.primary_action(bool(self.selection.polygons))
            elif self.wind_rect.collidepoint(event.pos):
                self.workflow.inject_wind()
            elif self.advanced_rect.collidepoint(event.pos):
                self.workflow.advanced = not self.workflow.advanced
            elif event.button in (1, 3):
                self.painting, self.erasing = event.button == 1, event.button == 3
                self.apply_at(event.pos)
        elif event.type == pygame.MOUSEMOTION and (self.painting or self.erasing):
            self.apply_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.painting = self.erasing = False
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
            self.painting = True
            self.apply_at((int(event.x*self.width), int(event.y*self.height)))
        elif event.type == pygame.FINGERUP:
            self.painting = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and self.workflow.phase in (MissionPhase.DEFINE, MissionPhase.CORRECTION):
                self.selection.clear()
            elif event.key == pygame.K_e:
                target = Path(__file__).with_name("selection.geojson")
                target.write_text(json.dumps(self.selection.to_geojson(), indent=2), encoding="utf-8")
            elif event.key == pygame.K_w:
                self.workflow.inject_wind()
        return True

    def label(self, screen, value, pos, color=TEXT, font=None) -> None:
        screen.blit((font or self.font).render(value, True, color), pos)

    def button(self, screen, rect, text, active=True, danger=False) -> None:
        color = (160, 55, 49) if danger else ((29, 142, 73) if active else (35, 49, 50))
        pygame.draw.rect(screen, color, rect, border_radius=7)
        pygame.draw.rect(screen, GREEN if active and not danger else LINE, rect, 1, border_radius=7)
        rendered = self.font.render(text, True, TEXT if active else MUTED)
        screen.blit(rendered, rendered.get_rect(center=rect.center))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(INK)
        pygame.draw.rect(screen, (5, 11, 13), (0, 0, self.width, 64))
        self.label(screen, "MSI", (18, 9), TEXT, self.title)
        self.label(screen, "MISSION OPERATOR", (18, 39), GREEN, self.small)
        self.label(screen, "PULVERIZAR · LOTE NORTE", (270, 13), TEXT, self.heading)
        notice = self.workflow.decision
        notice_color = (255, 183, 67) if self.workflow.phase is MissionPhase.PAUSED else GREEN
        self.label(screen, notice, (270, 38), notice_color, self.small)
        enabled = bool(self.selection.polygons) and self.workflow.phase not in (MissionPhase.RECONNAISSANCE, MissionPhase.COMPLETE)
        self.button(screen, self.primary_rect, self.workflow.action_label, enabled)
        pygame.draw.rect(screen, PANEL, self.left_rect)
        pygame.draw.rect(screen, PANEL, self.right_rect)
        self._left(screen)
        self._map(screen)
        self._right(screen)
        self._bottom(screen)

    def _left(self, screen) -> None:
        x, y = 18, 82
        self.label(screen, "1  INTENCIÓN", (x, y), GREEN, self.heading); y += 34
        self.button(screen, pygame.Rect(x, y, self.left_rect.width-36, 42), "PULVERIZAR ESTA ZONA"); y += 62
        self.label(screen, "2  DEFINÍ DÓNDE", (x, y), GREEN, self.heading); y += 30
        for line in ("Pintá sobre el mapa", "Click derecho: quitar", "Rueda: más precisión", f"Resolución: {AdaptiveGrid.resolution_m(self.zoom):.0f} m", f"Sectores: {len(self.selection.polygons)}"):
            self.label(screen, line, (x, y), GREEN if line.startswith("Resolución") else TEXT); y += 25
        y += 12; self.label(screen, "3  PARÁMETROS CLAVE", (x, y), GREEN, self.heading); y += 30
        for line in ("Dosis       7.5 L/ha", "Altura      12 m", "Velocidad   6 m/s", "Swath       15 m"):
            self.label(screen, line, (x, y)); y += 25
        if self.workflow.advanced:
            y += 10; self.label(screen, "PRECISIÓN", (x, y), MUTED, self.small); y += 22
            for line in ("CRS  WGS 84", "Lat  -34.6020", "Lon  -58.4020", "Overlap  20 %", "Ángulo  265°"):
                self.label(screen, line, (x, y), MUTED); y += 22
        self.button(screen, self.advanced_rect, "OCULTAR DETALLES" if self.workflow.advanced else "DETALLES / PRECISIÓN")

    def _map(self, screen) -> None:
        screen.set_clip(self.map_rect)
        pygame.draw.rect(screen, (44, 66, 48), self.map_rect)
        for i in range(12):
            r = pygame.Rect(self.map_rect.left+18+i*76, self.map_rect.top+18, 54, self.map_rect.height-36)
            pygame.draw.rect(screen, (52+i%2*8, 82+i%3*5, 51), r)
            for yy in range(r.top, r.bottom, 13):
                pygame.draw.line(screen, (75, 104, 66), (r.left, yy), (r.right, yy))
        pygame.draw.line(screen, (120, 112, 83), (self.map_rect.left, self.map_rect.bottom-70), (self.map_rect.right, self.map_rect.bottom-120), 18)
        self._grid(screen)
        for polygon in self.selection.polygons.values():
            points = [self.geo_to_screen(p) for p in polygon]
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(overlay, (48, 214, 103, 100), points)
            pygame.draw.polygon(overlay, GREEN, points, 2)
            screen.blit(overlay, (0, 0))
        if self.workflow.phase in (MissionPhase.RECONNAISSANCE, MissionPhase.CORRECTION):
            observed = self.map_rect.inflate(-self.map_rect.width//3, -self.map_rect.height//3)
            pygame.draw.rect(screen, (62, 190, 235), observed, 3)
            self.label(screen, "OBSERVADO · BORDE +4 m", (observed.left+8, observed.top+8), (118, 218, 255), self.small)
        self._drones(screen)
        self.label(screen, "CONTEXTO CARTOGRÁFICO SIMULADO · WGS84 · SIN TILES EXTERNOS", (self.map_rect.left+12, self.map_rect.top+10), TEXT, self.small)
        self.label(screen, f"Zoom {self.zoom:.0f}  ·  {AdaptiveGrid.resolution_m(self.zoom):.0f} m", (self.map_rect.right-145, self.map_rect.bottom-25), TEXT, self.small)
        screen.set_clip(None)

    def _grid(self, screen) -> None:
        cell = AdaptiveGrid.cell_at(CENTER, self.zoom)
        p0, p1, _, p3 = cell.polygon
        cw = max(8, abs(self.geo_to_screen(p1)[0]-self.geo_to_screen(p0)[0]))
        ch = max(8, abs(self.geo_to_screen(p3)[1]-self.geo_to_screen(p0)[1]))
        x, y = self.geo_to_screen(p0)
        while x > self.map_rect.left: x -= cw
        while x < self.map_rect.right:
            pygame.draw.line(screen, (115, 142, 119), (x, self.map_rect.top), (x, self.map_rect.bottom)); x += cw
        while y > self.map_rect.top: y -= ch
        while y < self.map_rect.bottom:
            pygame.draw.line(screen, (115, 142, 119), (self.map_rect.left, y), (self.map_rect.right, y)); y += ch

    def _drones(self, screen) -> None:
        if self.workflow.phase in (MissionPhase.DEFINE, MissionPhase.PREFLIGHT):
            return
        t = self.workflow.progress
        for i in range(3):
            x = self.map_rect.left + int(self.map_rect.width*(.25+.5*t))
            y = self.map_rect.top + int(self.map_rect.height*(.3+i*.18+math.sin(t*8+i)*.03))
            pygame.draw.circle(screen, TEXT, (x, y), 8)
            pygame.draw.line(screen, GREEN, (x-12, y), (x+12, y), 2)
            self.label(screen, f"D{i+1}", (x+12, y-12), TEXT, self.small)

    def _right(self, screen) -> None:
        x, y = self.right_rect.left+16, 82
        self.label(screen, "ESTADO DE MISIÓN", (x, y), GREEN, self.heading); y += 31
        self.label(screen, self.workflow.phase.value.upper(), (x, y), TEXT, self.title); y += 43
        phases = ["Área", "Preflight", "Recon", "Corrección", "Autorizar", "Ejecutar"]
        indices = {p: i for i, p in enumerate(MissionPhase)}
        active = min(5, indices[self.workflow.phase])
        for i, phase in enumerate(phases):
            pygame.draw.circle(screen, GREEN if i <= active else LINE, (x+8, y+8), 7)
            self.label(screen, phase, (x+25, y)); y += 28
        y += 10; self.label(screen, "RECURSOS", (x, y), GREEN, self.heading); y += 29
        active_resource = self.workflow.phase in (MissionPhase.EXECUTING, MissionPhase.PAUSED)
        for i, battery in enumerate((82, 76, 65)):
            state = "ACTIVO" if active_resource else "LISTO"
            self.label(screen, f"D{i+1}  {state}     {battery}%", (x, y)); y += 27
        y += 8; self.label(screen, "AMBIENTE", (x, y), GREEN, self.heading); y += 28
        wind_color = (255, 183, 67) if self.workflow.wind_ms > 7 else TEXT
        self.label(screen, f"Viento  {self.workflow.wind_ms:.1f} m/s  ·  265°", (x, y), wind_color); y += 26
        self.label(screen, "Link 98%  ·  21°C", (x, y)); y += 35
        self.label(screen, "OBSERVACIÓN", (x, y), GREEN, self.heading); y += 26
        for start in range(0, len(self.workflow.observation), 28):
            self.label(screen, self.workflow.observation[start:start+28], (x, y), TEXT, self.small); y += 19
        self.button(screen, self.wind_rect, "SIMULAR VIENTO ↑", True, True)

    def _bottom(self, screen) -> None:
        pygame.draw.rect(screen, (9, 18, 20), self.bottom_rect)
        x, y = self.bottom_rect.left+18, self.bottom_rect.top+12
        self.label(screen, "PROGRESO OPERACIONAL", (x, y), MUTED, self.small)
        bar = pygame.Rect(x, y+27, self.bottom_rect.width-36, 12)
        pygame.draw.rect(screen, LINE, bar, border_radius=6)
        show = self.workflow.phase in (MissionPhase.RECONNAISSANCE, MissionPhase.EXECUTING, MissionPhase.COMPLETE)
        value = self.workflow.progress if show else 0
        pygame.draw.rect(screen, GREEN, (bar.x, bar.y, int(bar.width*value), bar.height), border_radius=6)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1440, 900), pygame.RESIZABLE)
    pygame.display.set_caption("MSI NEXT · Mission Operator Preview")
    app, clock, running = NextExperience(), pygame.time.Clock(), True
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            running = app.process(event)
        app.workflow.tick(dt)
        app.render(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
