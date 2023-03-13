import os
from accepted_formats import video_formats, extracted_data


path = '/home/amit9021/AgadoDB/data'


for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        if not any(file.endswith(f"{i}") for i in video_formats) and not any(file.startswith(f"{x}") for x in extracted_data):
            print(file)
