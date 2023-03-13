import os
import shutil

# Define the root folder where the files are located
root_folder = '/home/amit9021/AgadoDB/data/multi_angles/AgadoFilmSession'

# Define the destination folder where the files will be moved
destination_folder = '/home/amit9021/AgadoDB/data/multi_angles/AgadoFilmSession'

# Define the subdirectories inside the root folder (A, B, C)

subdirs = ['lunges', 'squats', 'pushups', 'punches']

# Loop through the subdirectories
for subdir in subdirs:
    # Construct the path to the subdirectory in the root folder
    source_path = os.path.join(root_folder, subdir)

    # Construct the path to the subdirectory in the destination folder
    dest_path = os.path.join(destination_folder, subdir)

    # Loop through the subdirectories inside the source subdirectory (D, E, F)
    for inner_subdir in os.listdir(source_path):
        # Construct the path to the inner subdirectory in the source folder
        inner_source_path = os.path.join(source_path, inner_subdir)

        # Construct the path to the inner subdirectory in the destination folder
        inner_dest_path = os.path.join(dest_path, inner_subdir)

        for inner_subdir2 in os.listdir(inner_source_path):
            # Construct the path to the inner subdirectory in the source folder
            inner_source_path2 = os.path.join(
                inner_source_path, inner_subdir2, "non_corrector")
            # os.mkdir(os.path.join(inner_source_path2, "non_corrector"))

        # Loop through the files and directories inside the inner source subdirectory
            for filename in os.listdir(inner_source_path2):
                # Construct the path to the file in the inner source subdirectory
                file_source_path = os.path.join(
                    inner_source_path2, filename)
                file_dest_path = os.path.join(
                    inner_source_path, inner_subdir2)

                # Construct the path to the file in the inner destination subdirectory

                # Move the file from the source to the destination
                # shutil.move(file_source_path, file_dest_path)
