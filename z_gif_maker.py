from PIL import Image
import os
import math # Used for ceiling calculation if needed, int() is often sufficient

def create_gif_from_frames(frame_dir, gif_filename, fps=15, loop_backwards=True):
  """
  Creates a GIF animation from a sequence of frames in a directory,
  allowing control over the frame rate.

  Args:
    frame_dir: The directory containing the frames (e.g., "simulation_frames").
    gif_filename: The desired filename for the output GIF (e.g., "output.gif").
    fps: Frames per second for the output GIF (default: 15).
    loop_backwards: If True, the GIF will play forward and then backward in a loop.
                    If False, it will play forward only.
  """

  # --- Input Validation ---
  if not os.path.isdir(frame_dir):
      print(f"Error: Frame directory not found: {frame_dir}")
      return
  if fps <= 0:
      print("Error: FPS must be a positive number.")
      return
  # --- End Input Validation ---

  # --- Find and Sort Frames ---
  print(f"Searching for frames in '{frame_dir}'...")
  try:
      # Get a list of image files, convert to lowercase for case-insensitive check, and sort
      image_files = sorted([
          f for f in os.listdir(frame_dir)
          if f.lower().endswith(('.jpg', '.jpeg', '.png')) # Check common image types
      ])
      if not image_files:
          print("Error: No suitable image files (.jpg, .jpeg, .png) found.")
          return
      print(f"Found {len(image_files)} frames.")
  except OSError as e:
      print(f"Error accessing directory '{frame_dir}': {e}")
      return
  # --- End Find and Sort Frames ---

  # --- Load Images ---
  print("Loading images...")
  images = []
  for filename in image_files:
      filepath = os.path.join(frame_dir, filename)
      try:
          # Open and explicitly load the image data to ensure file handles are closed
          img = Image.open(filepath)
          img.load()
          images.append(img)
      except Exception as e: # Catch potential errors during open or load
          print(f"Warning: Error loading image '{filepath}': {e}. Skipping.")
          # You might want to decide here if skipping is acceptable or if the process should stop

  if not images:
      print("Error: Failed to load any valid images.")
      return
  # --- End Load Images ---

  # --- Prepare Frame Sequence (Handle Boomerang) ---
  images_to_save = list(images) # Create a mutable copy to potentially modify
  if loop_backwards and len(images_to_save) > 1:
      print("Applying boomerang effect (forward then reverse)...")
      # Add the reversed list, excluding the absolute first and last frames of the reversed part
      # to create a smoother loop (e.g., [0, 1, 2, 3] -> [0, 1, 2, 3, 2, 1])
      images_to_save.extend(images_to_save[-2:0:-1])
  elif loop_backwards:
       print("Note: Boomerang requires more than one frame. Creating standard loop.")
  # --- End Prepare Frame Sequence ---

  # --- Calculate Duration ---
  # Duration is the time *each* frame is displayed, in milliseconds.
  # duration = 1000ms / frames_per_second
  duration_ms = int(1000 / fps)
  # Ensure duration is at least 1ms if fps is very high
  if duration_ms < 1:
      duration_ms = 1 # Minimum duration often needed
      print(f"Warning: Specified FPS ({fps}) results in <1ms duration. Setting duration to 1ms.")
  print(f"Calculated frame duration: {duration_ms} ms for {fps} FPS.")
  # --- End Calculate Duration ---

  # --- Save as GIF ---
  print(f"Saving GIF animation to '{gif_filename}'...")
  try:
      # Use the first image object to call save
      images_to_save[0].save(
          gif_filename,
          save_all=True,
          append_images=images_to_save[1:], # Append the rest of the images
          duration=duration_ms,
          loop=0  # 0 means loop indefinitely
      )
      print(f"GIF animation '{gif_filename}' created successfully.")
  except Exception as e:
      print(f"Error saving GIF: {e}")
  # --- End Save as GIF ---

# --- Example Usage ---
# Directory where your simulation frames (JPGs) are stored
frame_directory = "simulation_frames_circle"

# Desired filename for the output GIF
output_gif_filename = "simulation_movie.gif"

# Set the desired frame rate (frames per second)
frames_per_second = 60 # Example: smoother animation

# Choose whether to loop forward and backward (True) or just forward (False)
boomerang_effect = True

# Call the function
create_gif_from_frames(
    frame_directory,
    output_gif_filename,
    fps=frames_per_second,
    loop_backwards=boomerang_effect
)

# --- Another Example (Forward loop only, slower) ---
# create_gif_from_frames(
#     frame_directory,
#     "simulation_forward_loop.gif",
#     fps=10,
#     loop_backwards=False
# )