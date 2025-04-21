#!/usr/bin/env python3.8

"""
Pygame simulation demonstrating a cellular automaton growth pattern,
visually resembling snowflake or crystal formation.

The simulation starts with a seed pattern (circle) on a grid. In each step,
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
GRID_WIDTH = 130  # Number of columns
GRID_HEIGHT = 120 # Number of rows
CELL_SIZE = 6     # Size of each cell in pixels

# Simulation speed
FRAME_DELAY = .2  # Seconds to pause between updates (adjust as needed, e.g., 0.05 for faster)

# Initial Seed Pattern
# INITIAL_SQUARE_SIZE = 10 # (Using circle seed instead)
INITIAL_CIRCLE_RADIUS = 8 # Radius of the initial circle seed

# Frame Saving Options
SAVE_FRAMES = True  # Set to True to save each frame, False to disable
OUTPUT_DIR = "simulation_frames_circle" # Directory to save frames into
FRAME_FILENAME_PREFIX = "frame_circle" # Prefix for saved frame filenames

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
    """Creates the initial grid state with a circular seed pattern."""
    # Use (height, width) for (rows, columns) convention in NumPy
    cells = np.zeros((height, width), dtype=int) # CORRECTED LINE

    # Calculate center point (column index, row index)
    center_x, center_y = width // 2, height // 2

    # Calculate squared radius for distance comparison (more efficient)
    radius_squared = INITIAL_CIRCLE_RADIUS ** 2

    # Create coordinate arrays for vectorized calculation
    # cc holds column indices, rr holds row indices for each cell
    # Note: meshgrid default indexing 'xy' -> first arg varies fastest (cols)
    # Both cc and rr will have shape (height, width) matching cells array
    cc, rr = np.meshgrid(np.arange(width), np.arange(height))

    # Calculate squared distance from center for all cells simultaneously
    # Using (row - center_y)**2 + (col - center_x)**2
    dist_sq = (rr - center_y)**2 + (cc - center_x)**2

    # Create a boolean mask where distance is within the radius
    # Mask will have shape (height, width)
    mask = dist_sq <= radius_squared

    # Apply the mask: set cells within the circle to state 1
    # This works because cells and mask now have the same shape (height, width)
    cells[mask] = 1

    print(f"Grid initialized with a circle seed (radius={INITIAL_CIRCLE_RADIUS}).")
    return cells

def calculate_neighbor_sum(cells, r, c, width, height):
    """
    Calculates the sum of the values of the 8 adjacent neighbors (Moore neighborhood)
    to promote isotropic growth.
    Uses toroidal (wrap-around) boundary conditions. Assumes cells array has shape (height, width).

    Neighbors included: Top, Bottom, Left, Right, Top-Left, Top-Right, Bottom-Left, Bottom-Right.
         LA  T  RA
          L [C]  R
         BL  B  BR
    Sum = T + B + L + R + LA + RA + BL + BR

    Args:
        cells: The grid numpy array (shape: height, width).
        r: Row index of the current cell.
        c: Column index of the current cell.
        width: Number of columns in the grid.
        height: Number of rows in the grid.
    """
    # Calculate neighbor coordinates with wrap-around
    left_coord = (c - 1) % width
    right_coord = (c + 1) % width
    above_coord = (r - 1) % height
    below_coord = (r + 1) % height

    # Get values of all 8 neighbors using (row, col) indexing
    val_top_left = cells[above_coord, left_coord]
    val_top = cells[above_coord, c]
    val_top_right = cells[above_coord, right_coord] # Get Top-Right
    val_left = cells[r, left_coord]                # Get Left
    val_right = cells[r, right_coord]              # Get Right
    val_bottom_left = cells[below_coord, left_coord] # Get Bottom-Left
    val_bottom = cells[below_coord, c]
    val_bottom_right = cells[below_coord, right_coord]

    # Calculate the sum using the Moore neighborhood (all 8 neighbors)
    neighbor_sum = (
        val_top_left + val_top + val_top_right +
        val_left + val_right +                 # Center cell [r, c] is excluded
        val_bottom_left + val_bottom + val_bottom_right
    )

    return int(neighbor_sum) # Ensure integer sum

def update_grid(surface, current_cells, cell_size, width, height):
    """
    Updates the grid based on neighbor sums and draws the new state.
    Assumes current_cells array has shape (height, width).

    The state of a cell in the *next* generation depends on the
    sum of specific neighbors in the *current* generation.
    The color displayed corresponds to the neighbor sum condition met.
    """
    # Initialize next state grid with the same shape as current_cells (height, width)
    next_grid_state = np.zeros_like(current_cells)

    # Iterate through all cells using (row, column) indices
    for r, c in np.ndindex(current_cells.shape):
        neighbor_sum = calculate_neighbor_sum(current_cells, r, c, width, height)

        # --- Cellular Automaton Rules ---
        # Determine the next state and color based on the neighbor sum
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
        # Pygame rect uses (left, top, width, height) -> (x, y, w, h)
        # x coordinate corresponds to column (c), y coordinate corresponds to row (r)
        rect_x = c * cell_size
        rect_y = r * cell_size
        # Leave 1px gap for grid effect if cell_size > 1
        rect_size = max(1, cell_size - 1)
        rect = (rect_x, rect_y, rect_size, rect_size)
        pygame.draw.rect(surface, cell_color, rect)

    # Add a delay to control animation speed
    time.sleep(FRAME_DELAY)
    return next_grid_state

def main(grid_width, grid_height, cellsize):
    """Initializes Pygame and runs the main simulation loop."""
    pygame.init()
    # Screen dimensions in pixels: (width, height)
    screen_width = grid_width * cellsize
    screen_height = grid_height * cellsize
    surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Cellular Automaton Growth Simulation")

    # Pass grid_width (cols) and grid_height (rows) to initialize_grid
    cells = initialize_grid(grid_width, grid_height)

    # --- Setup for Frame Saving ---
    frame_count = 0
    if SAVE_FRAMES:
        # Create the output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Saving frames enabled. Outputting to directory: '{OUTPUT_DIR}'")
    # --- End Setup for Frame Saving ---

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add other event handling here if needed (e.g., keyboard input)

        # Fill background each frame before drawing updated cells
        surface.fill(COLOR_BACKGROUND)

        # Update grid state and redraw to the surface
        # Pass grid_width (cols) and grid_height (rows) consistently
        cells = update_grid(surface, cells, cellsize, grid_width, grid_height)

        # --- Save Frame If Enabled ---
        if SAVE_FRAMES:
            frame_count += 1
            # Format filename with leading zeros for sorting (e.g., frame_circle_0001.jpg)
            filename = f"{FRAME_FILENAME_PREFIX}_{frame_count:04d}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            try:
                pygame.image.save(surface, filepath)
            except pygame.error as e:
                print(f"Error saving frame {frame_count}: {e}")
                # Optionally stop saving or simulation if errors persist
                # running = False
        # --- End Save Frame ---

        # Update the actual display window
        pygame.display.flip()

    pygame.quit()
    print("Simulation finished.")
    if SAVE_FRAMES:
        print(f"Saved {frame_count} frames to '{OUTPUT_DIR}'.")


# --- Script Execution ---

if __name__ == "__main__":
    # Pass GRID_WIDTH (columns) and GRID_HEIGHT (rows) to main
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)