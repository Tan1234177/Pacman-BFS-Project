"""Pacman BFS Pro - educational maze game. Requires pygame >= 2.5."""
import json
import math
import random
from collections import deque
from pathlib import Path

import pygame

CELL = 30
GRID = [
    '####################',
    '#........#.........#',
    '#.##.###.#.###.##..#',
    '#....#.......#.....#',
    '###..#.#####.#..####',
    '#....#...#...#.....#',
    '#.######.#.######..#',
    '#..................#',
    '#.##.###...###.##..#',
    '#....#.......#.....#',
    '#.##.#.#####.#.##..#',
    '#....#...#...#.....#',
    '#.######.#.######..#',
    '#..................#',
    '#.##.###...###.##..#',
    '#....#.......#.....#',
    '#.##.#.#####.#.##..#',
    '#....#.......#.....#',
    '#..................#',
    '####################',
]
# Normalize rows and ensure the board is a rectangular 20x20 grid.
assert len(GRID) == 20 and all(len(row) == 20 for row in GRID), 'Map must be 20x20'
ROWS, COLS = len(GRID), len(GRID[0])
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + 78
FPS = 60
BG = (9, 13, 29)
NAVY = (18, 28, 65)
BLUE = (46, 109, 245)
WHITE = (235, 242, 255)
MUTED = (157, 175, 207)
YELLOW = (255, 220, 65)
GREEN = (81, 224, 155)
RED = (250, 95, 105)
GHOST_COLORS = [(255, 100, 115), (90, 207, 255), (255, 165, 82), (198, 127, 255)]
SCORE_PATH = Path.home() / '.pacman_bfs_pro_score.json'
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
START = (1, 1)
GHOST_STARTS = [(18, 18), (18, 1), (1, 18), (9, 9)]
LEVELS = {'EASY': (230, 350, 2), 'NORMAL': (165, 250, 3), 'HARD': (115, 170, 4)}


def neighbors(cell):
    r, c = cell
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and GRID[nr][nc] != '#':
            yield nr, nc


def bfs(start, goal):
    """Return the shortest path from start to goal (excluding start)."""
    if start == goal:
        return []
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        for nxt in neighbors(current):
            if nxt in parent:
                continue
            parent[nxt] = current
            if nxt == goal:
                path = []
                at = goal
                while at != start:
                    path.append(at)
                    at = parent[at]
                return path[::-1]
            queue.append(nxt)
    return []


def load_high_score():
    try:
        return max(0, int(json.loads(SCORE_PATH.read_text(encoding='utf-8')).get('high_score', 0)))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0


def save_high_score(score):
    try:
        SCORE_PATH.write_text(json.dumps({'high_score': score}), encoding='utf-8')
    except OSError:
        pass


class PacmanGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('PACMAN BFS PRO | Python + Pygame')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 21, bold=True)
        self.small = pygame.font.SysFont('arial', 16)
        self.big = pygame.font.SysFont('arial', 43, bold=True)
        self.state = 'MENU'
        self.difficulty = 'NORMAL'
        self.mode = 60  # seconds; 0 means unlimited
        self.high_score = load_high_score()
        self.buttons = []
        self.new_game()

    def new_game(self):
        self.player = START
        self.ghosts = []
        self.score = 0
        self.lives = 3
        self.elapsed = 0.0
        self.player_accum = 0.0
        self.ghost_accum = 0.0
        self.invulnerable = 1.5
        self.pellets = {(r, c) for r, row in enumerate(GRID) for c, char in enumerate(row) if char == '.'}
        self.pellets.discard(START)
        self.spawn_ghosts()

    def spawn_ghosts(self):
        count = LEVELS[self.difficulty][2]
        self.ghosts = [{'pos': pos, 'home': pos, 'color': GHOST_COLORS[i]}
                       for i, pos in enumerate(GHOST_STARTS[:count])]
        for ghost in self.ghosts:
            self.pellets.discard(ghost['home'])

    def button(self, label, center_y, action, width=300):
        rect = pygame.Rect((WIDTH - width) // 2, center_y, width, 45)
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, BLUE if hover else NAVY, rect, border_radius=12)
        pygame.draw.rect(self.screen, (75, 105, 170), rect, 2, border_radius=12)
        surf = self.font.render(label, True, WHITE)
        self.screen.blit(surf, surf.get_rect(center=rect.center))
        self.buttons.append((rect, action))

    def text_center(self, message, y, font=None, color=WHITE):
        surf = (font or self.font).render(message, True, color)
        self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))

    def on_click(self, pos):
        for rect, action in self.buttons:
            if rect.collidepoint(pos):
                action()
                break

    def start(self):
        self.new_game()
        self.state = 'PLAY'

    def set_difficulty(self, value):
        self.difficulty = value

    def set_mode(self, value):
        self.mode = value

    def move_player(self):
        keys = pygame.key.get_pressed()
        direction = None
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction = (-1, 0)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction = (1, 0)
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction = (0, -1)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction = (0, 1)
        if direction is None:
            return
        target = (self.player[0] + direction[0], self.player[1] + direction[1])
        if target in neighbors(self.player):
            self.player = target
            if target in self.pellets:
                self.pellets.remove(target)
                self.score += 10
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
            self.check_collision()
            if not self.pellets and self.state == 'PLAY':
                self.state = 'WIN'

    def move_ghosts(self):
        for ghost in self.ghosts:
            # 15% chance of a random valid move for less predictable behavior.
            candidates = list(neighbors(ghost['pos']))
            if not candidates:
                continue
            if random.random() < 0.15:
                ghost['pos'] = random.choice(candidates)
            else:
                path = bfs(ghost['pos'], self.player)
                if path:
                    ghost['pos'] = path[0]
            self.check_collision()
            if self.state != 'PLAY':
                break

    def check_collision(self):
        if self.invulnerable > 0 or self.state != 'PLAY':
            return
        if any(ghost['pos'] == self.player for ghost in self.ghosts):
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'LOSE'
            else:
                self.player = START
                for ghost in self.ghosts:
                    ghost['pos'] = ghost['home']
                self.invulnerable = 1.7

    def update(self, dt):
        if self.state != 'PLAY':
            return
        self.elapsed += dt
        self.invulnerable = max(0.0, self.invulnerable - dt)
        if self.mode and self.elapsed >= self.mode:
            self.state = 'TIME'
            return
        player_ms, ghost_ms, _ = LEVELS[self.difficulty]
        self.player_accum += dt * 1000
        self.ghost_accum += dt * 1000
        if self.player_accum >= player_ms:
            self.player_accum %= player_ms
            self.move_player()
        if self.state == 'PLAY' and self.ghost_accum >= ghost_ms:
            self.ghost_accum %= ghost_ms
            self.move_ghosts()

    def draw_board(self):
        for r, row in enumerate(GRID):
            for c, char in enumerate(row):
                x, y = c * CELL, r * CELL
                if char == '#':
                    pygame.draw.rect(self.screen, NAVY, (x + 1, y + 1, CELL - 2, CELL - 2), border_radius=5)
                    pygame.draw.rect(self.screen, BLUE, (x + 3, y + 3, CELL - 6, CELL - 6), 1, border_radius=4)
        for r, c in self.pellets:
            pygame.draw.circle(self.screen, WHITE, (c * CELL + CELL // 2, r * CELL + CELL // 2), 3)
        for ghost in self.ghosts:
            r, c = ghost['pos']
            center = (c * CELL + CELL // 2, r * CELL + CELL // 2)
            pygame.draw.circle(self.screen, ghost['color'], center, 11)
            pygame.draw.circle(self.screen, WHITE, (center[0] - 4, center[1] - 2), 3)
            pygame.draw.circle(self.screen, WHITE, (center[0] + 4, center[1] - 2), 3)
        if self.invulnerable <= 0 or int(self.elapsed * 7) % 2 == 0:
            r, c = self.player
            center = (c * CELL + CELL // 2, r * CELL + CELL // 2)
            pygame.draw.circle(self.screen, YELLOW, center, 12)
            mouth = 0.2 + abs(math.sin(self.elapsed * 10)) * 0.55
            points = [center, (center[0] + int(13 * math.cos(mouth)), center[1] - int(13 * math.sin(mouth))),
                      (center[0] + int(13 * math.cos(mouth)), center[1] + int(13 * math.sin(mouth)))]
            pygame.draw.polygon(self.screen, BG, points)
        pygame.draw.rect(self.screen, NAVY, (0, ROWS * CELL, WIDTH, 78))
        time_label = 'UNLIMITED' if self.mode == 0 else f'{max(0, self.mode - int(self.elapsed))}s LEFT'
        self.screen.blit(self.small.render(f'SCORE {self.score}   BEST {self.high_score}', True, WHITE), (16, HEIGHT - 63))
        self.screen.blit(self.small.render(f'LIVES {self.lives}   {time_label}   {self.difficulty}', True, GREEN), (16, HEIGHT - 35))
        self.screen.blit(self.small.render('ESC: Pause', True, MUTED), (WIDTH - 110, HEIGHT - 35))

    def draw(self):
        self.screen.fill(BG)
        self.buttons = []
        if self.state in ('PLAY', 'PAUSE'):
            self.draw_board()
            if self.state == 'PAUSE':
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 175))
                self.screen.blit(overlay, (0, 0))
                self.text_center('PAUSED', 205, self.big, YELLOW)
                self.button('RESUME', 280, lambda: setattr(self, 'state', 'PLAY'))
                self.button('MAIN MENU', 350, lambda: setattr(self, 'state', 'MENU'))
        elif self.state == 'MENU':
            self.text_center('PACMAN BFS PRO', 115, self.big, YELLOW)
            self.text_center('Python + Pygame + BFS Pathfinding', 159, self.small, MUTED)
            self.button('START GAME', 240, self.start)
            self.button('SETTINGS', 305, lambda: setattr(self, 'state', 'SETTINGS'))
            self.button('HOW TO PLAY', 370, lambda: setattr(self, 'state', 'HELP'))
            self.button('CREDITS', 435, lambda: setattr(self, 'state', 'CREDITS'))
            self.text_center(f'BEST SCORE: {self.high_score}', 535, self.font, GREEN)
        elif self.state == 'SETTINGS':
            self.text_center('SETTINGS', 90, self.big, YELLOW)
            self.text_center('Difficulty', 145, self.font)
            for i, name in enumerate(LEVELS):
                self.button(('> ' if name == self.difficulty else '') + name, 175 + i * 52,
                            lambda value=name: self.set_difficulty(value))
            self.text_center('Time mode', 370, self.font)
            for i, (label, seconds) in enumerate([('30 SECONDS', 30), ('60 SECONDS', 60), ('UNLIMITED', 0)]):
                self.button(('> ' if seconds == self.mode else '') + label, 400 + i * 52,
                            lambda value=seconds: self.set_mode(value))
            self.button('BACK', 575, lambda: setattr(self, 'state', 'MENU'))
        elif self.state == 'HELP':
            self.text_center('HOW TO PLAY', 110, self.big, YELLOW)
            for i, line in enumerate(['WASD / Arrow Keys: Move Pacman', 'Eat pellets to score 10 points each',
                                       'Avoid ghosts that chase you with BFS', 'You start with 3 lives',
                                       'ESC: Pause / Resume', 'Eat all pellets to win!']):
                self.text_center(line, 200 + i * 45, self.small)
            self.button('BACK', 535, lambda: setattr(self, 'state', 'MENU'))
        elif self.state == 'CREDITS':
            self.text_center('CREDITS', 110, self.big, YELLOW)
            for i, line in enumerate(['Team Mixi Gaming Fan', 'Lead: Le Tan', 'Developers: Gia Khang, Phuc Khang',
                                       'Design: Hoang Khoa, Thanh Tung']):
                self.text_center(line, 225 + i * 50, self.small)
            self.button('BACK', 520, lambda: setattr(self, 'state', 'MENU'))
        else:
            messages = {'WIN': ('YOU WIN!', GREEN), 'LOSE': ('GAME OVER', RED), 'TIME': ('TIME IS UP!', YELLOW)}
            message, color = messages.get(self.state, ('GAME OVER', WHITE))
            self.text_center(message, 190, self.big, color)
            self.text_center(f'SCORE: {self.score}   BEST: {self.high_score}', 260, self.font)
            self.button('PLAY AGAIN', 345, self.start)
            self.button('MAIN MENU', 415, lambda: setattr(self, 'state', 'MENU'))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == 'PLAY':
                        self.state = 'PAUSE'
                    elif self.state == 'PAUSE':
                        self.state = 'PLAY'
                    elif self.state != 'MENU':
                        self.state = 'MENU'
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(event.pos)
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == '__main__':
    PacmanGame().run()
