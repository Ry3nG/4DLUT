import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import random

BASE_URL = "https://data.csail.mit.edu/graphics/fivek/img"
OUTPUT_DIR = "/mnt/slurm_home/zrgong/4DLUT/data/fivek_dataset/MIT-Adobe5k-UPE"
CATEGORIES_FILE = "/mnt/slurm_home/zrgong/4DLUT/data/fivek_dataset/categories.txt"

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def process_image(image_name):
    dng_url = f"{BASE_URL}/dng/{image_name}.dng"
    tiff_url = f"{BASE_URL}/tiff16_c/{image_name}.tif"

    dng_path = os.path.join(OUTPUT_DIR, "input", "InputAsShotZero", f"{image_name}.dng")
    tiff_path = os.path.join(OUTPUT_DIR, "output", "Export_C_512", f"{image_name}.tif")

    os.makedirs(os.path.dirname(dng_path), exist_ok=True)
    os.makedirs(os.path.dirname(tiff_path), exist_ok=True)

    try:
        # Download files
        download_file(dng_url, dng_path)
        download_file(tiff_url, tiff_path)
        return image_name
    except Exception as e:
        print(f"Error downloading image {image_name}: {str(e)}")
        return None

def main():
    # Read categories file
    with open(CATEGORIES_FILE, 'r') as f:
        image_names = [line.split(',')[0] for line in f]

    # Download images
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_image, name) for name in image_names]

        successful_images = []
        with tqdm(total=len(image_names)) as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    successful_images.append(result)
                pbar.update(1)

    # Create train and test sets
    random.shuffle(successful_images)
    split_index = int(len(successful_images) * 0.9)  # 90% for training, 10% for testing
    train_images = successful_images[:split_index]
    test_images = successful_images[split_index:]

    # Write train and test files
    with open(os.path.join(OUTPUT_DIR, 'images_train.txt'), 'w') as f:
        f.write('\n'.join(train_images))

    with open(os.path.join(OUTPUT_DIR, 'images_test.txt'), 'w') as f:
        f.write('\n'.join(test_images))

if __name__ == "__main__":
    main()
    print("Download complete!")
