import os
import numpy as np
import pandas as pd
import run_cfg


path_to_annotations = '/home/amit9021/AgadoDB/raw_data/2023-01-10_nissim_neve_avivim/tmp/annotation/person1_2023-01-10-150823.csv'


def is_rep_end(row):
    return row['move'] == 'rep_end'


def is_undefined(row):
    return row['move'] == 'undefined'


def is_up(row):
    return row['move'] == 'up'


def is_before(row1, row2):
    return row1['end'] <= row2['start']


def merge_rows(row1, row2):
    return {
        'start': row1['start'],
        'end': row2['end'],
        'move': 'up',
        'error': row1['error'],
        'exercise': row1['exercise']
    }


def convert_to_polina(path_to_annotations, FPS, sound_data):
    if not run_cfg.PONKA_WITH_ERORR:
        ponka_file = pd.read_csv(path_to_annotations,  names=[
            "frame", "action", "error"])

    else:
        ponka_file = path_to_annotations

    ponka_file["frame"] = ponka_file["frame"].apply(
        lambda x: int(x.split("frame")[1].split(".")[0]))

    # ponka_file["frame"] = (ponka_file["frame"] - 0.5 * FPS).astype(int)

    row_action = ponka_file["action"].str.strip(
        '[]').str.split(',').str[0].str.lower()
    mask = ~row_action.isin([])

    ponka_file.loc[mask, "move"] = row_action[mask]

    row_action = ponka_file["action"].str.strip(
        '[]').str.split(',').str[1].str.lower()
    mask = ~row_action.isin([])

    ponka_file.loc[mask, "exercise"] = row_action[mask]

    ponka_file = ponka_file.dropna(subset=['move'])
    ponka_file = ponka_file[ponka_file["move"] != "rep_start"]

    df2 = pd.DataFrame({
        'start': ponka_file['frame'].shift(),
        'end': ponka_file['frame'],
        'start_event': ponka_file['move'].shift(),
        'move': ponka_file['move'],
        'error': ponka_file['error'],
        'exercise': ponka_file['exercise']
    })

    df2 = df2.drop(columns=["start_event"])

    df2 = df2.reset_index(drop=True)

# Apply logic to the data frame
    indices_to_drop = []
    for i, row in df2.iterrows():
        if is_rep_end(row) and i < len(df2)-1:
            next_row = df2.iloc[i+1]
            if is_undefined(next_row):
                df2.at[i, 'move'] = 'up'
            elif is_before(row, next_row) and is_up(next_row):
                df2.at[i, ('start', 'end')] = [row['start'], next_row['end']]
                indices_to_drop.append(i+1)
                df2.at[i, 'move'] = 'up'
            elif i == len(df2)-1:
                df2.at[i, 'move'] = 'up'

    df2.drop(indices_to_drop, inplace=True)
    df2["start"].fillna(1, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    return df2


def convert_to_reps(ponka_file, FPS, df_data, ponka_annotated_video):
    """convert ponka to reps

    Args:
        ponka_file (pandas DF): ponka file converted to polina
        FPS (int): base video FPS
        df_data (pandas df): df of all the videos and this time stamps from wistle
        ponka_annotated_video (str): the video ponka annotated

    Returns:
        pandas DF: df of reps
    """
    test = []
    rep_start = []
    rep_end = []

    rep_count = 0
    currnet_ex = ""
    currnet_error = ""
    if run_cfg.CUTTED_VIDEO:
        df_data[ponka_annotated_video][0] = 0
    for i, row in ponka_file.iterrows():
        row_action = row["action"].strip(
            '[]').split(',')[0].lower()
        row_ex = row["action"].strip(
            '[]').split(',')[-1].lower()
        row_error = row["error"]

        if row_action == "rep_start" or row_action == "rep_end" and row_ex.startswith("exercise"):
            if not row_ex == currnet_ex or not row_error == currnet_error:
                rep_count = 0
            currnet_ex = row_ex
            currnet_error = row_error
            if row_action == "rep_start":
                rep_start = row['frame']
            if row_action == "rep_end":
                rep_end = row['frame']

                rep_count = rep_count + 1
                test.append(
                    {f"start": rep_start, "end": rep_end, "exercise": row_ex, 'error': row["error"], "rep_num": rep_count})

    formating = pd.DataFrame(test)
    return formating


def ponka_with_error(path_to_annotation):
    ponka_file = pd.read_csv(path_to_annotation,  names=[
        "frame", "action", "error"])

    new_df = pd.DataFrame(columns=["frame", "action", "error"])

    actions = []

    for i, row in ponka_file.iterrows():
        actions = [i for i in row["action"].strip(
            '[]').split(',')]
        if len(actions) == 3:
            for action in actions:
                if action.startswith(("rep", "up", "down", "between")):
                    state = action
                if action.startswith("exercise"):
                    exercise = action
                if action.startswith(("error", "correct")):
                    error = action

            new_df.loc[i, "frame"] = row["frame"]
            new_df.loc[i, "action"] = f"[{state},{exercise}]"
            new_df.loc[i, "error"] = error

        else:
            new_df.loc[i, "frame"] = row["frame"]
            new_df.loc[i, "action"] = f"[{actions[-1]}]"
            if i > 0:
                new_df.loc[i, "error"] = new_df["error"][i-1].strip(
                    '[]').split(',')[-1].lower()
            else:
                new_df.loc[i, "error"] = "correct"

    return new_df
