#!/usr/bin/env python3.8

"""
Pygame simulation demonstrating a cellular automaton growth pattern,
visually resembling snowflake or crystal formation.

The simulation starts with a few seed cells on a grid. In each step,
the state and color of each cell in the *next* generation are determined
by the sum of the values of specific neighbors in the *current* generation.
The grid wraps around (toroidal boundaries).
"""

import pygame
import numpy as np
import time

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 130
GRID_HEIGHT = 120
CELL_SIZE = 6  # Size of each cell in pixels

# Simulation speed
FRAME_DELAY = 0.1  # Seconds to pause between updates (e.g., 0.1 for faster)

# Colors (RGB tuples)
COLOR_BACKGROUND = (10, 10, 40)     # Dark blue background
COLOR_STATE_1 = (112, 178, 252)     # Bluer
COLOR_STATE_2 = (153, 242, 186)     # Mint
COLOR_STATE_3 = (255, 136, 6)       # Orange
COLOR_STATE_4 = (255, 57, 123)      # Red
COLOR_STATE_5 = (249, 204, 164)     # Yellowish
COLOR_STATE_6 = (188, 233, 254)     # Frozen/Light Blue
COLOR_STATE_7 = (250, 116, 219)     # Pink/Magenta (was 'e')
COLOR_FALLBACK = COLOR_BACKGROUND   # Color if no rule matches

# --- Main Simulation Logic ---

def initialize_grid(width, height):
    """Creates the initial grid state with seed points."""
    cells = np.zeros((width, height), dtype=int) # Use int dtype

    # Define starting seed points (relative to grid center)
    center_x, center_y = width // 2, height // 2
    quarter_x, quarter_y = width // 4, height // 4

    # Seed points - Values 1 and 2 seem to represent initial states
    # Naming is still a bit abstract, reflects original structure
    point_center = (center_x, center_y)
    point_mid_right = (center_x + quarter_x, center_y)
    point_mid_left = (center_x - quarter_x, center_y)
    point_top_left_q = (quarter_x, quarter_y)
    point_top_center_q = (center_x, quarter_y)
    point_bottom_center_q = (center_x, center_y + quarter_y)
    point_bottom_right_q = (center_x + quarter_x, center_y + quarter_y)

    # Apply seeds to the grid
    cells[point_center] = 1
    cells[point_mid_right] = 1 # Was 2 then 1 in original, setting to 1
    cells[point_mid_left] = 1
    cells[point_top_left_q] = 2
    cells[point_top_center_q] = 2
    cells[point_bottom_center_q] = 2
    cells[point_bottom_right_q] = 2
   

    print("Grid initialized with seed points.")
    return cells

def calculate_neighbor_sum(cells, r, c, width, height):
    """
    Calculates the sum of the values of a specific, non-standard set of neighbors.
    Uses toroidal (wrap-around) boundary conditions.

    Neighbors included: Top, Bottom, Top-Left, Bottom-Right.
         (LA) T  (RA)
          L  [C]  R
         (BL) B  (BR)
    Sum = T + B + LA + BR
    """
    # Calculate neighbor coordinates with wrap-around
    left_coord = (r - 1) % width
    right_coord = (r + 1) % width
    above_coord = (c - 1) % height
    below_coord = (c + 1) % height

    # Get values of the specific neighbors
    val_top_left = cells[left_coord, above_coord]
    val_top = cells[r, above_coord]
    # val_top_right = cells[right_coord, above_coord] # Not used
    # val_left = cells[left_coord, c]                # Not used
    # val_right = cells[right_coord, c]              # Not used
    # val_bottom_left = cells[left_coord, below_coord] # Not used
    val_bottom = cells[r, below_coord]
    val_bottom_right = cells[right_coord, below_coord]

    # Calculate the sum based on the specific rule
    neighbor_sum = val_top + val_bottom + val_top_left + val_bottom_right
    return int(neighbor_sum) # Ensure integer sum

