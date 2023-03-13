import os
import cv2
from argparse import ArgumentParser
import mediapipe as mp
import numpy as np
import json
import subprocess
from PIL import Image
import shutil


def generate_agado_json(frames_dir, vid_fmt):
    vcap = cv2.VideoCapture(args.video_path)
    vid_w, vid_h, vid_fps = vcap.get(3), vcap.get(4), vcap.get(5)
    vid_name = args.video_path.split('/')[-1]
    tmp = Image.open(os.path.join(frames_dir, '00001.jpg'))
    image_format = tmp.format
    image_mode = tmp.mode
    h = int(vcap.get(cv2.CAP_PROP_FOURCC))
    codec = chr(h & 0xff) + chr((h >> 8) & 0xff) + \
        chr((h >> 16) & 0xff) + chr((h >> 24) & 0xff)
    # generate agadovideo-v1.1 json file
    frames_data = {
        'version': 'agadovideo-v1.2',
        'video_name': vid_name,
        'video_source': args.video_source,
        'video_path': args.video_path,
        'video_format': vid_fmt,
        'video_codec': codec,
        'frames_format': image_format,
        'frames_mode': image_mode,
        'width': int(vid_w),
        'height': int(vid_h),
        'fps': int(vid_fps),
        'detection_source': '',
        'pose_source': 'MediaPipe',
        'pose_lift_source': 'MediaPipe',
        'pipe_fps': None,
        'frame_num': None,
        'frames': []
    }
    return frames_data


def main():
    print(f'Generating MediaPipe Prediction files for: {args.video_path}\n'
          f'Running with MODEL_COMPLEXITY = {args.mp_model_complexity}')

    [vid_dir, vid_fmt] = args.video_path.split(".")
    frames_dir = os.path.join(vid_dir, 'frames')

    os.makedirs(vid_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    pred_path = os.path.join(
        vid_dir, f'mp{args.mp_model_complexity}_{vid_dir.split("/")[-1]}.json')

    split_frames_cmd = f'ffmpeg -i {args.video_path} -qscale:v 2 {frames_dir}/%05d.jpg'
    subprocess.check_call(split_frames_cmd, shell=True,
                          stderr=subprocess.DEVNULL)

    frame_num = len(os.listdir(frames_dir))
    frames = sorted([str(i + 1).zfill(5) for i in range(frame_num)])

    frames_data = generate_agado_json(frames_dir, vid_fmt)
    frames_data['frame_num'] = frame_num

    w, h = frames_data['width'], frames_data['height']

    mp_pose = mp.solutions.pose
    pose_extractor = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=args.mp_model_complexity,
        enable_segmentation=False,
        min_detection_confidence=0.2,
        min_tracking_confidence=0.2
    )

    for frame in frames:
        frame_idx = int(frame.split(".")[0]) - 1
        frames_data['frames'].append({'frame_name': frame})

        img = cv2.imread(os.path.join(frames_dir, frame + '.jpg'))

        results = pose_extractor.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pose_2d = []
        pose_3d = []

        if results.pose_landmarks:

            landmark_2d_list = results.pose_landmarks
            for j, landmark in enumerate(landmark_2d_list.landmark):
                pose_2d.append(
                    [landmark.x, landmark.y, landmark.z, landmark.visibility])
            pose_2d = np.array(pose_2d)

            landmark_3d_list = results.pose_world_landmarks
            for j, landmark in enumerate(landmark_3d_list.landmark):
                # pose_3d.append([-landmark.z, landmark.x, -landmark.y])
                pose_3d.append(
                    [landmark.x, landmark.y, landmark.z, landmark.visibility])
            pose_3d = np.array(pose_3d)

            frames_data['frames'][frame_idx]['2d_pose'] = list(
                list(pt) for pt in pose_2d)
            frames_data['frames'][frame_idx]['3d_pose'] = list(
                list(pt) for pt in pose_3d)
        else:
            frames_data['frames'][frame_idx]['2d_pose'] = []
            frames_data['frames'][frame_idx]['3d_pose'] = []

    with open(pred_path, 'w') as f:
        json.dump(frames_data, f)

    shutil.rmtree(frames_dir)


parser = ArgumentParser()
parser.add_argument(
    '--video_path',
    type=str,
    default='/path/to/video/file/here/aaa_bbbb_cccc_dddd_121212.mp4',
    help='path to video file')
parser.add_argument(
    '--mp_model_complexity',
    type=int,
    default=2,
    help="MediaPipe's model complexity in [0, 1, 2]")
parser.add_argument(
    '--video_source',
    type=str,
    default='',
    help='source for video - url/ employee')
args = parser.parse_args()


if __name__ == '__main__':
    main()
