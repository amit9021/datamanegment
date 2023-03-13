import os
import pandas as pd


class ManualCSV:
    def __init__(self, manual_csv_path, new_csv_path):

        self.manuel_df = pd.read_excel(manual_csv_path)
        self.smart_df = pd.read_excel(new_csv_path)
        self.match_df = pd.DataFrame()

    def create_match_data_frame(self):
        self.match_df["File"] = self.smart_df["File"]
        # print(self.match_df)
        self.convert_old_names()

    def convert_old_names(self):
        for index, row in self.manuel_df.iterrows():
            name = row['video_name'].split('.')[0].split('_')
            if any(x in name[2] for x in ["lunge", "squat", 'situp', 'pushup', 'jumpingjack', "pullup"]):
                self.manuel_df.loc[index,
                                   "video_name"] = f"{name[2]}s_{name[1]}{name[3]}_"
            else:
                self.manuel_df.loc[index,
                                   "video_name"] = f"{name[2]}_{name[1]}{name[3]}_"

        self.add_manual_data()

    def add_manual_data(self):
        for match_index, match_row in self.match_df.iterrows():
            for manual_index, manual_row in self.manuel_df.iterrows():
                manual_name = manual_row['video_name']
                names = match_row['File'].split('_')
                match_name = f"{'_'.join(names[0:2])}_"
                if match_name.startswith(manual_name):
                    self.match_df.loc[match_index,
                                      "source"] = manual_row['source']
                    self.match_df.loc[match_index,
                                      "gender"] = manual_row['gender']
                    self.match_df.loc[match_index,
                                      "LTR_flip"] = manual_row['LTR flip']
                    self.match_df.loc[match_index,
                                      "additional_comments"] = manual_row['additional_comments']

        return self.match_df


path_to_smart_csv = '/home/amit9021/AgadoDB/to_rule_them_all1.xlsx'
path_to_manual_csv = '/home/amit9021/agado_share/AgadoVision/data/data/Annotation_Video.xlsx'

manual_csv = ManualCSV(path_to_manual_csv, path_to_smart_csv)

manual_csv.create_match_data_frame()
manual_csv.match_df.to_excel('/home/amit9021/AgadoDB/manual_data.xlsx')
print(manual_csv.match_df)
