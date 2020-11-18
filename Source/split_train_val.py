from os import listdir
from os.path import isfile, join
import random
import os

DIVIDER = 0.8

# folders where carla images contained per type
folder_path_rgb = "C:\\Repos\\data\\carla_images_x1\\rgb\\all\\"

# listing all and only the files in the folder
rgb_files = [f for f in listdir(folder_path_rgb) if isfile(join(folder_path_rgb, f))]

random.shuffle(rgb_files)

leng = len(rgb_files)

train = int(leng*DIVIDER)

val = leng - train

for i in range(0, train):
    with open('C:\\Repos\\data\\train.txt', 'a') as file:
        file.write(folder_path_rgb + rgb_files[i] + '\n')

for j in range(train, leng):
    with open('C:\\Repos\\data\\valid.txt', 'a') as file:
        file.write(folder_path_rgb + rgb_files[j] + '\n')

