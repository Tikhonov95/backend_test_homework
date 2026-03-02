"""
Snake game (OOP version) for Yandex Practicum.

Rules:
- Snake moves continuously (cannot stop or reverse instantly).
- Eating an apple increases snake length by 1.
- Crossing borders wraps to the opposite side.
- Collision with itself resets the game.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame


# =========================
# Settings
# =========================
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20

GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

FPS = 20

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


Point = Tuple[int, int]


@dataclass
class GameObject:
    """Base class for game objects."""
    position: Point
    body_color: Tuple[int, int, int]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object on the surface."""
        raise NotImplementedError


class Apple(GameObject):
    """Apple object that appears at random positions on the grid."""

    def __init__(self) -> None:
        super().__init__(position=(0, 0), body_color=RED)
        self.randomize_position(exclude_positions=[])

    def randomize_position(self, exclude_positions: List[Point]) -> None:
        """Set apple position to a random free cell not occupied by the snake."""
        all_cells = [
            (x * CELL_SIZE, y * CELL_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        ]
        free_cells = [cell for cell in all_cells if cell not in exclude_positions]
        self.position = random.choice(free_cells) if free_cells else (0, 0)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the apple as a filled cell."""
        rect = pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Snake object that moves on the grid and grows after eating apples."""

    def __init__(self) -> None:
        center = ((GRID_WIDTH // 2) * CELL_SIZE, (GRID_HEIGHT // 2) * CELL_SIZE)
        super().__init__(position=center, body_color=GREEN)

        self.length: int = 1
        self.positions: List[Point] = [center]
        self.direction: Point = (CELL_SIZE, 0)  # start moving right
        self.next_direction: Optional[Point] = None

        self._grow_pending: int = 0

    def get_head_position(self) -> Point:
        """Return the head position of the snake."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Apply the buffered direction change (if any)."""
        if self.next_direction is None:
            return
        self.direction = self.next_direction
        self.next_direction = None

    def set_next_direction(self, new_direction: Point) -> None:
        """Set next direction if it's not the direct opposite of current direction."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction == opposite:
            return
        self.next_direction = new_direction

    def move(self) -> Point:
        """
        Move snake by one cell.
        Returns the tail cell that was removed (for optional clearing).
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = (head_x + dx) % SCREEN_WIDTH
        new_y = (head_y + dy) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)

        removed_tail = self.positions[-1]
        if self._grow_pending > 0:
            self._grow_pending -= 1
            self.length += 1
            removed_tail = (-1, -1)
        else:
            self.positions.pop()

        return removed_tail

    def grow(self) -> None:
        """Increase snake length by 1 on the next move."""
        self._grow_pending += 1

    def reset(self) -> None:
        """Reset snake to the initial state."""
        center = ((GRID_WIDTH // 2) * CELL_SIZE, (GRID_HEIGHT // 2) * CELL_SIZE)
        self.position = center
        self.length = 1
        self.positions = [center]
        self.direction = (CELL_SIZE, 0)
        self.next_direction = None
        self._grow_pending = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all snake segments."""
        for pos in self.positions:
            rect = pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)


def handle_keys(snake: Snake) -> None:
    """Handle keyboard events and update snake's next direction."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.set_next_direction((0, -CELL_SIZE))
            elif event.key == pygame.K_DOWN:
                snake.set_next_direction((0, CELL_SIZE))
            elif event.key == pygame.K_LEFT:
                snake.set_next_direction((-CELL_SIZE, 0))
            elif event.key == pygame.K_RIGHT:
                snake.set_next_direction((CELL_SIZE, 0))


def main() -> None:
    """Run the main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(exclude_positions=snake.positions)

    while True:
        clock.tick(FPS)
        screen.fill(BLACK)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()

        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(exclude_positions=snake.positions)
        else:
            if head == apple.position:
                snake.grow()
                apple.randomize_position(exclude_positions=snake.positions)

        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()