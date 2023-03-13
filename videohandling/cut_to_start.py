import math
import os
import subprocess

import cv2
import numpy as np
import pandas as pd
import run_cfg
from loguru import logger as logging
from videohandling.utils.utils import get_video_FPS, folder_creating, convert_to_timestamp


def create_csv(df: pd.DataFrame, exercise: str, error: str, FPS_video: int, **kwargs):
    """
    Given a Pandas DataFrame `polina_file` or `reps` ,
    filters it by the given `exercise` and `error` and converts the 'start' and 'end' columns
    to frame-based data using the given `FPS_video` parameter.

    Args:
        df (pd.DataFrame): The DataFrame containing the time-based exercise data annotation / reps.
        exercise (str): The name of the exercise to filter by.
        error (str): The type of error to filter by.
        FPS_video (int): The frames per second of the video.

        **kwargs (dict): The keyword arguments.
            -col_name (str): The name of the column move/rep_num.
            -annotation_name (str): The name of the annotation file annotation/annotation-reps.
            -vid_dir (str): The path to the video directory.
            -file_name (str): The name of the video file.

    Returns:
        filtered_df(pd.DataFrame): A DataFrame containing the filtered and frame-based data of the exercise movements.
    """
    df_new = df.copy()
    f_list = df_new[(df_new['exercise'] == exercise)
                    & (df_new['error'] == error)].index

    f_slice = slice(f_list[0], f_list[-1] +
                    (0 if kwargs["col_name"] == "rep_num" else 1))

    filtered_df = df_new.loc[f_slice, [
        'start', 'end', f"{kwargs['col_name']}", 'error']].copy()
    filtered_df = filtered_df[(filtered_df['error'] != "no_cut") & (
        filtered_df['error'] != "")]

    # convert start and end columns from time-based data to frame-based data
    filtered_df[['start', 'end']] = np.floor(
        filtered_df[['start', 'end']] * FPS_video).astype(int)

    filtered_df.reset_index(drop=True, inplace=True)

    if not filtered_df.empty:
        first_frame = int(filtered_df['start'].iloc[0] - 1)

        filtered_df[['start', 'end']] = filtered_df[[
            'start', 'end']].sub(first_frame)
        filtered_df['end'] = filtered_df['end'].sub(1)
        # if not run_cfg.CUTTED_VIDEO:
        #     filtered_df['start'] = (
        #         filtered_df['start'] + 0.3 * FPS_video).astype(int)
        #     filtered_df['end'] = (filtered_df['end'] -
        #                           0.5 * FPS_video).astype(int)

        filtered_df = filtered_df.drop(columns=["error"])

        annotation_name = f"{kwargs['annotation_name']}_{kwargs['file_name']}.csv"
        filtered_df.to_csv(os.path.join(
            kwargs['vid_dir'], annotation_name), index=False)


def create_cuting_matrix(reps: pd.DataFrame, FPS_video, sound_data) -> pd.DataFrame:
    """
    Creates a cutting matrix from the given reps DataFrame.

    Args:
        reps (pandas.DataFrame): A DataFrame containing columns "exercise", "error",
            "start", and "end" representing exercise name, error type, start time, and
            end time, respectively.

    Returns:
        pandas.DataFrame: A DataFrame containing columns "exercise", "error", "start",
            and "end" representing the cutting matrix for the given reps DataFrame.
    """

    data = []
    reps_new = reps.copy()
    grouped = reps_new.groupby(["exercise", "error"])
    data = [[exerersize, error, grp["start"].min(), grp["end"].max()]
            for (exerersize, error), grp in grouped]

    reps_new = pd.DataFrame(
        data, columns=["exercise", "error", "start", "end"])
    reps_new = reps_new.dropna()
    reps_new = reps_new[(reps_new['exercise'] != "") &
                        (reps_new['error'] != "no_cut")]
    reps_new_timestamp = convert_to_timestamp(reps_new, FPS_video, sound_data)
    if not run_cfg.EXERCISE == "all":
        reps_new = reps_new[(
            reps_new["exercise"] == run_cfg.EXERCISE)]

    return reps_new.reset_index(drop=True)


def cut_to_ponka_annotation(path_to_video: str, working_path: str, person: str, polina_file: pd.DataFrame, FPS: int, reps: pd.DataFrame, sound_data: pd.DataFrame):
    """Cut the video into exercises and errors, and annotate each cut with the corresponding information.

    Args:
        path_to_video: The path to the video file to cut.
        working_path: The working path to save the results.
        person: The name of the person who performs the exercises.
        polina_file: The path to the Polina file to use for the annotations.
        FPS: The base FPS (frames per second) of the video.
        reps: A DataFrame containing information about all the repetitions in the video.
    """
    logging.info(
        "build the cutting matix for cuting the video to exercise and errors")

    video_name = "_".join(path_to_video.split("/")[-1].split("_")[1:])
    angle = video_name.split('_')[1]
    extention = path_to_video.split('.')[-1]
    FPS_video = get_video_FPS(path_to_video)

    cuting_matrix = create_cuting_matrix(
        reps, FPS_video, sound_data[video_name][0])

    logging.debug(f"cuting matrix is: \n{cuting_matrix}")

    logging.debug(f"FPS of the video is: {FPS_video}, base FPS is: {FPS}")

    for i, row in cuting_matrix.iterrows():
        start_time = row["start"] - run_cfg.ADD_EXTRA_TIME
        end_time = row["end"] + run_cfg.ADD_EXTRA_TIME

        file_name, path_to_results, vid_dir = folder_creating(
            working_path, person, angle, row)

        "create the annotation file"
        create_csv(polina_file,
                   row['exercise'], row['error'],  FPS_video, col_name="move", annotation_name="annotation", vid_dir=vid_dir, file_name=file_name)

        create_csv(reps,
                   row['exercise'], row['error'],  FPS_video, col_name="rep_num", annotation_name="annotation-reps", vid_dir=vid_dir, file_name=file_name)

        output_video = os.path.join(
            path_to_results, f"{file_name}.{extention}")

        if run_cfg.TO_CUT:

            if extention == "webm":
                videoCapture = cv2.VideoCapture(path_to_video)
                FPS = videoCapture.get(cv2.CAP_PROP_FPS)
                "re encode if webm file with original webm FPS"
                command = f"ffmpeg -ss {start_time} -to {end_time} -i '{path_to_video}' -r {int(FPS)} '{output_video}'"
            else:
                command = f"ffmpeg -ss {start_time} -to {end_time} -i '{path_to_video}' -c:v copy -c:a copy '{output_video}'"
            try:
                subprocess.run(command, shell=True, check=True)
            except:
                print("error")
