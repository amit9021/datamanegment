import numpy as np
import cv2
import os


def compare_images(image1, image2):
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)
    return np.allclose(img1, img2, rtol=1e-05, atol=1e-08)


root_dir = '/home/amit9021/AgadoDB/raw_data/2022-12-09_nissim_neve-avivim/angle1/Frames/'
comparison_dir = '/home/amit9021/AgadoDB/raw_data/2022-12-09_nissim_neve-avivim/angle1/Frames1/'

for filename in os.listdir(root_dir):
    image1 = os.path.join(root_dir, filename)
    image2 = os.path.join(comparison_dir, filename)
    result = compare_images(image1, image2)
    print(f"Image {filename}: {result}")
