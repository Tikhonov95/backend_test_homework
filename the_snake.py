"""Snake game (OOP version) for Practicum sprint project."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20

GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

FPS = 20

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


Direction = tuple[int, int]


DIRECTION_UP: Direction = (0, -1)
DIRECTION_DOWN: Direction = (0, 1)
DIRECTION_LEFT: Direction = (-1, 0)
DIRECTION_RIGHT: Direction = (1, 0)

OPPOSITE = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_LEFT: DIRECTION_RIGHT,
    DIRECTION_RIGHT: DIRECTION_LEFT,
}


@dataclass
class GameObject:
    """Base game object placed on the grid."""

    position: tuple[int, int]
    body_color: tuple[int, int, int]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object on a surface."""
        raise NotImplementedError


class Apple(GameObject):
    """Apple object that appears on random free cells."""

    def __init__(self) -> None:
        """Create an apple and place it on a free random cell."""
        super().__init__(position=(0, 0), body_color=RED)
        self.randomize_position(exclude_positions=())

    def randomize_position(
        self,
        exclude_positions: Iterable[tuple[int, int]],
    ) -> None:
        """Move apple to a random cell, avoiding snake cells."""
        exclude = set(exclude_positions)
        while True:
            x = random.randrange(GRID_WIDTH) * CELL_SIZE
            y = random.randrange(GRID_HEIGHT) * CELL_SIZE
            if (x, y) not in exclude:
                self.position = (x, y)
                return

    def draw(self, surface: pygame.Surface) -> None:
        """Draw apple as a filled square."""
        rect = pygame.Rect(self.position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Snake controlled by the player."""

    def __init__(self) -> None:
        """Create a snake in the initial position."""
        start = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position=start, body_color=GREEN)
        self.length = 1
        self.positions: list[tuple[int, int]] = [start]
        self.direction: Direction = DIRECTION_RIGHT
        self.next_direction: Direction | None = None

    def get_head_position(self) -> tuple[int, int]:
        """Return snake head position."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Apply pending direction if it is not opposite."""
        if self.next_direction is None:
            return
        if OPPOSITE[self.direction] != self.next_direction:
            self.direction = self.next_direction
        self.next_direction = None

    def move(self) -> None:
        """Move snake by one cell with wrap-around."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_x = (head_x // CELL_SIZE + dir_x) % GRID_WIDTH
        new_y = (head_y // CELL_SIZE + dir_y) % GRID_HEIGHT
        new_head = (new_x * CELL_SIZE, new_y * CELL_SIZE)

        self.positions.insert(0, new_head)
        while len(self.positions) > self.length:
            self.positions.pop()

    def grow(self) -> None:
        """Increase snake length by one."""
        self.length += 1

    def reset(self) -> None:
        """Reset snake to initial state."""
        start = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [start]
        self.direction = DIRECTION_RIGHT
        self.next_direction = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw snake as filled squares."""
        for pos in self.positions:
            rect = pygame.Rect(pos, (CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)


def handle_keys(snake: Snake) -> None:
    """Handle keyboard and quit events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_UP:
            snake.next_direction = DIRECTION_UP
        elif event.key == pygame.K_DOWN:
            snake.next_direction = DIRECTION_DOWN
        elif event.key == pygame.K_LEFT:
            snake.next_direction = DIRECTION_LEFT
        elif event.key == pygame.K_RIGHT:
            snake.next_direction = DIRECTION_RIGHT


def main() -> None:
    """Run the game main loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(exclude_positions=snake.positions)

    while True:
        clock.tick(FPS)
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(exclude_positions=snake.positions)

        if head == apple.position:
            snake.grow()
            apple.randomize_position(exclude_positions=snake.positions)

        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()
