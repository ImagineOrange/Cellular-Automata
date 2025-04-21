#!/usr/bin/env python3.8

"""
Pygame simulation demonstrating a cellular automaton growth pattern,
visually resembling snowflake or crystal formation.

The simulation starts with a seed pattern on a grid. In each step,
the state and color of each cell in the *next* generation are determined
by the sum of the values of specific neighbors in the *current* generation.
The grid wraps around (toroidal boundaries).

Includes optional frame saving.
"""

import pygame
import numpy as np
import time
import os # Import the os module for directory operations

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 130
GRID_HEIGHT = 120
CELL_SIZE = 6  # Size of each cell in pixels

# Simulation speed
FRAME_DELAY = 0.5  # Seconds to pause between updates (e.g., 0.1 for faster)

# Initial Seed Pattern
INITIAL_SQUARE_SIZE = 10 # Size of the initial square seed

# Frame Saving Options
SAVE_FRAMES = True  # Set to True to save each frame, False to disable
OUTPUT_DIR = "simulation_frames" # Directory to save frames into
FRAME_FILENAME_PREFIX = "frame" # Prefix for saved frame filenames

# Colors (RGB tuples)
COLOR_BACKGROUND = (10, 10, 40)     # Dark blue background
COLOR_STATE_1 = (112, 178, 252)     # Bluer
COLOR_STATE_2 = (153, 242, 186)     # Mint
COLOR_STATE_3 = (255, 136, 6)       # Orange
COLOR_STATE_4 = (255, 57, 123)      # Red
COLOR_STATE_5 = (249, 204, 164)     # Yellowish
COLOR_STATE_6 = (188, 233, 254)     # Frozen/Light Blue
COLOR_STATE_7 = (250, 116, 219)     # Pink/Magenta
COLOR_FALLBACK = COLOR_BACKGROUND   # Color if no rule matches

# --- Main Simulation Logic ---

def initialize_grid(width, height):
    """Creates the initial grid state with a square seed pattern."""
    cells = np.zeros((width, height), dtype=int)

    # Calculate center point
    center_x, center_y = width // 2, height // 2

    # Calculate top-left corner of the square for centering
    start_x = center_x - INITIAL_SQUARE_SIZE // 2
    start_y = center_y - INITIAL_SQUARE_SIZE // 2

    # Ensure start coordinates are within bounds (optional, good practice)
    start_x = max(0, start_x)
    start_y = max(0, start_y)

    # Calculate end coordinates (exclusive)
    end_x = min(width, start_x + INITIAL_SQUARE_SIZE)
    end_y = min(height, start_y + INITIAL_SQUARE_SIZE)

    # Set the cells within the square to state 1 using slicing
    cells[start_x:end_x, start_y:end_y] = 1

    print(f"Grid initialized with a {INITIAL_SQUARE_SIZE}x{INITIAL_SQUARE_SIZE} square seed.")
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
            cell_color = COLOR_STATE_1
        elif neighbor_sum == 2:
            new_state = 2
            cell_color = COLOR_STATE_2
        elif neighbor_sum == 3:
            new_state = 0
            cell_color = COLOR_STATE_3
        elif neighbor_sum == 4:
            new_state = 0
            cell_color = COLOR_STATE_4
        elif neighbor_sum == 5:
            new_state = 1
            cell_color = COLOR_STATE_5
        elif neighbor_sum == 6:
            new_state = 0
            cell_color = COLOR_STATE_1
        elif neighbor_sum == 7:
            new_state = 0
            cell_color = COLOR_STATE_2
        elif neighbor_sum == 8:
            new_state = 3
            cell_color = COLOR_STATE_3
        elif neighbor_sum == 9:
            new_state = 5
            cell_color = COLOR_STATE_4
        elif neighbor_sum == 10:
            new_state = 1
            cell_color = COLOR_STATE_5
        elif neighbor_sum == 11:
            new_state = 2
            cell_color = COLOR_STATE_1
        elif neighbor_sum == 12:
            new_state = 3
            cell_color = COLOR_STATE_4
        elif neighbor_sum == 13:
            new_state = 4
            cell_color = COLOR_STATE_6
        elif neighbor_sum == 14:
            new_state = 5
            cell_color = COLOR_STATE_5
        elif neighbor_sum == 15:
            new_state = 4
            cell_color = COLOR_STATE_7
        # Else: new_state remains 0, cell_color remains COLOR_FALLBACK

        next_grid_state[r, c] = new_state

        # Draw the cell for the *current* step based on the calculated color
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

    # --- Setup for Frame Saving ---
    frame_count = 0
    if SAVE_FRAMES:
        # Create the output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Saving frames enabled. Outputting to directory: '{OUTPUT_DIR}'")
    # --- End Setup for Frame Saving ---

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill background each frame before drawing updated cells
        surface.fill(COLOR_BACKGROUND)

        # Update grid state and redraw to the surface
        cells = update_grid(surface, cells, cellsize, width, height)

        # --- Save Frame If Enabled ---
        if SAVE_FRAMES:
            frame_count += 1
            # Format filename with leading zeros for sorting (e.g., frame_0001.jpg)
            filename = f"{FRAME_FILENAME_PREFIX}_{frame_count:04d}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            try:
                pygame.image.save(surface, filepath)
            except pygame.error as e:
                print(f"Error saving frame {frame_count}: {e}")
                # Optionally stop saving if an error occurs frequently
                # SAVE_FRAMES = False
        # --- End Save Frame ---

        # Update the actual display window
        pygame.display.flip()

    pygame.quit()
    print("Simulation finished.")
    if SAVE_FRAMES:
        print(f"Saved {frame_count} frames to '{OUTPUT_DIR}'.")


# --- Script Execution ---

if __name__ == "__main__":
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)