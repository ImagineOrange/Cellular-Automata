#!/usr/bin/env python3.8
import pygame
import numpy as np
import time 

#colors
col_died = (69, 163, 177) # Color for state 2
col_alive = (253, 143, 0) # Color for state 1 (orange)
col_background = (10,10,40) # Background color (Blackblue)
col_grid = (30,30,60) # Color for grid lines if drawn (unused in current rect fill)
col_ant = (122, 163, 220) # Color for the ant (blue)

def main(width,height,cellsize):
    pygame.init()
    surface = pygame.display.set_mode((width*cellsize,height*cellsize)) #initialize display
    pygame.display.set_caption("L_Ant_Optimized")
    cells,ant = init(width,height) # Get initial grid state and ant state

    running = True # Use a flag for the main loop
    while running:
        for event in pygame.event.get(): #event loop: script will quit if user exits window
            if event.type == pygame.QUIT:
                running = False # Set flag to false to exit loop

        # --- Game Logic Update ---
        # Efficiently update only the ant and the cell it's on
        cells, ant = update_ant_and_grid(cells, ant, width, height)

        # --- Drawing ---
        # Draw the entire current state
        draw_simulation(surface, cells, ant, cellsize)

        # --- Display Update ---
        pygame.display.update() #update screen each generation

    pygame.quit() # Cleanly quit pygame
    return # Exit main function

def init(width,height):
    """Initializes the grid and the ant's starting state."""
    # Grid initialized with shape (width, height) -> (columns, rows)
    grid = np.zeros((width,height), dtype=int) # Use dtype for clarity
    # Calculate center (column index, row index)
    center_x, center_y = width // 2, height // 2
    # grid[(center_x, center_y)] = 1 # Start center as state 1 (optional, ant flips it immediately)
    # Ant format: (column_index, row_index, 'direction_char')
    ant = (center_x, center_y, 'r') # Start ant at center, facing right ('r')
    return grid, ant

def update_ant_and_grid(cells, ant, width, height):
    """
    Applies Langton's Ant rules:
    1. Checks cell state under ant.
    2. Flips the cell state.
    3. Turns the ant left or right based on the original cell state.
    4. Moves the ant forward one step.
    Operates efficiently without looping through the whole grid.
    """
    ax, ay, adir = ant # Unpack ant state (x=col, y=row, dir)
    # Ensure indices are integers (should be from init/previous step)
    ax, ay = int(ax), int(ay)

    current_cell_state = cells[ax, ay] # Get state of the cell the ant is on
    next_cells = cells # Modify the array directly (or use .copy() if cells needed elsewhere unmodified)

    # Apply Langton's Ant Rules (Modified for states 0, 1, 2)
    # Rule based on the state *before* flipping
    if current_cell_state == 1: # If on state 1 ("Alive")
        # Turn Left 90 degrees
        if adir == 'u': new_dir = 'l'
        elif adir == 'd': new_dir = 'r'
        elif adir == 'r': new_dir = 'u'
        else: # adir == 'l'
            new_dir = 'd'
        # Flip cell to state 2 ("Died")
        next_cells[ax, ay] = 2
    else: # If on state 0 ("Background") or State 2 ("Died")
        # Turn Right 90 degrees
        if adir == 'u': new_dir = 'r'
        elif adir == 'd': new_dir = 'l'
        elif adir == 'r': new_dir = 'd'
        else: # adir == 'l'
            new_dir = 'u'
        # Flip cell to state 1 ("Alive")
        next_cells[ax, ay] = 1

    # Move ant forward one step in the *new* direction
    if new_dir == 'u':   new_ay = (ay - 1) % height; new_ax = ax
    elif new_dir == 'd': new_ay = (ay + 1) % height; new_ax = ax
    elif new_dir == 'l': new_ax = (ax - 1) % width;  new_ay = ay
    else: # new_dir == 'r'
         new_ax = (ax + 1) % width;  new_ay = ay

    # Create the new ant state tuple
    new_ant = (new_ax, new_ay, new_dir)
    # Return the modified grid and new ant state
    return next_cells, new_ant

def draw_simulation(surface, cells, ant, cellsize):
    """Draws the current state of the grid and the ant."""
    surface.fill(col_background) # Fill background once per frame

    # Iterate through grid cells (x=col, y=row)
    for x, y in np.ndindex(cells.shape):
        cell_state = cells[x, y] # Access state using (col, row) index
        # Determine color based on state
        if cell_state == 1:
            color = col_alive
        elif cell_state == 2:
            color = col_died
        else: # cell_state == 0
            color = col_background # Or col_grid if you want empty cells visible

        # Draw rectangle for the cell if it's not background color
        # Optimization: avoid drawing background colored cells
        if color != col_background:
            # Pygame rect: (left, top, width, height)
            # left = column * cellsize, top = row * cellsize
            rect_left = x * cellsize
            rect_top = y * cellsize
            # Draw slightly smaller rect for grid effect if cellsize > 1
            rect_size = max(1, cellsize - 1)
            pygame.draw.rect(surface, color, (rect_left, rect_top, rect_size, rect_size))

    # Draw the ant distinctly after drawing the grid background
    ant_x, ant_y, _ = ant # Unpack ant position (x=col, y=row)
    ant_rect_left = int(ant_x * cellsize) # Ensure pixel coords are int
    ant_rect_top = int(ant_y * cellsize)
    ant_rect_size = max(1, cellsize - 1) # Match cell size for ant visual
    pygame.draw.rect(surface, col_ant, (ant_rect_left, ant_rect_top, ant_rect_size, ant_rect_size))

# --- Script Execution ---
if __name__ == "__main__": # Standard Python entry point check
    # Set grid dimensions and cell size here
    main(100, 100, 7) # Width=100 cols, Height=100 rows, CellSize=7 pixels