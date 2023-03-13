import subprocess
import json
import pandas as pd
import run_cfg
import os


def get_video_FPS(input_video: str):
    """Get video FPS from video path Args: video_path (str): video path Returns: int: FPS """

    out = subprocess.run(['ffprobe', '-of', 'json', '-show_entries', 'format:stream', input_video],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    results = json.loads(out.stdout)
    metadata_format = results['format']['tags']
    metadata_streams = [res['tags']
                        for res in results['streams']]
    fps_str = results['streams'][0]['r_frame_rate']
    FPS_video = float(
        int(fps_str.split("/")[0]) / int(fps_str.split("/")[1]))

    return int(FPS_video)


def convert_to_match(ponka_file, polina_file, ratio):
    # if not run_cfg.PONKA_WITH_ERORR:

    polina_file["start"] = polina_file["start"] / ratio
    polina_file["end"] = polina_file["end"] / ratio
    ponka_file["start"] = ponka_file["start"] / ratio
    ponka_file["end"] = ponka_file["end"] / ratio

    return ponka_file, polina_file


def to_ponka_dict(df_data):
    data = {}
    for i, row in df_data.iterrows():
        filename = row[0]
        # exclude empty cells and convert to list
        frames = row[1:].dropna().tolist()
        # get the person name
        if filename in data:
            data[filename].append(frames)
        else:
            data[filename] = frames
    return data


def convert_to_timestamp(df: pd.DataFrame, FPS: int, sound_data: float):
    """convert `polina file` or `reps` to timestamp
    args:
        df (pandas df): polina file or reps
        FPS (int): base video FPS
    Returns:
        df: dataframe with timestamp
    """

    for i, row in df.iterrows():
        if not run_cfg.CUTTED_VIDEO:
            df.loc[i, "start"] = row["start"] / FPS - (sound_data)

            df.loc[i, "end"] = row["end"] / FPS - (sound_data)
        else:
            df.loc[i, "start"] = row["start"] / FPS
            df.loc[i, "end"] = row["end"] / FPS
    return df


def folder_creating(working_path, person, angle, row):
    exercise = run_cfg.SESSION_DICT["".join(
        row["exercise"].split())]["name"]

    error = run_cfg.SESSION_DICT["".join(
        row["exercise"].split())]["".join(
            row["error"].split())]

    file_name = f"{exercise}_{person}_{error}_{angle}"

    if not os.path.exists(os.path.join(working_path, "results")):
        os.mkdir(os.path.join(working_path, "results"))

    path_to_results = os.path.join(working_path, "results")

    if not os.path.exists(os.path.join(path_to_results, file_name)):
        os.mkdir(os.path.join(path_to_results, file_name))
    vid_dir = os.path.join(path_to_results, file_name)
    return file_name, path_to_results, vid_dir
