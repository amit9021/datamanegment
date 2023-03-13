
import datetime
import os

import pandas as pd
import run_cfg
from annotation_check import PonkaValidation
from convert_to_polina import (convert_to_polina, convert_to_reps,
                               ponka_with_error)
from loguru import logger as logging
from videohandling.cut_to_start import cut_to_ponka_annotation
from videohandling.utils.utils import (convert_to_timestamp, get_video_FPS,
                                       to_ponka_dict)

logging.add(
    f"/home/amit9021/Datamangment/data/datamangment/logs/ponka_{datetime.datetime.now()}.log", backtrace=True, diagnose=True)


def main():
    """
    This program reads `ponka annotated CSV` files.
    ----------------------------------------------- 
    It then matches each annotation file to the corresponding person's video, 
    extracts relevant information such as the frame rate and the time when each movement/rep occurs, 
    and uses this information to cut the video into segments based on the annotations.
    The resulting segments are saved as new video files.

    The program assumes that the annotation files are stored in a directory called 'annotation' under a specified working directory, 
    and that the video files are stored in the same working directory. It also requires a CSV file containing sound data, 
    which is used to detect the start and end times of each whistle blow.

        `working directory:
        |-- annotation
        |   |-- person1_samename.csv
        |   |-- ...
        |-- cut_person1_angle1_samename.mp4
        |-- cut_person1_angle2_othername.mp4
        |-- ...`

    Usage:
    ------
        To use this program, simply run the 'main()' function.

    Parameters:
        The program's parameters are defined in the 'run_cfg.py' file.

    Returns:
        The program saves the resulting video files in the working directory inside result folder.

    """
    working_path = run_cfg.WORKING_PATH
    annotations_path = os.path.join(working_path, 'annotation')
    sound_data = to_ponka_dict(pd.read_csv(
        os.path.join(working_path, 'wistle_data.csv')))

    for annotation_file in os.listdir(annotations_path):
        logging.info(f"starting program...")

        """
        loking for ponka csv files
        at annotations folder
        """

        if annotation_file.endswith('.csv'):
            ponka_filename = annotation_file.split('.')[0].split('_')[1:]
            ponka_filename = '_'.join(ponka_filename)

            person_number = annotation_file.split('_')[0]
            ponka_file = pd.read_csv(os.path.join(
                annotations_path, annotation_file), names=["frame", "action", "error"])

            # if not person == "person30":
            #     continue
            logging.info(f"working on annotation {annotation_file}")

            for video in os.listdir(working_path):
                if not video.endswith('.csv') and not video.startswith('cut'):

                    video_name = video.split(".")[0].split('_')[1:]
                    video_name = '_'.join(video_name)

                    if ponka_filename in video_name:

                        """
                        looking for the video that match the ponka file
                        to get FPS details
                        and shifting the csv file to the same time
                        """
                        logging.info(
                            f"working on video {video}, wich is ponka file")
                        path_to_annotatated_video = os.path.join(
                            working_path, video)
                        FPS = get_video_FPS(path_to_annotatated_video)

                        if run_cfg.PONKA_WITH_ERORR:
                            ponka_file = ponka_with_error(
                                os.path.join(annotations_path, annotation_file))
                            polina_file = convert_to_polina(
                                ponka_file, FPS, sound_data[video][0])
                            reps = convert_to_reps(
                                ponka_file, FPS, sound_data, video)
                        else:
                            ponka_file = pd.read_csv(os.path.join(
                                annotations_path, annotation_file), names=["frame", "action", "error"])
                            polina_file = convert_to_polina(
                                os.path.join(annotations_path, annotation_file))
                            reps = convert_to_reps(
                                ponka_file, FPS, sound_data, video)

                        logging.info(f"reps are: \n {reps}")
                        logging.info(f"polina file is: \n {polina_file}")
                        try:
                            validation = PonkaValidation(
                                ponka_file, FPS, polina_file)
                            validation()
                            # polina_file = convert_to_timestamp(
                            #     polina_file, FPS, sound_data[video][0])
                            # reps = convert_to_timestamp(
                            #     reps, FPS, sound_data[video][0])

                            person_videos = [video for video in os.listdir(
                                working_path) if video.startswith('cut') and video.split('_')[1] == person_number]
                            for video in person_videos:

                                logging.info(
                                    f"cutting person {person_number} in video {video}")
                                path_to_video = os.path.join(
                                    working_path, video)

                                cut_to_ponka_annotation(
                                    path_to_video, working_path, person_number, polina_file, FPS, reps, sound_data)

                            break

                        except Exception as e:
                            logging.error(e)
                            print(e)
                            break


if __name__ == "__main__":
    main()
