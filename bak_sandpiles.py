#!/usr/bin/env python3.8

# Bak-Tang-Wiesenfeld Sandpile Model Simulation
# Current time: Monday, April 21, 2025 at 12:06:46 AM MDT
# Location: Boulder, Colorado, United States

import pygame
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress # Import for linear regression
import warnings # To ignore log(0) warnings if necessary
import os # os module is not strictly needed here, but was imported before

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 100 # Grid dimensions (GRID_SIZE x GRID_SIZE)
CELL_SIZE = WIDTH // GRID_SIZE
# FPS = 60 # Set FPS > 0 to control simulation speed, 0 for max speed
SAND_DROPS_PER_FRAME = 5 # Add multiple grains per frame to speed up reaching criticality

# --- Style Enhancements ---
# Pygame Colors
BACKGROUND_COLOR = (15, 15, 25) # Darker background
PYGAME_COLORS = [
    (15, 15, 25),     # Level 0 (matches background)
    (30, 60, 100),    # Level 1 (Dark Blue)
    (80, 40, 120),    # Level 2 (Purple)
    (180, 70, 100),   # Level 3 (Magenta/Pink)
    (240, 240, 50)    # Level 4 or higher (Bright Yellow for contrast)
]

# Matplotlib Style
plt.style.use('dark_background')
# --- End Style Enhancements ---

# Initialize grid - THIS IS A GLOBAL VARIABLE
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Per Bak's Criticality Model - Sandpile")
clock = pygame.time.Clock()

# Avalanche size tracker - GLOBAL VARIABLE
avalanche_sizes = []
# Total drops tracker - GLOBAL VARIABLE
total_drops = 0

def add_sand(x, y):
    """Add a grain of sand at the specified cell."""
    global grid, total_drops # Declare intention to modify global variables
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        # Note: Pygame grid uses (x, y) coordinates, NumPy array uses (row, col) -> (y, x)
        grid[y, x] += 1
        total_drops += 1 # Increment global drop count

def topple():
    """
    Performs the toppling operation for the grid iteratively until stable
    and returns the total size of the avalanche chain reaction for this step.
    Uses a while loop to avoid recursion depth errors.
    """
    global grid # Declare intention to use and modify the global grid
    total_avalanche_size_for_this_drop = 0

    # Loop as long as there are any unstable cells (>= 4) anywhere on the grid
    while np.any(grid >= 4):
        # Find all cells that currently need to topple in this pass
        topple_indices_y, topple_indices_x = np.where(grid >= 4)

        # If somehow no indices were found but the while condition was true, break (safety check)
        if len(topple_indices_y) == 0:
             break

        # Create a temporary grid JUST for the additions from this specific pass
        additions = np.zeros_like(grid)
        # Count how many cells toppled in *this specific pass*
        num_topples_this_pass = len(topple_indices_y)
        # Add this pass's topples to the total avalanche size
        total_avalanche_size_for_this_drop += num_topples_this_pass

        # Process all cells identified for toppling in this pass
        for y, x in zip(topple_indices_y, topple_indices_x):
             grid[y, x] -= 4 # Decrease the unstable cell itself

             # Add sand to neighbors in the temporary additions grid
             # (Boundary checks ensure we don't add outside the grid)
             if x > 0: additions[y, x - 1] += 1
             if x < GRID_SIZE - 1: additions[y, x + 1] += 1
             if y > 0: additions[y - 1, x] += 1
             if y < GRID_SIZE - 1: additions[y + 1, x] += 1

        # Add the accumulated additions from THIS PASS back to the main grid
        grid += additions
        # The while condition will then re-evaluate if any cells (including those
        # that just received sand) are now >= 4, triggering the next pass if needed.

    # Once the loop finishes (no cells >= 4), return the total accumulated size
    return total_avalanche_size_for_this_drop

def record_avalanche(size):
    """Records non-zero avalanche sizes."""
    global avalanche_sizes # Declare intention to modify global list
    if size > 0:
        avalanche_sizes.append(size)

def draw_grid():
    """Draw the sandpile grid on the screen."""
    screen.fill(BACKGROUND_COLOR) # Fill background once
    # Get indices where grid > 0 for optimized drawing
    non_zero_indices_y, non_zero_indices_x = np.where(grid > 0)

    for y, x in zip(non_zero_indices_y, non_zero_indices_x):
        # Clamp color index to the available colors
        color_index = min(grid[y, x], len(PYGAME_COLORS) - 1)
        color = PYGAME_COLORS[color_index]
        # Draw slightly smaller rect for grid effect if desired
        # Pygame rect is (left, top, width, height) -> (x*cs, y*cs, cs, cs)
        pygame.draw.rect(
            screen,
            color,
            (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE -1, CELL_SIZE -1)
        )

