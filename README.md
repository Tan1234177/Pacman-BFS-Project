# Pacman BFS Pro

A Python/Pygame maze game demonstrating **Breadth-First Search (BFS)** shortest-path navigation for multiple chasing ghosts.

## Features
- Multiple ghosts that chase Pacman using BFS with occasional random movement
- Easy, Normal, Hard difficulty settings
- 30-second, 60-second, and unlimited modes
- Lives, score, persistent high score, pause, victory and game-over screens
- Menu, instructions, credits; no external image assets required

## Requirements
Python 3.10+ and Pygame 2.5+.

```bash
python -m pip install -r requirements.txt
python pacman.py
```

## Controls
WASD / arrow keys to move; Esc to pause/resume or go back.

## How BFS works
The maze is a 20x20 grid. Each walkable cell is a graph vertex and adjacent walkable cells are edges. Each ghost uses a queue-based BFS to find the shortest unweighted path to the player's current cell. The ghost then moves one cell along that path. A small chance of random movement makes chases less predictable.

## Notes
- High score is saved in `~/.pacman_bfs_pro_score.json`.
- The game is an educational group project. Keep the original contributors credited.
- A screenshot of the running game can be added to this README before publishing on GitHub.
