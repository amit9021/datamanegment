import os
import pandas as pd
import numpy as np
from annotation_check import create_data_reps
import cv2


def draw_reps(video_path, csv_path, reps):
    print("to be continued")
    



path_to_ponka_annotations = '/home/amit9021/AgadoDB/raw_data/2023-01-20_nissim_neve-avivim/angle1/'
bad_files = []
good_files = []
for file in os.listdir(path_to_ponka_annotations):
    if file.endswith('.csv'):
        csv_path = os.path.join(path_to_ponka_annotations, file)
        ponka_file = pd.read_csv(csv_path, names=["frame", "action"])
        validation, reps = create_data_reps(ponka_file)
        if validation:
            print(f"File {file} is OK")
            good_files.append([file] + [reps])
        else:
            print(f"File {file} is NOT OK")
            bad_files.append([file] + [reps])
            
print(bad_files)




            