# --- Enhanced Plotting Function ---
def plot_avalanches_enhanced():
    """
    Plots the avalanche sizes on a log-log plot with dark style,
    calculates and shows the power-law fit exponent.
    """
    global avalanche_sizes, total_drops # Access global variables for plotting stats

    if not avalanche_sizes:
        print("No avalanches recorded to plot.")
        return

    plt.figure(figsize=(10, 8)) # Slightly larger figure

    # Use numpy.histogram to get counts and bins
    # Ensure bins cover the full range, add +1 for log upper bound
    min_size = min(avalanche_sizes) if avalanche_sizes else 1
    max_size = max(avalanche_sizes) if avalanche_sizes else 1
    # Create log-spaced bins from min to max avalanche size
    # Adding a small epsilon to min_size if it's 0 for log10, though avalanche size should be >= 1
    bins = np.logspace(np.log10(max(1, min_size)), np.log10(max_size + 1), 50)
    counts, bin_edges = np.histogram(avalanche_sizes, bins=bins)

    # Calculate bin centers (use geometric mean for log bins is often preferred)
    # bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:]) # Geometric mean

    # Filter out bins with zero counts for log fitting
    nonzero_mask = counts > 0
    filtered_centers = bin_centers[nonzero_mask]
    filtered_counts = counts[nonzero_mask]

    if len(filtered_centers) < 2:
        print("Not enough data points with non-zero counts for fitting.")
        # Plot scatter even if fitting fails
        plt.scatter(filtered_centers, filtered_counts, alpha=0.7, color='cyan', label='Avalanche Counts')
    else:
        # --- Power-Law Fit ---
        log_x = np.log10(filtered_centers)
        log_y = np.log10(filtered_counts)

        # Optional: Select a range for fitting (can improve exponent estimate)
        # This often requires domain knowledge or visual inspection
        # Example: fit_mask = (filtered_centers > 10) & (filtered_centers < max_size / 10)
        # log_x_fit = log_x[fit_mask] # Apply mask if defined
        # log_y_fit = log_y[fit_mask]
        # For simplicity, fit all non-zero points first:
        log_x_fit = log_x
        log_y_fit = log_y

        # Ignore RuntimeWarning for invalid value encountered in log10 if any zero counts slip through
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            slope, intercept, r_value, p_value, std_err = linregress(log_x_fit, log_y_fit)

        # Calculate exponent tau for P(s) ~ s^-tau
        # Slope here is for log(N(s)) vs log(s). N(s) is frequency (count).
        # Probability density P(s) ~ N(s) / s (approximately, related to bin width)
        # So log(P(s)) ~ log(N(s)) - log(s) = (slope * log(s) + intercept) - log(s)
        # log(P(s)) ~ (slope - 1) * log(s) + intercept
        # The exponent for P(s) is -(slope - 1) = 1 - slope
        tau_exponent = 1.0 - slope

        print(f"Fit Results: Slope={slope:.3f}, Intercept={intercept:.3f}, R^2={r_value**2:.3f}")
        print(f"Estimated Power-Law Exponent τ (for P(s)~s^-τ) ≈ {tau_exponent:.3f}")

        # Plot scatter of histogram data
        plt.scatter(filtered_centers, filtered_counts, alpha=0.7, s=30, color='cyan', label='Avalanche Counts')

        # Plot the fit line over the range it was fit to
        fit_line_log_y = slope * log_x_fit + intercept
        plt.plot(10**log_x_fit, 10**fit_line_log_y, color='red', linestyle='--', linewidth=2,
                 label=f'Fit (Slope ≈ {slope:.2f}, τ ≈ {tau_exponent:.2f})')
        # --- End Power-Law Fit ---
        plt.legend()

    # --- Plot Styling ---
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Avalanche Size (s)', fontsize=12)
    plt.ylabel('Frequency (N(s))', fontsize=12)
    plt.title(f'Avalanche Size Distribution (Log-Log) - {len(avalanche_sizes)} Avalanches Recorded', fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5) # Add grid lines
    plt.figtext(0.5, 0.01, f'Total Sand Drops: {total_drops}', ha='center', fontsize=10, alpha=0.8)
    # --- End Plot Styling ---

    plt.tight_layout() # Adjust layout to prevent labels overlapping
    plt.show()
# --- End Enhanced Plotting Function ---


def main():
    """Main simulation loop."""
    running = True
    paused = False # Add pause state
    frame_count = 0

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Toggle pause
                    paused = not paused
                    print("Paused" if paused else "Resumed")
                if event.key == pygame.K_p: # Plot current data on demand
                     if avalanche_sizes:
                         print("\nPlotting current avalanche data...")
                         plot_avalanches_enhanced()
                     else:
                         print("No avalanches recorded yet.")
        # --- End Event Handling ---

        if not paused:
            # --- Simulation Step ---
            for _ in range(SAND_DROPS_PER_FRAME):
                 # Add sand to the center
                 add_sand(GRID_SIZE // 2, GRID_SIZE // 2)
                 # Perform toppling immediately after adding sand to catch the resulting avalanche
                 avalanche_this_step = topple()
                 record_avalanche(avalanche_this_step) # Record size if > 0
            # --- End Simulation Step ---

            frame_count += 1

            # Optional: Print status periodically
            if frame_count % 100 == 0:
                 print(f"Frames: {frame_count}, Drops: {total_drops}, Avalanches Recorded: {len(avalanche_sizes)}")


        # --- Drawing ---
        draw_grid() # Draw the current state

        # --- Display Update ---
        pygame.display.flip()
        # clock.tick(FPS) # Uncomment and set FPS > 0 to limit simulation speed

    pygame.quit()

    # Plot avalanche sizes after the simulation ends
    print(f"\nSimulation ended. Total Drops: {total_drops}, Avalanches Recorded: {len(avalanche_sizes)}.")
    print("Plotting final avalanche data...")
    plot_avalanches_enhanced()

if __name__ == "__main__":
    main()