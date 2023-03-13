import pandas as pd
import os
from datamangment.Formater import csv_formater
from tqdm import tqdm
import ffmpeg
import pymediainfo
from datetime import datetime
import pytz

# Load the excel file into a dataframe
df = pd.read_excel("/home/amit9021/AgadoDB/to_rule_them_all.xlsx")

# Add a new column to the dataframe
df["json_exist"] = False

video_formats = (".mp4", ".mov", ".MOV", ".webm", ".avi")
path_to_format = "/home/amit9021/AgadoDB/data"

# Iterate through the file names in the 'video_name' column


def rename_to_agado(video_formats, path_to_format):
    num_of_videos = 0
    json_list = []
    csv_list = []
    for dirpath, dirnames, filenames in os.walk(path_to_format):
        for file in filenames:
            if file.endswith(video_formats):
                num_of_videos += 1
    with tqdm(total=num_of_videos, desc="Names Changing") as pbar:
        for dirpath, dirnames, filenames in os.walk(path_to_format):
            for file in filenames:
                if file.endswith(video_formats):
                    date = dirpath.split(
                        "/")[-1].split("_")[0].replace("-", "")
                    video_path = os.path.join(dirpath, file)
                    firs_side = video_path.split(
                        ".")[0].split("/")[-1].split("_")
                    ext = video_path.split(".")[-1]
                    # media_info = pymediainfo.MediaInfo.parse(video_path)
                    # date = media_info.tracks[0].encoded_date
                    # if date is None:
                    #     date = media_info.tracks[0].file_last_modification_date
                    # dt_object = datetime.strptime(
                    #     date, "UTC %Y-%m-%d %H:%M:%S")
                    # utc_tz = pytz.timezone("UTC")
                    # utc_dt = utc_tz.localize(dt_object)
                    # local_tz = pytz.timezone("Asia/Jerusalem")
                    # local_dt = utc_dt.astimezone(local_tz)
                    # date_str = local_dt.strftime("%Y%m%d%H%M%S")

                    new_name = f"{'_'.join(map(str, firs_side[0:4]))}_{date}.{ext}"
                    new_name_path = os.path.join(dirpath, new_name)
                    print(new_name)
                    os.rename(video_path, new_name_path)
                    for dir in dirnames:
                        if dir == file.split(".")[0]:
                            print("tmp")
                            os.rename(
                                os.path.join(dirpath, dir),
                                os.path.join(dirpath, new_name.split(".")[0]),
                            )

                if file.endswith(".json"):
                    json_list.append(os.path.join(dirpath, file))
                if file.endswith(".csv"):
                    csv_list.append(os.path.join(dirpath, file))
        # for json_file in json_list:
        #     json_formater(json_file)

        for csv_file in csv_list:
            csv_formater(csv_file, date)
            pbar.update(1)
