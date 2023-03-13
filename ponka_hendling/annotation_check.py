import os
import pandas as pd
import numpy as np
from loguru import logger
import cv2
import glob
from pathlib import Path
import subprocess
from argparse import ArgumentParser


ADD_EXTRA_FRAMES = 5
EXT = ('.mp4', '.mov', '.avi', '.webm')
MORE_THAN_ONE_VIDEO = False
MORE_THAN_ONE_ANGEL = False
VALIDATION_CSV = True

# relevant for all cases
FOLDER_PATH = '/home/amit9021/AgadoDB/raw_data/2023-01-20_nissim_neve-avivim/angle1'

# relevant jast for single video
CSV_PATH = '/home/amit9021/AgadoDB/raw_data/2023-01-20_nissim_neve-avivim/angle1/20230120_101654.csv'
# relevant jast for single video
VID_PATH = '/home/amit9021/AgadoDB/raw_data/2023-01-20_nissim_neve-avivim/angle1/20230120_101654.webm'


class PonkaValidation():
    def __init__(self, df, FPS, polina_file):
        self.df = df
        self.FPS = FPS
        self.polina_file = polina_file

    def __call__(self):
        self._rep_start_end_cycle()
        self._check_up_down_cycle()

    def _rep_start_end_cycle(self):
        """
        tohar validtion that check if all rep start have rep ends

        Args:
            df (pd.DataFrame): ponka file converted to polina
            FPS (int): _description_

        Returns:
            bool: _description_ the csv is valid or not
        """

        "create reps data from rep_start to rep_end"
        reps = []
        reps_to_time = []
        prev_exercise = 'start'
        for i, row in self.df.iterrows():
            row_name = self.df["action"][i]
            row_name = row_name.strip('[]').split(',')[0].lower()
            if row_name == 'undefined':
                continue
            else:
                attributes = row_name
                if attributes.startswith('rep_start'):
                    reps.append([row['frame']])
                    prev_exercise = 'start'
                if attributes.startswith('rep_end') and prev_exercise != 'end':  # or attributes.split(",")[1].startswith('rep_end') \
                    reps[-1].append(row['frame'])
                    prev_exercise = 'end'
        for rep in reps:
            if len(rep) == 2:
                VALIDATION_CSV = True

                # continue
            else:
                VALIDATION_CSV = False
                raise Exception(f"no rep end for rep start at frame: {rep}")

        return VALIDATION_CSV, reps

    def _check_up_down_cycle(self):
        # TODO: check if the up and down are in the right order
        print('check up down cycle')


def split_string(param):
    return int(param.strip('frame').split(".")[0])


def calc_time(time):
    return f'00:{str(int(time / 60)).zfill(2)}:{str(int(time % 60)).zfill(2)}.{str((time % 60 - int(time % 60)) * 1000).split(".")[0]}'


def cut_videos(folder_path, ponka_file, vid_path, reps):
    videoCapture = cv2.VideoCapture(vid_path)
    FPS = videoCapture.get(cv2.CAP_PROP_FPS)
    df = ponka_file
    # validation, reps = create_data_reps(df)
    _, extension = os.path.splitext(vid_path)
    prev = ''
    for j, [rep_start, rep_end] in enumerate(reps):
        index = df[df['frame'] == rep_start].index.values[0]
        # if len(df["action"][index+1].split(",")) == 1:
        #     movement_name = 'None'
        #     prev = movement_name
        # else:
        if df["action"][index+1].split(",")[1].startswith('exercise'):
            movement_name = df["action"][index + 1].split(",")[1]
            movement_name = movement_name[:-1]
        else:
            movement_name = df["action"][index + 1].split(",")[0]
            movement_name = movement_name[1:]
        if movement_name == prev:
            continue
        else:
            path = os.path.join(folder_path, 'videos', movement_name)
            os.makedirs(path, exist_ok=True)
            count = len(os.listdir(path))
            rep_start = split_string(rep_start)
            rep_end = split_string(rep_end)
            start_time = calc_time(rep_start / FPS)
            end_time = calc_time(
                (rep_end - rep_start + ADD_EXTRA_FRAMES) / FPS)
            cut_cmd = f'ffmpeg -y -i {vid_path} -ss {start_time} -t {end_time} -c:a copy {path}/rep{count + 1}{extension}'
            subprocess.call(cut_cmd, shell=True)
            logger.info(f"Save the video in #{path}")
            print(f'{path}/rep{count + 1}{extension}')
        prev = movement_name


def main(folder_path, several_videos, several_angels):
    if several_videos:  # different videos with different annotation file
        videos_list = []
        annotation_list = []
        for root, dirs, files in os.walk(folder_path):
            for _file in files:
                if _file.split(".")[1] == 'csv':
                    annotation_list.append(_file)
                else:
                    videos_list.append(_file)
                continue
        for i in range(len(videos_list)-1):
            csv_path = os.path.join(folder_path, annotation_list[i].split(".")[
                0], annotation_list[i])
            video = annotation_list[i].split(
                ".")[0] + '.' + videos_list[i].split(".")[1]
            vid_path = os.path.join(folder_path, video)
            cut_videos(folder_path, csv_path, vid_path)
    elif several_angels:  # different angeles of the same video with one annotation file
        videos_list = []
        annotation_file = ''
        for root, dirs, files in os.walk(folder_path):
            for _file in files:
                if _file.split(".")[1] == 'csv':
                    annotation_file = _file
                else:
                    videos_list.append(_file)
                continue
        for i in range(len(videos_list) - 1):
            video = annotation_file.split(
                ".")[0] + '.' + videos_list[i].split(".")[1]
            csv_path = os.path.join(folder_path, annotation_file)
            vid_path = os.path.join(folder_path, video)
            cut_videos(folder_path, csv_path, vid_path)
    else:  # one video with one annotation file
        cut_videos(folder_path, args.csv_path, args.vid_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--folder_path", default=FOLDER_PATH,
                        help="save the file in the following folder")
    parser.add_argument("--csv_path", default=CSV_PATH,
                        help="path to the csv annotation file")
    parser.add_argument("--vid_path", default=VID_PATH,
                        help="path to the video")
    args = parser.parse_args()

    if MORE_THAN_ONE_VIDEO and not MORE_THAN_ONE_ANGEL:
        main(args.folder_path, several_videos=True, several_angels=False)
    elif MORE_THAN_ONE_ANGEL and not MORE_THAN_ONE_VIDEO:
        main(args.folder_path, several_videos=False, several_angels=True)
    elif not MORE_THAN_ONE_ANGEL and not MORE_THAN_ONE_VIDEO:
        main(args.folder_path, several_videos=False, several_angels=False)
