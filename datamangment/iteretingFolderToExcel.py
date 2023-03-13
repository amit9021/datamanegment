import os
import pandas as pd


from videoMetaData import look_for_metaData, look_for_csv_json, repetition_col, json_meta_data_change, check_full_body, frame_count


def process_directory(path, file_extension=("mp4", "mov", "MOV", "webm", "avi")):
    data = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file_extension:
                if file.endswith(file_extension):
                    subdirectories = root.replace(
                        path, "").strip("/").split("/")

                    video_data = file.split("_")[0:4]

                    data.append([file] + [file.split(".")[1]] +
                                subdirectories[0:2] + video_data)

    return data


path = '/home/amit9021/AgadoDB/data'
data = process_directory(path)
max_subdirectories = max([len(row) for row in data])
cols = ["File"] + ["Format"] + ["Angular"] + ["Collection"] + \
    ["Exercice"] + ["Person"] + ["Corrections"] + ["Angle"]
df = pd.DataFrame(data, columns=cols)
df = look_for_metaData(df, path)
df = frame_count(path, df)

# TODO: add annotations-reps to CSV
df = look_for_csv_json(df, path)
df = repetition_col(path, df)
# json_meta_data_change(path, df)
df = check_full_body(path, df)

print(df)


df.to_excel('/home/amit9021/AgadoDB/to_rule_them_all1.xlsx', index=False)
print(df)
