import os
import pandas as pd
import logging
import time
import datetime
from tqdm import tqdm
from videoNameFormater import rename_to_agado
import mediapipe2agadovideo_v1_2 as mp2agado
import subprocess


logging.basicConfig(
    filename=os.path.join(
        "/home/amit9021/Datamangment/data/datamangment/logs",
        f"log_{datetime.datetime.now()}.txt",
    ),
    level=logging.DEBUG,
)


class UpdatingCSV:
    def __init__(self, csv_path):

        self.df = pd.read_excel(csv_path)
        self.missing_df = pd.DataFrame()
        self.root_to_data = "/home/amit9021/AgadoDB/data"
        self.path_to_data = self.root_to_data
        self.video_formats = (".mp4", ".mov", ".MOV", ".webm", ".avi")

    def check_missing_values(self):
        what_missing = []
        max_col = 0
        data = []
        for index, row in self.df.iterrows():
            for column in row.index.tolist()[13:]:

                if row[column] == "" or pd.isnull(row[column]):
                    what_missing.append(column)
            what = list(set(what_missing))

            data.append(
                [row["File"]]
                + [row["Angular"]]
                + [row["Collection"]]
                + [(i) for i in what]
            )
            # max_col = max(max_col, len(what))
        self.missing_df = pd.DataFrame(
            data,
            columns=["File"]
            + ["Angular"]
            + ["Collection"]
            + [f"miss{i}" for i in range(len(what))],
        )
        print(self.missing_df)

    def work_on_mp(self):
        missing = []
        for index, row in self.missing_df.iterrows():
            for column in row.index.tolist()[3:]:
                if row[column] == "" or pd.isnull(row[column]):
                    continue
                missing.append(row[column].split("_")[0])
            dir_path_to_data = os.path.join(
                self.path_to_data,
                row["Angular"],
                row["Collection"],
                row["File"].split(".")[0],
            )

            if os.path.exists(dir_path_to_data):
                for file in os.listdir(dir_path_to_data):
                    for miss in missing:
                        if file.startswith(miss):
                            print("found")
                            continue

                # missing_values = self.df[self.df.isnull().any(axis=1)]
                # print(missing_values) row.isnull().any() or

    def check_new_data(self):
        logging.info("Checking for new data...")
        """
        This method iterates through all new_data folders within AgadoDB collections.
        ang change the name of the files to the AgadoDB naming convention.
        
        If there is new data, it will add it to a new dataframe called new_df,
        and then check for the following:
        
        2. MP JSONs
        3. Annotations
        4. Add to "Rule Them All" (presumably a reference to a consolidated dataset)

        Returns:
        new_df (pd.DataFrame): DataFrame containing new data that has been added to AgadoDB
        """
        new_df = pd.DataFrame(columns=self.df.columns.tolist())
        i = 0
        new_data_path = []
        for root, dirnames, filenames in tqdm(os.walk(self.path_to_data)):
            for dirname in dirnames:
                if dirname == "new_data":
                    rename_to_agado(self.video_formats,
                                    os.path.join(root, dirname))

                    for r, d, f in tqdm(os.walk(os.path.join(root, dirname))):
                        for filename in f:
                            # check if file is new data

                            logging.info(f"found new data: {filename}")

                            # read in new data and append to new_df
                            new_df.loc[i, "File"] = filename
                            i += 1

                    new_data_path.append(os.path.join(root, dirname))

                # perform checks on new data

        self.create_mp(new_data_path)

        self.add_to_rule_them_all(new_df)
        return new_df

    def create_mp(self, new_data_path):
        """
        creatin media_pipe JSONs in the dataset.

        Args:
        new_data_path (pd.DataFrame): list of paths to new data folders in agado DB
        """
        for path in new_data_path:
            for root, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(self.video_formats):
                        print(f"runnig media pipe on {filename}")
                        cmd = f"python /home/amit9021/Datamangment/data/datamangment/mediapipe2agadovideo_v1_2.py --video_path {os.path.join(root, filename)}"
                        subprocess.call(cmd, shell=True)

    def check_annotations(self, data):
        """
        Check the annotations in the dataset.

        Args:
        data (pd.DataFrame): The dataset to check
        """
        # TODO: Implement logic to check the annotations in the dataset
        pass

    def add_to_rule_them_all(self, data):
        """
        Add the dataset to the consolidated "Rule Them All" dataset.

        Args:
        data (pd.DataFrame): The dataset to add to "Rule Them All"
        """
        # TODO: Implement logic to add the dataset to the consolidated "Rule Them All" dataset
        pass


check_csv = UpdatingCSV("/home/amit9021/AgadoDB/to_rule_them_all.xlsx")

check_csv.check_new_data()
