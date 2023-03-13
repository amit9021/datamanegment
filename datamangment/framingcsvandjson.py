import os
import pandas as pd
from tqdm import tqdm


def look_for_csv_json(df, path):
    file_extension = (".csv", ".json")
    video_formats = ['.mp4', '.mov', '.MOV', '.webm', '.avi']
    predefined_words = ('annotation', 'mp1', 'mp2')
    df["annotation"] = ""
    df["mp1_json"] = ""
    df["mp2_json"] = ""

    with tqdm(total=df.shape[0], desc="Gathering Csv And Json Data") as pbar:
        for index, row in df.iterrows():
            csv_json_found = False
            video_name = row['File']

            for root, dirnames, files in os.walk(path):
                for file in files:
                    try:
                        file_nnn = file.split('_', 1)[1].split('.')[0]
                    except:
                        continue

                    if not video_name.split(".")[0] == file_nnn:
                        continue

                    if not file.endswith(file_extension):
                        continue

                    if file.endswith(file_extension) and file.startswith('annotation'):
                        csv_json_found = True
                        df.loc[index, 'annotation'] = "yes"
                    else:
                        df.loc[index, 'annotation'] = "no"
                    if file.endswith(file_extension) and file.startswith('mp1'):
                        csv_json_found = True
                        df.loc[index, 'mp1_json'] = "yes"
                    else:
                        df.loc[index, 'mp1_json'] = "no"
                    if file.endswith(file_extension) and file.startswith('mp2'):
                        csv_json_found = True
                        df.loc[index, 'mp2_json'] = "yes"
                    else:
                        df.loc[index, 'mp2_json'] = "no"
                if not csv_json_found:
                    df.loc[index, 'annotation'] = "no"
                    df.loc[index, 'mp1_json'] = "no"
                    df.loc[index, 'mp2_json'] = "no"
                if csv_json_found:
                    break
            pbar.update(1)

    return df
