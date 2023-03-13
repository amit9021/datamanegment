import os
import pandas as pd


# Read the excel file
dataFrame = pd.read_excel('/home/amit9021/AgadoDB/to_rule_them_all.xlsx')
base_path = "/home/amit9021/AgadoDB/data"

# filtering the data set
angular = ["multi_angles", "single_angle"]
collection = ["2022-12-09_nissim_neve-avivim"]
exercise = ["lunges", "squat"]
person = ["person1", "person2"]
angle = ["angle1"]
what_file_to_use = ['annotation', 'mp2']


filtered_df = dataFrame[(dataFrame['Exercice'].isin(exercise))]

print(filtered_df)


for index, row in filtered_df.iterrows():
    video_name = row['File']
    dirName = video_name.split('.')[0]
    dir_path = os.path.join(
        base_path, row['Angular'], row['Collection'], dirName)

    for file in what_file_to_use:
        for fileName in os.listdir(dir_path):
            if fileName.startswith(file):
                print(f"working on {fileName}")

    ####  From here we start working on filtered files ####
