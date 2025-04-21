import pygame
import numpy as np
import math
import random
import time

# --- Configuration Constants ---

# Grid dimensions
GRID_WIDTH = 180
GRID_HEIGHT = 120
CELL_SIZE = 6  # Size of each cell in pixels

# Simulation Parameters
J = 1.0  # Interaction energy (usually 1)
KB = 1.0 # Boltzmann constant (often set to 1 in simulations)
INITIAL_TEMP = 3.5 # Initial temperature
MIN_TEMP = 0.1
MAX_TEMP = 5.0
MONTE_CARLO_STEPS_PER_FRAME = GRID_WIDTH * GRID_HEIGHT # Update roughly all spins per frame

# Colors (RGB tuples) - Darker theme
COLOR_SPIN_UP = (40, 80, 180)    # Darker Blue
COLOR_SPIN_DOWN = (180, 40, 80)  # Darker Red/Purple
COLOR_BACKGROUND = (10, 10, 20)     # Very Dark Blue/Black
COLOR_SLIDER_BG = (40, 40, 55)
COLOR_SLIDER_HANDLE = (180, 180, 200)
COLOR_TEXT = (220, 220, 240)      # Light text color for contrast

# Pygame Setup
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 80 # Keep height for UI
SLIDER_HEIGHT = 20
SLIDER_WIDTH = SCREEN_WIDTH - 100
SLIDER_X = 50
SLIDER_Y = SCREEN_HEIGHT - 45 # Position of slider track
HANDLE_WIDTH = 10
HANDLE_HEIGHT = 30

# Font
pygame.font.init() # Initialize font module
try:
    FONT_SIZE = 18 # Make slightly smaller again to fit 3 values
    FONT = pygame.font.SysFont("Arial", FONT_SIZE)
except:
    FONT_SIZE = 22 # Fallback
    FONT = pygame.font.Font(None, FONT_SIZE)

# --- Simulation Logic ---

def initialize_spins(width, height):
    """Creates the initial spin grid with random +/-1 values."""
    spins = np.random.choice([-1, 1], size=(height, width))
    print("Spin grid initialized randomly.")
    return spins

def calculate_delta_energy(spins, r, c, height, width):
    """Calculates the change in energy if the spin at (r, c) is flipped."""
    current_spin = spins[r, c]
    neighbor_sum = 0
    neighbor_sum += spins[(r - 1) % height, c] # Up
    neighbor_sum += spins[(r + 1) % height, c] # Down
    neighbor_sum += spins[r, (c - 1) % width] # Left
    neighbor_sum += spins[r, (c + 1) % width] # Right
    delta_e = 2.0 * J * current_spin * neighbor_sum
    return delta_e

def update_ising(spins, temp, height, width):
    """Performs Monte Carlo steps using the Metropolis algorithm."""
    if temp <= 0: temp = 0.00001
    for _ in range(MONTE_CARLO_STEPS_PER_FRAME):
        r, c = random.randrange(height), random.randrange(width)
        delta_e = calculate_delta_energy(spins, r, c, height, width)
        accept = False
        if delta_e < 0:
            accept = True
        else:
            probability = math.exp(-delta_e / (KB * temp))
            if random.random() < probability:
                accept = True
        if accept:
            spins[r, c] *= -1

def calculate_correlation_analogue(spins):
    """Calculates the average fraction of aligned neighbors as a proxy for correlation."""
    height, width = spins.shape
    total_aligned_fraction_sum = 0.0
    num_neighbors = 4 # Von Neumann neighborhood size

    for r in range(height):
        for c in range(width):
            current_spin = spins[r, c]
            aligned_neighbors = 0
            if spins[(r - 1) % height, c] == current_spin: aligned_neighbors += 1 # Up
            if spins[(r + 1) % height, c] == current_spin: aligned_neighbors += 1 # Down
            if spins[r, (c - 1) % width] == current_spin: aligned_neighbors += 1 # Left
            if spins[r, (c + 1) % width] == current_spin: aligned_neighbors += 1 # Right
            total_aligned_fraction_sum += (aligned_neighbors / num_neighbors)

    avg_fraction = total_aligned_fraction_sum / (height * width)
    correlation_proxy = max(0.0, min(1.0, 2.0 * (avg_fraction - 0.5)))
    return correlation_proxy

def calculate_net_magnetism(spins):
    """Calculates the average magnetization of the grid."""
    # M = sum(spins) / N
    net_m = np.mean(spins) # More direct than sum/size
    return net_m

# --- Drawing Logic ---

def draw_grid(surface, spins, cell_size):
    """Draws the spin grid."""
    height, width = spins.shape
    for r in range(height):
        for c in range(width):
            color = COLOR_SPIN_UP if spins[r, c] == 1 else COLOR_SPIN_DOWN
            rect_x = c * cell_size
            rect_y = r * cell_size
            pygame.draw.rect(surface, color, (rect_x, rect_y, cell_size, cell_size))

