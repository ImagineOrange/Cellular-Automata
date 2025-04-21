import pygame
import numpy as np
import time

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 150
GRID_HEIGHT = 100
CELL_SIZE = 7  # Size of each cell in pixels

# Simulation speed
FRAME_DELAY = 0.02  # Seconds to pause between updates (Brian's Brain often looks good slightly slower)

# Initial state probability (density of 'Firing' cells)
INITIAL_FIRING_DENSITY = 0.3 # Adjust as needed

# Cell States
STATE_OFF = 0
STATE_FIRING = 1
STATE_REFRACTORY = 2 # Often called 'dying'

# Colors (RGB tuples)
COLOR_OFF = (10, 10, 40)     # Dark blue background (matches background)
COLOR_FIRING = (255, 255, 150)    # Bright Yellow for 'Firing' state
COLOR_REFRACTORY = (100, 100, 200)   # Blue/Purple for 'Refractory' state
COLOR_GRID = (30, 30, 60)       # Grid lines (subtle)

# --- Main Simulation Logic ---

def initialize_grid(width, height, firing_density):
    """Creates the initial grid state with random 'Firing' cells."""
    # Use (height, width) for NumPy array shape (rows, columns)
    # Start all cells as OFF
    cells = np.zeros((height, width), dtype=int)
    # Randomly set some cells to the FIRING state based on density
    num_firing = int(width * height * firing_density)
    firing_indices_r = np.random.randint(0, height, size=num_firing)
    firing_indices_c = np.random.randint(0, width, size=num_firing)
    cells[firing_indices_r, firing_indices_c] = STATE_FIRING

    print(f"Grid initialized with random firing density: {firing_density * 100:.1f}%")
    return cells

def count_firing_neighbors(cells, r, c, height, width):
    """
    Counts the number of 'Firing' neighbors (State 1) for a cell at (r, c)
    using Moore neighborhood and toroidal boundary conditions.
    Assumes cells array has shape (height, width).
    """
    total_firing = 0
    # Iterate through the 3x3 neighborhood centered at (r, c)
    for i in range(-1, 2):
        for j in range(-1, 2):
            # Skip the center cell itself
            if i == 0 and j == 0:
                continue

            # Calculate neighbor coordinates with wrap-around
            neighbor_r = (r + i) % height
            neighbor_c = (c + j) % width

            # Check if the neighbor is in the FIRING state
            if cells[neighbor_r, neighbor_c] == STATE_FIRING:
                total_firing += 1

    return int(total_firing)

def update_grid(surface, current_cells, cell_size, height, width):
    """
    Updates the grid based on the Brian's Brain rules and draws the new state.
    Assumes current_cells array has shape (height, width).
    """
    # Initialize next state grid with the same shape (height, width)
    next_grid_state = np.zeros_like(current_cells)

    # Iterate through all cells using (row, column) indices
    for r, c in np.ndindex(current_cells.shape):
        current_state = current_cells[r, c]
        next_state = STATE_OFF # Default to OFF

        # --- Brian's Brain Rules ---
        if current_state == STATE_REFRACTORY:
            next_state = STATE_OFF # Refractory always becomes Off
        elif current_state == STATE_FIRING:
            next_state = STATE_REFRACTORY # Firing always becomes Refractory
        elif current_state == STATE_OFF:
            # Check neighbors only if the cell is OFF
            firing_neighbors = count_firing_neighbors(current_cells, r, c, height, width)
            if firing_neighbors == 2:
                next_state = STATE_FIRING # Off becomes Firing if exactly 2 neighbors are Firing
            else:
                next_state = STATE_OFF # Otherwise, stays Off
        # Else case should not happen if states are 0, 1, 2

        next_grid_state[r, c] = next_state

        # --- Drawing ---
        # Determine color based on the *next* state
        if next_state == STATE_FIRING:
            cell_color = COLOR_FIRING
        elif next_state == STATE_REFRACTORY:
            cell_color = COLOR_REFRACTORY
        else: # next_state == STATE_OFF
            cell_color = COLOR_OFF

        # Pygame rect uses (left, top, width, height) -> (x, y, w, h)
        rect_x = c * cell_size
        rect_y = r * cell_size
        rect_width = max(1, cell_size - 1)
        rect_height = max(1, cell_size - 1)
        rect = (rect_x, rect_y, rect_width, rect_height)

        # Draw only if the color is not the background (optimization)
        if cell_color != COLOR_OFF:
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
    pygame.display.set_caption("Brian's Brain Cellular Automaton")

    # Initialize grid - pass height (rows) then width (cols)
    cells = initialize_grid(grid_width, grid_height, density)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add other event handling here (e.g., pause, reset, click to change state)

        # Fill background each frame
        surface.fill(COLOR_OFF) # Use OFF color as background

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
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, INITIAL_FIRING_DENSITY)