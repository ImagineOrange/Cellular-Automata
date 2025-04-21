import pygame
import numpy as np
import time

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 150
GRID_HEIGHT = 100
CELL_SIZE = 7  # Size of each cell in pixels

# Simulation speed
FRAME_DELAY = 0.05  # Seconds to pause between updates (adjust as needed)

# Initial state probability (0.0 to 1.0)
RANDOM_DENSITY = 0.48

# Colors (RGB tuples)
COLOR_ALIVE = (255, 180, 100)     # Orange/Yellow for alive cells
COLOR_BACKGROUND = (10, 10, 40)     # Dark blue background
COLOR_GRID = (30, 30, 60)       # Grid lines (subtle)

# Diamoeba Rule B35678/S5678
BIRTH_NEIGHBORS = {3, 5, 6, 7, 8}
SURVIVAL_NEIGHBORS = {5, 6, 7, 8}

# --- Main Simulation Logic ---

def initialize_grid(width, height, density):
    """Creates the initial grid state with random cell placement."""
    # Use (height, width) for NumPy array shape (rows, columns)
    cells = np.random.choice([0, 1], size=(height, width), p=[1 - density, density])
    print(f"Grid initialized with random density: {density * 100:.1f}%")
    return cells

def count_live_neighbors(cells, r, c, height, width):
    """
    Counts the number of live neighbors for a cell at (r, c) using Moore neighborhood
    and toroidal (wrap-around) boundary conditions.
    Assumes cells array has shape (height, width).
    """
    total_alive = 0
    # Iterate through the 3x3 neighborhood centered at (r, c)
    for i in range(-1, 2):
        for j in range(-1, 2):
            # Skip the center cell itself
            if i == 0 and j == 0:
                continue

            # Calculate neighbor coordinates with wrap-around
            neighbor_r = (r + i) % height
            neighbor_c = (c + j) % width

            # Add neighbor's value (1 if alive, 0 if dead)
            total_alive += cells[neighbor_r, neighbor_c]

    return int(total_alive)

def update_grid(surface, current_cells, cell_size, height, width):
    """
    Updates the grid based on the Diamoeba rules (B35678/S5678) and draws the new state.
    Assumes current_cells array has shape (height, width).
    """
    # Initialize next state grid with the same shape (height, width)
    next_grid_state = np.zeros_like(current_cells)

    # Iterate through all cells using (row, column) indices
    for r, c in np.ndindex(current_cells.shape):
        live_neighbors = count_live_neighbors(current_cells, r, c, height, width)
        current_state = current_cells[r, c]
        next_state = 0 # Default to dead

        # --- Diamoeba Rules (B35678/S5678) ---
        if current_state == 0 and live_neighbors in BIRTH_NEIGHBORS:
            next_state = 1 # Birth
        elif current_state == 1 and live_neighbors in SURVIVAL_NEIGHBORS:
            next_state = 1 # Survival
        # Else: cell dies or stays dead (next_state remains 0)

        next_grid_state[r, c] = next_state

        # --- Drawing ---
        # Determine color based on the *next* state for visualization clarity
        # (or use current_state if you prefer showing the state *before* update)
        cell_color = COLOR_ALIVE if next_state == 1 else COLOR_BACKGROUND

        # Pygame rect uses (left, top, width, height) -> (x, y, w, h)
        # x coordinate corresponds to column (c), y coordinate corresponds to row (r)
        rect_x = c * cell_size
        rect_y = r * cell_size
        # Leave 1px gap for grid effect if cell_size > 1
        rect_width = max(1, cell_size - 1)
        rect_height = max(1, cell_size - 1)
        rect = (rect_x, rect_y, rect_width, rect_height)

        # Draw only if the color is not the background (optimization)
        if cell_color != COLOR_BACKGROUND:
             pygame.draw.rect(surface, cell_color, rect)

    # Add a delay to control animation speed
    time.sleep(FRAME_DELAY)
    return next_grid_state

def main(grid_width, grid_height, cellsize, density):
    """Initializes Pygame and runs the main simulation loop."""
    pygame.init()
    # Screen dimensions in pixels: (width, height)
    screen_width = grid_width * cellsize
    screen_height = grid_height * cellsize
    surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Diamoeba Cellular Automaton (B35678/S5678)")

    # Initialize grid - pass height (rows) then width (cols)
    cells = initialize_grid(grid_width, grid_height, density)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add other event handling here if needed (e.g., pause, reset)

        # Fill background each frame before drawing updated cells
        surface.fill(COLOR_BACKGROUND) # Use background color for grid effect

        # Update grid state and redraw to the surface
        # Pass height (rows) then width (cols)
        cells = update_grid(surface, cells, cellsize, grid_height, grid_width)

        # Update the actual display window
        pygame.display.flip()

    pygame.quit()
    print("Simulation finished.")

# --- Script Execution ---

if __name__ == "__main__":
    # Pass grid_width (columns) and grid_height (rows) to main
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, RANDOM_DENSITY)