def draw_ui(surface, current_temp, correlation_proxy, net_magnetism):
    """Draws the UI elements: slider and text displays."""
    # Draw slider background track
    pygame.draw.rect(surface, COLOR_SLIDER_BG, (SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT), border_radius=5)

    # Calculate handle position
    temp_ratio = max(0.0, min(1.0,(current_temp - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)))
    handle_x = SLIDER_X + int(temp_ratio * SLIDER_WIDTH) - HANDLE_WIDTH // 2
    handle_x = max(SLIDER_X - HANDLE_WIDTH // 2, min(handle_x, SLIDER_X + SLIDER_WIDTH - HANDLE_WIDTH // 2))

    # Draw handle
    handle_rect = pygame.Rect(handle_x, SLIDER_Y - (HANDLE_HEIGHT - SLIDER_HEIGHT)//2, HANDLE_WIDTH, HANDLE_HEIGHT)
    pygame.draw.rect(surface, COLOR_SLIDER_HANDLE, handle_rect, border_radius=3)

    # --- Draw Text Displays ---
    # Calculate positions for three text items above the slider
    text_y_pos = SLIDER_Y - 20 # Y position for text line
    text_width_third = SCREEN_WIDTH / 3

    # Temperature Text (Left)
    temp_text_surface = FONT.render(f"Temp: {current_temp:.2f}", True, COLOR_TEXT)
    temp_text_rect = temp_text_surface.get_rect(center=(text_width_third / 2, text_y_pos))
    surface.blit(temp_text_surface, temp_text_rect)

    # Magnetism Text (Center)
    mag_text_surface = FONT.render(f"Mag: {net_magnetism:.3f}", True, COLOR_TEXT)
    mag_text_rect = mag_text_surface.get_rect(center=(SCREEN_WIDTH / 2, text_y_pos))
    surface.blit(mag_text_surface, mag_text_rect)

    # Correlation Proxy Text (Right)
    corr_text_surface = FONT.render(f"Align: {correlation_proxy:.3f}", True, COLOR_TEXT)
    corr_text_rect = corr_text_surface.get_rect(center=(SCREEN_WIDTH - text_width_third / 2, text_y_pos))
    surface.blit(corr_text_surface, corr_text_rect)


# --- Main Function ---

def main(grid_width, grid_height, cellsize):
    """Initializes Pygame and runs the main simulation loop."""
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ising Model Simulation")

    spins = initialize_spins(grid_width, grid_height)
    current_temp = INITIAL_TEMP
    correlation_proxy = 0.0 # Initialize
    net_magnetism = 0.0     # Initialize

    dragging_slider = False
    running = True
    clock = pygame.time.Clock()

    frame_count = 0
    # Update potentially slower calculations less often
    metrics_update_frequency = 5 # Frames

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                slider_rect = pygame.Rect(SLIDER_X, SLIDER_Y - (HANDLE_HEIGHT - SLIDER_HEIGHT)//2, SLIDER_WIDTH, HANDLE_HEIGHT)
                if slider_rect.collidepoint(mouse_x, mouse_y):
                    dragging_slider = True
                    raw_pos = mouse_x - SLIDER_X
                    temp_ratio = max(0.0, min(1.0, raw_pos / SLIDER_WIDTH))
                    current_temp = MIN_TEMP + temp_ratio * (MAX_TEMP - MIN_TEMP)
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                mouse_x, _ = event.pos
                raw_pos = mouse_x - SLIDER_X
                temp_ratio = max(0.0, min(1.0, raw_pos / SLIDER_WIDTH))
                current_temp = MIN_TEMP + temp_ratio * (MAX_TEMP - MIN_TEMP)


        # --- Simulation Step ---
        update_ising(spins, current_temp, grid_height, grid_width)

        # --- Calculate Metrics (less frequently for correlation) ---
        frame_count += 1
        net_magnetism = calculate_net_magnetism(spins) # Calculate magnetism every frame (cheap)
        if frame_count % metrics_update_frequency == 0:
             correlation_proxy = calculate_correlation_analogue(spins) # Calculate proxy less often


        # --- Drawing ---
        surface.fill(COLOR_BACKGROUND) # Fill background
        draw_grid(surface, spins, cellsize) # Draw spins
        draw_ui(surface, current_temp, correlation_proxy, net_magnetism) # Draw slider and all text

        # --- Display Update ---
        pygame.display.flip()
        # clock.tick(30) # Optional: Limit FPS

    pygame.quit()
    print("Simulation finished.")

# --- Script Execution ---

if __name__ == "__main__":
    main(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)