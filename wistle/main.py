from argparse import ArgumentParser
import os
import pandas as pd
from tqdm import tqdm
import sound_cutting as sc
import run_cfg


def main(working_path: os.path):
    """
    this module find the wistle in the video and cut the video to the start of the exersice

    Args:
    -----
        working_path (os.path): (the default is run_cfg.WORKING_PATH, path containing all the videos)
    """

    data = dict()
    angles = dict(
        angle1={"min_hertz_to_filter": 1600, "min_amp_to_filter": 600},
        angle2={"min_hertz_to_filter": 1600, "min_amp_to_filter": 300},
        angle3={"min_hertz_to_filter": 1600, "min_amp_to_filter": 150},
        angle4={"min_hertz_to_filter": 2000, "min_amp_to_filter": 200},
        angle5={"min_hertz_to_filter": 2000, "min_amp_to_filter": 200},
    )

    if not os.path.exists(os.path.join(working_path, 'wistle_data.csv')):
        for video in tqdm(os.listdir(working_path)):
            if not video.endswith('.csv') and video.endswith('.webm') or video.endswith('.mp4') or video.endswith('.MOV') or video.endswith('.mov'):
                angle = video.split('_')[1]
                # if angle == "angle2":

                try:
                    data[video] = sc.find_whistle(
                        video, angles[angle]['min_hertz_to_filter'], angles[angle]['min_amp_to_filter'])
                except:
                    print(f'error in {video}')

        df_data = pd.DataFrame.from_dict(data, orient='index')
        df_data.to_csv(os.path.join(working_path, 'wistle_data.csv'))

        variable = input('check wistle_data.csv and press y to continue: ')

        "this is puse the run until we check the csv file for errors"
        if variable == 'y':
            df_data = pd.read_csv(os.path.join(
                working_path, 'wistle_data.csv'), index_col=0)
            for video, row in df_data.iterrows():
                sc.cut_video(video, working_path, row[0])
    else:
        df_data = pd.read_csv(os.path.join(
            working_path, 'wistle_data.csv'), index_col=0)
        for video, row in df_data.iterrows():
            sc.cut_video(video, working_path, row[0])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--video_path", default=run_cfg.WORKING_PATH, help="path to videofile")
    args = parser.parse_args()

    main(args.video_path)
