import pandas as pd
import os
from videohandling.utils.utils import get_video_FPS
import math

"""
reverse to precutteded annotations
----------------------------------

This function reads through CSV files in a given directory containing annotations for cutted video clips.
It matches the CSV file with corresponding video and whistle annotations in the original_wistle DataFrame.
For each matched video and whistle annotation, it updates the corresponding annotations in the CSV file to match the frame number in the video.
The updated annotations are then written to a new CSV file in a 'fix' subdirectory within the original directory.

Parameters:
    cutted_video_annotations (str): The path to the directory containing CSV files of annotations for cutted video clips.
    original_wistle (pandas DataFrame) :A DataFrame containing the video and whistle annotations for the original videos.
    video_anotated (str): The path to the directory containing the annotated original video files.

Returns:
    None

"""


cutted_video_annotations = '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/working_folder/annotation'
video_anotated = '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/angle1'
original_wistle = pd.read_csv(
    '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/angle1/wistle_data.csv')
original_wistle = original_wistle.drop(columns=['1', '2', '3', '4'], axis=1)
original_wistle.columns = ['video', 'wistle']


for file in os.listdir(cutted_video_annotations):
    if file.endswith('csv'):
        annotation = pd.read_csv(os.path.join(
            cutted_video_annotations, file), header=None)
        for i, row in original_wistle.iterrows():
            if row["video"].split("_")[0] == file.split('_')[0]:
                for video in os.listdir(video_anotated):
                    if video.split('_')[0] == file.split('_')[0] and video.endswith('.mp4'):
                        FPS = get_video_FPS(
                            os.path.join(video_anotated, video))
                        original_wistle.loc[i, 'wistle'] = int(math.floor(
                            row['wistle'] * FPS))
                        for index, ann_row in annotation.iterrows():
                            ann_row[0] = f"frame{int(ann_row[0].split('frame')[1].split('.')[0]) + original_wistle.loc[i, 'wistle'].astype(int) - 15}.jpg"

                            print(ann_row[0], video, file)
                        annotation.to_csv(os.path.join(
                            cutted_video_annotations, 'fix', file), index=False, header=False)


# original_wistle['wistle'] = original_wistle['wistle'].astype(int)
# print(original_wistle)
