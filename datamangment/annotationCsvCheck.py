import pandas as pd
import os
import tqdm

# Load the excel file into a dataframe
df = pd.read_excel(
    '/home/amit9021/AgadoDB/to_rule_them_all.xlsx')

# Add a new column to the dataframe
df['csv_exists'] = ""

video_formats = ['.mp4', '.mov', '.MOV', '.webm', '.avi']

# Iterate through the file names in the 'video_name' column
for dirpath, dirnames, filenames in tqdm.tqdm(os.walk("/home/amit9021/AgadoDB/data")):
    for index, row in df.iterrows():
        video_name = row['File']
        for video_format in video_formats:
            if video_name.endswith(video_format):
                csv_file_name = f"annotation_{video_name.replace(video_format, '.csv')}"
                if csv_file_name in filenames:
                    df.loc[index, 'csv_exists'] = True

# Save the dataframe back to the excel file
df.to_excel("/home/amit9021/Downloads/Annotation_Video1.xlsx", index=False)
