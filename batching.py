import os
import subprocess
import glob
from pathlib import Path

def batch_process_images():
    """Process all images in potential folder with all methods."""
    potential_folder = "potential"
    
    # Check if potential folder exists
    if not os.path.exists(potential_folder):
        print(f"Folder '{potential_folder}' not found!")
        return
    
    # Get all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(potential_folder, ext)))
        image_files.extend(glob.glob(os.path.join(potential_folder, ext.upper())))
    
    if not image_files:
        print(f"No image files found in '{potential_folder}' folder!")
        return
    
    # Methods to try
    methods = [
        {"name": "threshold", "args": ["--method", "threshold", "--threshold", "128"]},
        {"name": "adaptive", "args": ["--method", "adaptive", "--block-size", "15", "--C", "3"]},
        {"name": "adaptive_large", "args": ["--method", "adaptive", "--block-size", "21", "--C", "5"]}
    ]
    
    # Grid sizes to try
    grid_sizes = [50]
    
    print(f"Found {len(image_files)} images to process")
    
    for idx, image_path in enumerate(image_files):
        print(f"\nProcessing image {idx + 1}/{len(image_files)}: {os.path.basename(image_path)}")
        
        # Create output folder for this image
        output_folder = f"output_{idx + 1}"
        os.makedirs(output_folder, exist_ok=True)
        
        for grid_size in grid_sizes:
            for method in methods:
                method_name = method["name"]
                method_args = method["args"]
                
                # Create output filename
                output_file = os.path.join(output_folder, f"{method_name}_grid{grid_size}.png")
                
                # Build command
                cmd = [
                    "python", "nonogram_preprocess.py",
                    image_path,
                    output_file,
                    "--grid-size", str(grid_size)
                ] + method_args
                
                try:
                    print(f"  Creating {method_name} (grid {grid_size})...")
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    print(f"    Error processing {method_name}: {e}")
                except Exception as e:
                    print(f"    Unexpected error: {e}")
        
        print(f"  Completed image {idx + 1} -> folder '{output_folder}'")
    
    print(f"\nBatch processing complete! Check output folders 'output_1', 'output_2', etc.")

if __name__ == "__main__":
    batch_process_images()