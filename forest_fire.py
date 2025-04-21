import pygame
import numpy as np
import random
import time

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 150
GRID_HEIGHT = 100
CELL_SIZE = 6  # Size of each cell in pixels

# Simulation Parameters
P_GROWTH = 0.001   # Probability of empty cell becoming a tree
P_IGNITION = 0.00001 # Probability of tree catching fire spontaneously (lightning)
# Fire spread is guaranteed if neighbor is burning in this simple model

# Simulation speed
FRAME_DELAY = 0.05  # Seconds to pause between updates

# Cell States
STATE_EMPTY = 0
STATE_TREE = 1
STATE_BURNING = 2

# Colors (RGB tuples)
COLOR_EMPTY = (30, 20, 10)      # Dark Brown/Black for empty ground
COLOR_TREE = (0, 100, 20)       # Dark Green for trees
COLOR_BURNING = (255, 100, 0)   # Orange/Red for fire
COLOR_GRID = (50, 40, 30)       # Subtle grid lines (if needed)

# --- Simulation Logic ---

def initialize_grid(width, height, initial_tree_density=0.6):
    """Creates the initial grid state, mostly trees."""
    # Use (height, width) for NumPy array shape (rows, columns)
    cells = np.random.choice(
        [STATE_EMPTY, STATE_TREE],
        size=(height, width),
        p=[1 - initial_tree_density, initial_tree_density]
    )
    print(f"Grid initialized with ~{initial_tree_density * 100:.1f}% trees.")
    return cells

def update_forest_fire(current_cells, height, width):
    """
    Updates the grid based on forest fire rules:
    1. Burning cell -> Empty cell
    2. Tree cell -> Burning if neighbor burns OR random ignition
    3. Empty cell -> Tree by random growth
    Assumes current_cells array has shape (height, width).
    """
    next_grid_state = current_cells.copy() # Start with current state

    for r in range(height):
        for c in range(width):
            current_state = current_cells[r, c]

            # --- Rule 1: Burning cells burn out ---
            if current_state == STATE_BURNING:
                next_grid_state[r, c] = STATE_EMPTY
                continue # Cell is now empty, no further rules apply this step

            # --- Rule 2: Trees potentially catch fire ---
            if current_state == STATE_TREE:
                # Check Moore neighborhood for burning neighbors
                is_neighbor_burning = False
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0: continue # Skip self
                        nr, nc = (r + i) % height, (c + j) % width
                        if current_cells[nr, nc] == STATE_BURNING:
                            is_neighbor_burning = True
                            break # Found one burning neighbor, no need to check more
                    if is_neighbor_burning: break

                # Apply fire spread or random ignition
                if is_neighbor_burning or (random.random() < P_IGNITION):
                    next_grid_state[r, c] = STATE_BURNING
                # else: Tree remains a Tree (already set in copy)
                continue # Cell state determined, go to next cell

            # --- Rule 3: Empty cells potentially grow trees ---
            if current_state == STATE_EMPTY:
                if random.random() < P_GROWTH:
                    next_grid_state[r, c] = STATE_TREE
                # else: Empty remains Empty (already set in copy)

    return next_grid_state

# --- Drawing Logic ---

def draw_grid(surface, cells, cell_size):
    """Draws the forest grid."""
    height, width = cells.shape
    for r in range(height):
        for c in range(width):
            state = cells[r, c]
            if state == STATE_TREE:
                color = COLOR_TREE
            elif state == STATE_BURNING:
                color = COLOR_BURNING
            else: # state == STATE_EMPTY
                color = COLOR_EMPTY

            rect_x = c * cell_size
            rect_y = r * cell_size
            pygame.draw.rect(surface, color, (rect_x, rect_y, cell_size, cell_size))

# --- Main Function ---

def main(grid_width, grid_height, cellsize):
    """Initializes Pygame and runs the main simulation loop."""
    pygame.init()
    screen_width = grid_width * cellsize
    screen_height = grid_height * cellsize
    surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Forest Fire Simulation")

    # Initialize grid - pass height (rows) then width (cols)
    cells = initialize_grid(grid_width, grid_height)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add event handling here (e.g., click to start fire)
            if event.type == pygame.MOUSEBUTTONDOWN:
                 # Get mouse position and convert to grid coordinates
                 mouse_x, mouse_y = event.pos
                 grid_c = mouse_x // cellsize
                 grid_r = mouse_y // cellsize
                 # Check bounds
                 if 0 <= grid_r < grid_height and 0 <= grid_c < grid_width:
                     # Start a fire at the clicked tree cell
                     if cells[grid_r, grid_c] == STATE_TREE:
                          cells[grid_r, grid_c] = STATE_BURNING
                          print(f"Fire started at ({grid_r}, {grid_c})")


        # --- Simulation Step ---
        # Pass height (rows) then width (cols)
        cells = update_forest_fire(cells, grid_height, grid_width)

        # --- Drawing ---
        # No need to fill background if empty cells are drawn
        draw_grid(surface, cells, cellsize)

        # --- Display Update ---
        pygame.display.flip()
        time.sleep(FRAME_DELAY) # Control speed

    pygame.quit()
    print("Simulation finished.")

# --- Script Execution ---

if __name__ == "__main__":
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)