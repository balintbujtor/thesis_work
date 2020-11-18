from os import listdir
from os.path import isfile, join
import random
import os


# folders where carla images contained per type
folder_path_sem = "C:\\Repos\\data\\carla_images_x1\\semantic\\all\\"
folder_path_conv = "C:\\Repos\\data\\carla_images_x1\\converted\\all\\"
folder_path_rgb = "C:\\Repos\\data\\carla_images_x1\\rgb\\all\\"
folder_path_depth = "C:\\Repos\\data\\carla_images_x1\\depth\\all\\"

folder_path_labels = "C:\\Repos\\data\\carla_text_anns\\"

# listing all and only the files in the folder
sem_files = [f for f in listdir(folder_path_sem) if isfile(join(folder_path_sem, f))]
conv_files = [f for f in listdir(folder_path_conv) if isfile(join(folder_path_conv, f))]
rgb_files = [f for f in listdir(folder_path_rgb) if isfile(join(folder_path_rgb, f))]
depth_files = [f for f in listdir(folder_path_depth) if isfile(join(folder_path_depth, f))]

# listing all and only the files in the folder
label_files = [f for f in listdir(folder_path_labels) if isfile(join(folder_path_labels, f))]

print(len(rgb_files), len(conv_files), len(sem_files), len(depth_files), len(label_files))

for file in label_files:
    if os.stat(folder_path_labels + str(file)).st_size == 0:
        print("van ures: ", file)
        name, _ = os.path.splitext(file)
        im_name = name + ".jpg"
        print(im_name)
        os.remove(folder_path_rgb + im_name)
        os.remove(folder_path_labels + file)

print("removed images and annotations without objects")

