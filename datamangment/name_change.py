import os


for dirpath, dirnames, filenames in os.walk('/home/amit9021/AgadoDB/data/multi_angles/new_data/2023-02-12_nissim_neve_avivim_A'):

    for file in filenames + dirnames:
        # if 'exercise3' in file:

        #     for ex in [f"exercise{i}" for i in range(1, 10)]:
        #         if ex in file:
        #             csv_path = os.path.join(dirpath, file)
        #             file_name = file.replace(
        #                 ex, 'bulgariansquats')
        #             file_ext = file.split('.')[-1]
        #             new_name = f"{'_'.join(file_name[:4])}.{file_ext}"
        #             new_path = os.path.join(dirpath, file_name)
        #             try:
        #                 os.rename(csv_path, new_path)
        #                 print(file_name)
        #             except:
        #                 continue
        #             print(file_name)

        # if '_cut' in file:
        #     csv_path = os.path.join(dirpath, file)
        #     file_name = file.replace('_cut', 'knees')
        #     file_ext = file.split('.')[-1]
        #     new_name = f"{'_'.join(file_name[:4])}.{file_ext}"
        #     new_path = os.path.join(dirpath, file_name)
        #     try:
        #         os.rename(csv_path, new_path)
        #     except:
        #         continue
        #     print(file_name)

        # else:
            # print(f'not annotation')


        if '_cut' in file:
            ext = file.split('.')[-1]
            index = file.find("_cut")

            if index != -1:
                # Replace everything after the "_cut" substring with "knees"
                new_string = file[:index] + "" +"." + ext
                
                csv_path = os.path.join(dirpath, file)
                new_path = os.path.join(dirpath, new_string)
                
                try:
                    os.rename(csv_path, new_path)
                except:
                    continue
                print(new_string)
    