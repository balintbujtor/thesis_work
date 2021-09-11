from os import listdir
from os.path import isfile, join

# folders where carla images contained per type
folder_path_sem = "/home/balint/carla_images/semantic/all/"
folder_path_conv = "/home/balint/carla_images/converted/all/"
folder_path_rgb = "/home/balint/carla_images/rgb/all/"
folder_path_depth = "/home/balint/carla_images/depth/all/"

# unique annotation id number
cur_ann = 1

# listing all and only the files in the folder
sem_files = [f for f in listdir(folder_path_sem) if isfile(join(folder_path_sem, f))]
conv_files = [f for f in listdir(folder_path_conv) if isfile(join(folder_path_conv, f))]
rgb_files = [f for f in listdir(folder_path_rgb) if isfile(join(folder_path_rgb, f))]
depth_files = [f for f in listdir(folder_path_depth) if isfile(join(folder_path_depth, f))]

sem_files.sort()
conv_files.sort()
rgb_files.sort()
depth_files.sort()

if len(sem_files) == len(conv_files) == len(rgb_files) == len(depth_files):
    print("all folders have the same amount of images")
else:
    print("gond van")


print(len(sem_files), len(conv_files), len(rgb_files), len(depth_files))
for i in range(len(sem_files)):
    try:
        town_no = int(sem_files[i][4])
        if sem_files[i][5] == '0':
            sem_im_num = int(sem_files[i][10] + sem_files[i][11] + sem_files[i][12] + sem_files[i][13])
            conv_im_num = int(conv_files[i][11] + conv_files[i][12] + conv_files[i][13] + conv_files[i][14])
            rgb_im_num = int(rgb_files[i][7] + rgb_files[i][8] + rgb_files[i][9] + rgb_files[i][10])
            depth_im_num = int(depth_files[i][12] + depth_files[i][13] + depth_files[i][14] + depth_files[i][15])

            if i > 0:
                prev_sem_im_num = int(sem_files[i-1][10] + sem_files[i-1][11] + sem_files[i-1][12] + sem_files[i-1][13])
                prev_conv_im_num = int(conv_files[i-1][11] + conv_files[i-1][12] + conv_files[i-1][13] + conv_files[i-1][14])
                prev_rgb_im_num = int(rgb_files[i-1][7] + rgb_files[i-1][8] + rgb_files[i-1][9] + rgb_files[i-1][10])
                prev_depth_im_num = int(depth_files[i-1][12] + depth_files[i-1][13] + depth_files[i-1][14] + depth_files[i-1][15])
            else:
                prev_sem_im_num = 1

        else:
            sem_im_num = int(sem_files[i][9] + sem_files[i][10] + sem_files[i][11] + sem_files[i][12])
            conv_im_num = int(conv_files[i][10] + conv_files[i][11] + conv_files[i][12] + conv_files[i][13])
            rgb_im_num = int(rgb_files[i][6] + rgb_files[i][7] + rgb_files[i][8] + rgb_files[i][9])
            depth_im_num = int(depth_files[i][11] + depth_files[i][12] + depth_files[i][13] + depth_files[i][14])

            if i > 0:
                prev_sem_im_num = int(sem_files[i-1][9] + sem_files[i-1][10] + sem_files[i-1][11] + sem_files[i-1][12])
                prev_conv_im_num = int(conv_files[i-1][10] + conv_files[i-1][11] + conv_files[i-1][12] + conv_files[i-1][13])
                prev_rgb_im_num = int(rgb_files[i-1][6] + rgb_files[i-1][7] + rgb_files[i-1][8] + rgb_files[i-1][9])
                prev_depth_im_num = int(depth_files[i-1][11] + depth_files[i-1][12] + depth_files[i-1][13] + depth_files[i-1][14])
            else:
                prev_sem_im_num = 1

        if not (sem_im_num == conv_im_num == rgb_im_num == depth_im_num):
            print(sem_files[i], conv_files[i], rgb_files[i], depth_files[i])

        if not (sem_im_num == prev_sem_im_num + 1):
            print(sem_im_num, prev_sem_im_num)
            print(sem_files[i], sem_files[i - 1])

    except ValueError:
        print(sem_files[i], conv_files[i], rgb_files[i], depth_files[i])
        break
