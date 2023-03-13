import os
import pandas as pd
import pymediainfo
import ffmpeg
from tqdm import tqdm
import json
import subprocess
import shutil
import cv2


def look_for_metaData(df, path):

    video_formats = ['.mp4', '.mov', '.MOV', '.webm', '.avi']
    df["duration"] = ""
    df["width"] = ""
    df["height"] = ""
    with tqdm(total=df.shape[0], desc="Gathering Meta Data") as pbar:
        for index, row in df.iterrows():
            video_name = row['File']

            for root, dirnames, files in os.walk(path):

                for file in files:

                    if not video_name == file:
                        continue
                    file_path = os.path.join(root, file)

                    media_info = pymediainfo.MediaInfo.parse(file_path)
                    try:
                        meta = ffmpeg.probe(file_path)
                    except ffmpeg.Error as e:
                        print('stdout:', e.stdout.decode('utf8'))
                        print('stderr:', e.stderr.decode('utf8'))

                    for track in media_info.tracks:
                        if track.track_type == 'Video':
                            if track.format == "VP8":
                                df.loc[index, 'duration'] = media_info.general_tracks[0].other_duration[3]

                            else:
                                df.loc[index, 'duration'] = track.other_duration[3]

                            df.loc[index, 'width'] = track.width
                            df.loc[index, 'height'] = track.height
            pbar.update(1)
    return df


def look_for_csv_json(df, path):
    file_extension = (".csv", ".json")
    video_formats = ['.mp4', '.mov', '.MOV', '.webm', '.avi']
    predefined_words = ('annotation', 'mp1', 'mp2')
    df["annotation"] = ""
    df["mp1_json"] = ""
    df["mp2_json"] = ""

    with tqdm(total=df.shape[0], desc="Gathering Csv And Json Data") as pbar:
        for index, row in df.iterrows():
            dir_path = os.path.join(
                path, row["Angular"], row["Collection"], row['File'].split(".")[0])
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.endswith(file_extension) and file.startswith(predefined_words):

                        df.loc[index, 'annotation'] = "yes"

                    if file.endswith(file_extension) and file.startswith('mp1'):

                        df.loc[index, 'mp1_json'] = "yes"

                    if file.endswith(file_extension) and file.startswith('mp2'):

                        df.loc[index, 'mp2_json'] = "yes"

        pbar.update(1)

    return df


def repetition_col(path, df):
    with tqdm(total=df.shape[0], desc="Gathering Repetitions") as pbar:
        for index, row in df.iterrows():

            reps = 0
            reps_indices = []
            up_flag = False
            down_flag = False
            filename = row['File']
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(f"annotation_{filename.split('.')[0]}.csv"):
                        file_path = os.path.join(root, file)
                        # Do something with the matching file
                        exercize = file.split("_")[1]
                        for annotation_index, annotation_row in pd.read_csv(file_path).iterrows():

                            if annotation_row["move"] == 'up' and up_flag == True and down_flag == True:
                                down_flag = False
                                reps += 1
                                reps_indices.append(
                                    int((annotation_row["end"] + annotation_row["start"]) / 2))
                            if exercize == "lunges":
                                if annotation_row["move"] == 'up' and up_flag == False:
                                    up_flag = True
                                elif annotation_row["move"] == "right" or annotation_row["move"] == "left":
                                    down_flag = True
                            else:
                                if annotation_row["move"] == 'up' and up_flag == False:
                                    up_flag = True
                                elif annotation_row["move"] == "down":
                                    down_flag = True

                        df.loc[index, 'repetition'] = reps
                        break
            pbar.update(1)
        else:
            print(f"No matching file found for: {filename}")

    return df


def json_meta_data_change(path, df):
    with tqdm(total=df.shape[0], desc="updating json files") as pbar:
        for index, row in df.iterrows():
            filename = row['File']
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(f"mp1_{filename.split('.')[0]}.json") or file.endswith(f"mp2_{filename.split('.')[0]}.json"):
                        file_path = os.path.join(root, file)
                        # Do something with the matching file
                        try:
                            with open(file_path) as json_file:
                                data = json.load(json_file)
                                data["video_name"] = filename
                                data["video_path"] = os.path.join(
                                    "/".join(root.split("/")[3:]), filename)
                            with open(file_path, 'w') as json_file:
                                json.dump(data, json_file)
                        except:  # noqa: E722
                            print(f"Error in {file_path}")
                        break
            pbar.update(1)
        else:
            print(f"No matching file found for: {filename}")


def check_full_body(path, df):
    with tqdm(total=df.shape[0], desc="check full body") as pbar:
        for index, row in df.iterrows():
            count_viz = 0
            filename = row['File']
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(f"mp1_{filename.split('.')[0]}.json") or file.endswith(f"mp2_{filename.split('.')[0]}.json"):
                        file_path = os.path.join(root, file)
                        # Do something with the matching file
                        try:
                            with open(file_path) as json_file:
                                out_of_frame = 0
                                data = json.load(json_file)
                                min_x = 0
                                min_y = 0
                                max_x = 0
                                max_y = 0
                                for pose in data["frames"]:
                                    for point in pose["2d_pose"]:
                                        min_x = min(min_x, point[0])
                                        min_y = min(min_y, point[1])
                                        max_x = max(max_x, point[0])
                                        max_y = max(max_y, point[1])
                                count_viz = count_viz / data["frame_num"]

                        except:  # noqa: E722
                            print(f"Error in {file_path}")
                        if min_x >= 0 and min_y >= 0 and max_x <= data["width"] * 1.2 and max_y <= data["height"] * 1.2:
                            df.loc[index, 'full_body'] = "yes"
                        else:
                            df.loc[index, 'full_body'] = "no"

                        break
            pbar.update(1)
        else:
            print(f"No matching file found for: {filename}")
    return df


def frame_count(path, df):

    with tqdm(total=df.shape[0], desc="updating frame count and fps ") as pbar:
        for index, row in df.iterrows():
            filename = row['File']
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(f"mp2_{filename.split('.')[0]}.json"):
                        file_path = os.path.join(root, file)
                        # Do something with the matching file
                        try:
                            with open(file_path) as json_file:
                                data = json.load(json_file)
                                frame_count = data["frame_num"]
                                fps = data["fps"]
                        except:  # noqa: E722
                            print(f"Error in {file_path}")

                        df.loc[index, 'frame_count'] = frame_count
                        df.loc[index, 'fps'] = fps
                        pbar.update(1)
                        break

        else:
            print(f"No matching file found for: {filename}")
        for index, row in df.iterrows():
            filename = row['File']
            if pd.isna(row['frame_count']):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(filename):
                            file_path = os.path.join(root, file)
                            # Do something with the matching file
                            try:
                                path_to_frames = os.path.join(root, "frames")
                                os.mkdir(path_to_frames)
                                subprocess.call(
                                    ['ffmpeg', '-i', file_path, '-q:v', '1', f"{path_to_frames}/frame_%05d.jpg"], stderr=subprocess.DEVNULL)

                                # Count the number of frames
                                frame_count = len(
                                    list(filter(lambda x: x.startswith("frame_"), os.listdir(path_to_frames))))
                                print("Number of frames:", frame_count)

                                # Delete the folder containing the frames
                                shutil.rmtree(path_to_frames)
                                cap = cv2.VideoCapture(file_path)
                                fps = int(cap.get(cv2.CAP_PROP_FPS))
                            except:
                                print(f"Error in {file_path}")
                        df.loc[index, 'frame_count'] = frame_count
                        df.loc[index, 'fps'] = fps
                        pbar.update(1)
                        break

    return df
