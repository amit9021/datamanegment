
import matplotlib.pyplot as plt
from librosa import display, onset, load,  amplitude_to_db, feature
import numpy as np
import os
import subprocess
import run_cfg
import cv2


def find_whistle(video: str, min_hertz_to_filter: int, min_amp_to_filter: int) -> np.array:
    """
    Finds the whistle sound events in a video by filtering the audio and detecting onsets.

    args:
        video (str): The video file path.
        min_hertz_to_filter(int): The minimum frequency in hertz to filter 
        min_amp_to_filter (int): The minimum amplitude threshold to filter out noise and keep only the whistle sound events.

    Returns:
        onset_times(np.array): An array of onset times of the whistle sound events detected in the video.

    """

    path = os.path.join(run_cfg.WORKING_PATH, video)

    y, sr = load(path, mono=True, duration=60)

    S_full = feature.melspectrogram(y=y, sr=sr,)

    S_filterd = feature.melspectrogram(y=y, sr=sr,
                                       fmin=min_hertz_to_filter)

    y_filter = feature.inverse.mel_to_audio(S_filterd, sr=sr)

    y_filter = y_filter * 1000
    # check amp between -0.5 and 0.5 and make it 0
    y_filter = np.where((y_filter > min_amp_to_filter) | (
        y_filter < -min_amp_to_filter), y_filter, 0)

    # Detect the sound events
    onset_times = onset.onset_detect(
        y_filter, sr=sr, units="time", backtrack=True)

    fig = plt.figure(figsize=(16, 20))
    fig.suptitle(y, fontsize=16)
    plt.subplot(4, 1, 1)
    display.waveshow(y, sr=sr)
    plt.title("Original Signal")

    plt.subplot(4, 1, 2)
    display.waveshow(y_filter, sr=sr)
    plt.title("Filtered Signal")

    plt.subplot(4, 1, 3)
    display.specshow(amplitude_to_db(S_full, ref=np.max),
                     y_axis='log', x_axis='time', sr=sr)
    plt.title("Original frequncy spectrum")

    plt.subplot(4, 1, 4)
    display.specshow(amplitude_to_db(S_filterd, ref=np.max),
                     y_axis='log', x_axis='time', sr=sr)
    plt.title("Filtered frequncy spectrum")
    # plt.show()
    sound_path = os.path.join(run_cfg.WORKING_PATH, "sounds")
    if not os.path.exists(sound_path):
        os.makedirs(sound_path)

    plt.savefig(os.path.join(sound_path, video.split('.')[0] + '.png'))

    return onset_times


def cut_video(video, working_path, where_to_cut):

    start_time = where_to_cut

    input_video = os.path.join(working_path, video)

    output_video = os.path.join(working_path, f"cut_{video.split('/')[-1]}")
    if video.split('.')[-1] == "webm":
        videoCapture = cv2.VideoCapture(input_video)
        FPS = videoCapture.get(cv2.CAP_PROP_FPS)
        # TODO: chack webm quality
        command = f"ffmpeg -ss {start_time} -i '{input_video}' -r {int(FPS)} '{output_video}'"
    else:
        command = f"ffmpeg -ss {start_time} -i '{input_video}' -c:v copy -c:a copy '{output_video}'"

    subprocess.run(command, shell=True, check=True)
