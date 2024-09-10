import os
from PIL import Image
import concurrent.futures

def resize_image(file_path, output_path):
    with Image.open(file_path) as img:
        # Get the original dimensions
        width, height = img.size

        # Calculate the new dimensions
        if width > height:
            new_width = 510
            new_height = int(510 * height / width)
        else:
            new_height = 510
            new_width = int(510 * width / height)

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        resized_img.save(output_path, "PNG")

def resize_image_510(file_path, output_path):
    with Image.open(file_path) as img:
        # Convert to RGB if the image is in a different mode
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Get the original dimensions
        width, height = img.size

        # Determine the crop box
        if width > height:
            left = (width - height) / 2
            top = 0
            right = (width + height) / 2
            bottom = height
        else:
            left = 0
            top = (height - width) / 2
            right = width
            bottom = (height + width) / 2

        # Crop the image to a square
        img = img.crop((left, top, right, bottom))

        # Resize to 510x510
        resized_img = img.resize((510, 510), Image.LANCZOS)

        resized_img.save(output_path, "PNG")

def process_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for image_file in image_files:
            input_path = os.path.join(input_dir, image_file)
            output_path = os.path.join(output_dir, image_file)
            futures.append(executor.submit(resize_image_510, input_path, output_path))

        concurrent.futures.wait(futures)

# Define the directories
input_dirs = [
    "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/input/InputAsShotZero",
    "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/output/Export_C_512"
]

output_dirs = [
    "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/input/InputAsShotZero_resized510x510",
    "/mnt/slurm_home/zrgong/4DLUT/fivek_dataset/MIT-Adobe5k-UPE/output/Export_C_512_resized510x510"
]

# Process both directories
for input_dir, output_dir in zip(input_dirs, output_dirs):
    print(f"Processing directory: {input_dir}")
    process_directory(input_dir, output_dir)
    print(f"Finished processing: {input_dir}")

print("All images have been resized.")
