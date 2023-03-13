import os
import pandas as pd
import cv2
import datetime
import subprocess
import json


path = '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/wistle/results'
dest = '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/wistle/results/tmp'
video_basenames = [file for file in os.listdir(path) if file.endswith(
    'mp4') or file.endswith('MOV') or file.endswith('mov')]

video_paths = [os.path.join(path, file) for file in os.listdir(
    path) if file.endswith('mp4') or file.endswith('MOV') or file.endswith('mov')]

for video in video_basenames:
    video_ext = video.split(".")[-1]

    video_folder_basename = video.split(".")[0]

    action, curr_person, curr_err, curr_angle = video_folder_basename.split(
        "_")
    curr_person = 'person' + str(int(curr_person.strip('person')))
    curr_angle = 'angle' + str(int(curr_angle.strip('angle')))
    new_video_name = action + '_' + curr_person + '_' + curr_err + '_' + curr_angle

    for file in os.listdir(os.path.join(path, video_folder_basename)):
        if file.startswith('annotation-reps'):
            rep_ann_path = os.path.join(path, video_folder_basename, file)
        if file.startswith('annotation_'):
            state_ann_path = os.path.join(path, video_folder_basename, file)

    state_ann = pd.read_csv(state_ann_path)
    rep_ann = pd.read_csv(rep_ann_path)

    rep_1 = rep_ann.loc[rep_ann['rep_num'] ==
                        1, ['start', 'end']].values.squeeze()
    rep_2 = rep_ann.loc[rep_ann['rep_num'] ==
                        2, ['start', 'end']].values.squeeze()

    # vidcap = cv2.VideoCapture(os.path.join(path, video))
    # fps = vidcap.get(cv2.CAP_PROP_FPS)
    out = subprocess.run(['ffprobe', '-of', 'json', '-show_entries', 'format:stream', os.path.join(path, video)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    results = json.loads(out.stdout)
    metadata_format = results['format']['tags']
    metadata_streams = [res['tags'] for res in results['streams']]
    fps_str = results['streams'][0]['r_frame_rate']
    fps = float(int(fps_str.split("/")[0]) / int(fps_str.split("/")[1]))
    # if rep_1[0] > 5:
    #     rep_1[0] -= 5
    # # if rep_2[1] < number -5:
    # #     rep_2[1] += 5
    # rep_2[1] += 5
    #
    # rep_1[1] += 5
    # rep_2[0] -= 5

    # if video_folder_basename != 'squats_person30_correct_angle3':
    #     continue
    # print('\n')
    # print(video_folder_basename)
    # print(rep_1)
    # print(rep_2)
    rep_1_start = datetime.datetime.strftime(
        datetime.datetime.utcfromtimestamp(rep_1[0] / fps), "%H:%M:%S.%f")
    rep_1_duration = datetime.datetime.strftime(
        datetime.datetime.utcfromtimestamp((rep_1[1] - rep_1[0]) / fps), "%H:%M:%S.%f")
    rep_2_start = datetime.datetime.strftime(
        datetime.datetime.utcfromtimestamp(rep_2[0] / fps), "%H:%M:%S.%f")
    rep_2_duration = datetime.datetime.strftime(
        datetime.datetime.utcfromtimestamp((rep_2[1] - rep_2[0]) / fps), "%H:%M:%S.%f")

    reps = [
        [rep_1_start, rep_1_duration],
        [rep_2_start, rep_2_duration],
    ]

    if 'correct' in video:
        subdir = 'correct'
    elif 'back' in video:
        subdir = 'back'
    elif 'knees' in video:
        subdir = 'knees'

    for i in [1, 2]:
        ffmpeg_cmd = f'ffmpeg -y -ss {reps[i-1][0]} -i "{os.path.join(path, video)}" -codec copy -t {reps[i-1][1]} {os.path.join(dest, subdir, new_video_name)}_rep{str(i)}.{video_ext}'
        print(ffmpeg_cmd)
        subprocess.call(ffmpeg_cmd, shell=True)
    xxx = 3
