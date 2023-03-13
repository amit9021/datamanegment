import pandas as pd
import os
import tqdm


# Load the excel file into a dataframe
df = pd.read_excel(
    '/home/amit9021/AgadoDB/to_rule_them_all.xlsx')

# Add a new column to the dataframe
df['json_exist'] = False

video_formats = ['.mp4', '.mov', '.MOV', '.webm', '.avi']


# def json_formater(file):

#     if file.endswith('.json'):
#         media_pipe = False
#         for word in file.split('.')[0].split('_'):
#             if word == 'mp1' or word == 'mp2':
#                 media_pipe = True
#                 break
#         if media_pipe:
#             mp_path = os.path.join(dirpath, file)
#             new_name = f"{file.split('_')[0]}_{dirpath.split('/')[-1]}.json"
#             new_path = os.path.join(dirpath, new_name)
#             os.rename(mp_path, new_path)
#             print(mp_path)
#         else:
#             print('not media pipe')


def csv_formater(file, date):
    file_name = file.split('/')[-1]
    path = file.split(file_name)[0]
    if file_name.startswith('annotation') or file_name.startswith('anotation-reps'):

        new_name = f"{'_'.join(file_name.split('_')[:5])}_{date}.csv"
        new_path = os.path.join(path, new_name)
        os.rename(file, new_path)
        print(new_path)
    else:
        print('not annotation')


# Save the dataframe back to the excel file
