# Combined Medical Imaging Enhancement Script
# Supports: General Medical, X-ray, and CT
# Choose modality using: --modality general/xray/ct

import os
import cv2
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from skimage.metrics import structural_similarity as ssim, peak_signal_noise_ratio as psnr

def enhance_image(img):
    # Basic enhancement: denoise + sharpening
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    enhanced = cv2.filter2D(denoised, -1, sharpen_kernel)
    return enhanced

def process_directory(input_dir, output_dir, modality):
    os.makedirs(output_dir, exist_ok=True)
    filenames = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png','.jpg','.jpeg','.tif','.bmp'))]
    if not filenames:
        print("No images found in input directory.")
        return

    metrics = []
    for fn in tqdm(filenames, desc=f"Processing {modality.upper()} Images"):
        path = os.path.join(input_dir, fn)
        img = cv2.imread(path)
        if img is None:
            continue

        enhanced = enhance_image(img)

        save_path = os.path.join(output_dir, f"enhanced_{modality}_{fn}")
        cv2.imwrite(save_path, enhanced)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        enhanced_gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        m_psnr = psnr(img_gray, enhanced_gray, data_range=255)
        m_ssim = ssim(img_gray, enhanced_gray, data_range=255)
        metrics.append([fn, modality, m_psnr, m_ssim])

    df = pd.DataFrame(metrics, columns=["filename","modality","PSNR","SSIM"])
    df.to_csv(os.path.join(output_dir, "metrics.csv"), index=False)
    print("Processing complete. Metrics saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="./input_images")
    parser.add_argument("--output_dir", default="./results_mixed")
    parser.add_argument("--modality", default="general", choices=["general","xray","ct"])
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir, args.modality)
