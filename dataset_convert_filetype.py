import os
import rawpy
from PIL import Image
import concurrent.futures

def convert_dng_to_png(input_file, output_file):
    with rawpy.imread(input_file) as raw:
        rgb = raw.postprocess()
    img = Image.fromarray(rgb)
    img.save(output_file, 'PNG')

def convert_tif_to_png(input_file, output_file):
    with Image.open(input_file) as img:
        img.save(output_file, 'PNG')

def process_file(input_file, output_file):
    if input_file.lower().endswith('.dng'):
        convert_dng_to_png(input_file, output_file)
    elif input_file.lower().endswith('.tif'):
        convert_tif_to_png(input_file, output_file)
    else:
        print(f"Unsupported file format: {input_file}")

def convert_dataset(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tasks = []

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.dng', '.tif')):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, os.path.splitext(relative_path)[0] + '.png')

                output_subdir = os.path.dirname(output_path)
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)

                tasks.append((input_path, output_path))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for input_path, output_path in tasks:
            executor.submit(process_file, input_path, output_path)

if __name__ == "__main__":
    # Hardcoded input and output directories
    input_dir_dng = "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/input/InputAsShotZero"
    output_dir_dng = "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/input/InputAsShotZero"

    input_dir_tif = "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/output/Export_C_512"
    output_dir_tif = "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/output/Export_C_512"

    # Convert DNG files
    print("Converting DNG files...")
    convert_dataset(input_dir_dng, output_dir_dng)

    # Convert TIF files
    print("Converting TIF files...")
    convert_dataset(input_dir_tif, output_dir_tif)

    print("Conversion completed.")