def update_grid(surface, current_cells, cell_size, width, height):
    """
    Updates the grid based on neighbor sums and draws the new state.

    The state of a cell in the *next* generation depends on the
    sum of specific neighbors in the *current* generation.
    The color displayed corresponds to the neighbor sum condition met.
    """
    next_grid_state = np.zeros_like(current_cells) # Initialize next state grid

    for r, c in np.ndindex(current_cells.shape): # Iterate through all cells
        neighbor_sum = calculate_neighbor_sum(current_cells, r, c, width, height)

        # --- Cellular Automaton Rules ---
        # Determine the next state and color based on the neighbor sum
        # These rules define the growth pattern. Modify them for different visuals.
        new_state = 0 # Default to state 0 (dead/background)
        cell_color = COLOR_FALLBACK # Default color

        if neighbor_sum == 1:
            new_state = 1
            cell_color = COLOR_STATE_1 # Bluer
        elif neighbor_sum == 2:
            new_state = 2
            cell_color = COLOR_STATE_2 # Mint
        elif neighbor_sum == 3:
            new_state = 0 
            cell_color = COLOR_STATE_3 # Orange
        elif neighbor_sum == 4:
            new_state = 0 
            cell_color = COLOR_STATE_4 # Red
        elif neighbor_sum == 5:
            new_state = 1
            cell_color = COLOR_STATE_5 # Yellowish
        elif neighbor_sum == 6:
            new_state = 0 
            cell_color = COLOR_STATE_1 # Bluer (Re-used)
        elif neighbor_sum == 7:
            new_state = 0
            cell_color = COLOR_STATE_2 # Mint (Re-used)
        elif neighbor_sum == 8:
            new_state = 3
            cell_color = COLOR_STATE_3 # Orange (Re-used)
        elif neighbor_sum == 9:
            new_state = 5 # State 5 wasn't defined by color, maps to COLOR_STATE_4?
            cell_color = COLOR_STATE_4 # Red (Re-used)
        elif neighbor_sum == 10:
            new_state = 1
            cell_color = COLOR_STATE_5 # Yellowish (Re-used)
        elif neighbor_sum == 11:
            new_state = 2
            cell_color = COLOR_STATE_1 # Bluer (Re-used)
        elif neighbor_sum == 12:
            new_state = 3
            cell_color = COLOR_STATE_4 # Red (Re-used)
        elif neighbor_sum == 13:
            new_state = 4 # State 4 wasn't defined by color, maps to COLOR_STATE_6?
            cell_color = COLOR_STATE_6 # Frozen/Light Blue
        elif neighbor_sum == 14:
            new_state = 5
            cell_color = COLOR_STATE_5 # Yellowish (Re-used)
        elif neighbor_sum == 15:
            new_state = 4
            cell_color = COLOR_STATE_7 # Pink/Magenta (was 'e')
        # Else: new_state remains 0, cell_color remains COLOR_FALLBACK

        next_grid_state[r, c] = new_state

        # Draw the cell for the *current* step based on the calculated color
        # (Color represents the condition met based on *previous* neighbors)
        rect = (r * cell_size, c * cell_size, cell_size - 1, cell_size - 1) # Leave 1px gap
        pygame.draw.rect(surface, cell_color, rect)

    # Add a delay to control animation speed
    time.sleep(FRAME_DELAY)
    return next_grid_state

def main(width, height, cellsize):
    """Initializes Pygame and runs the main simulation loop."""
    pygame.init()
    screen_width = width * cellsize
    screen_height = height * cellsize
    surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Cellular Automaton Growth Simulation")

    cells = initialize_grid(width, height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill background each frame before drawing updated cells
        surface.fill(COLOR_BACKGROUND)

        # Update grid state and redraw
        cells = update_grid(surface, cells, cellsize, width, height)

        # Update the display
        pygame.display.flip() # Use flip for full surface update

    pygame.quit()
    print("Simulation finished.")

# --- Script Execution ---

if __name__ == "__main__":
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)