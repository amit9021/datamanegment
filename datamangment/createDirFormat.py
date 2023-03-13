import os


def create_folder_structure():
    root_folder = '/home/amit9021/AgadoDB/data/multi_angles/sortingtmp'
    exersize_folders = ['lunges', 'squats', 'pushups', 'punches']
    person_folders = ['amit', 'nadav', 'polina', 'tazch', 'vit']

    error_folders = []
    angle_folders = ['angle1', 'angle2', 'angle3']

    for exersize_folder in exersize_folders:
        ex_path = os.path.join(root_folder, exersize_folder)
        os.makedirs(os.path.join(ex_path), exist_ok=True)
        for person_folder in person_folders:
            person_path = os.path.join(ex_path, person_folder)
            os.makedirs(os.path.join(person_path), exist_ok=True)

            if len(error_folders) > 0:
                for error_folder in error_folders:
                    error_path = os.path.join(person_path, error_folder)
                    os.makedirs(os.path.join(error_path), exist_ok=True)
                    for angle_folder in angle_folders:
                        angle_path = os.path.join(error_path, angle_folder)
                        os.makedirs(os.path.join(angle_path), exist_ok=True)
            else:  # no error folder
                for angle_folder in angle_folders:
                    angle_path = os.path.join(person_path, angle_folder)
                    os.makedirs(os.path.join(angle_path), exist_ok=True)


if __name__ == '__main__':
    create_folder_structure()
