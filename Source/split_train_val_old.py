from os import listdir
from os.path import isfile, join
import random
import os

TEST = 0.5
TRAIN = 0.8


# folders where carla images contained per type
folder_path_rgb = "C:\\Repos\\convert2Yolo\\coco\\test_imgs"

# listing all and only the files in the folder
rgb_files = [f for f in listdir(folder_path_rgb) if isfile(join(folder_path_rgb, f))]

random.shuffle(rgb_files)

leng = len(rgb_files)

test = int(leng*TEST)

train = int(leng*TRAIN)

print(leng, test, train)

for i in range(0, test):
    with open('C:\\Repos\\data\\test.txt', 'a') as file:
        file.write('data/custom/images/' + rgb_files[i] + '\n')

for j in range(test, train):
    with open('C:\\Repos\\data\\addto_train.txt', 'a') as file:
        file.write('data/custom/images/' + rgb_files[j] + '\n')

for k in range(train, leng):
    with open('C:\\Repos\\data\\addto_valid.txt', 'a') as file:
        file.write('data/custom/images/' + rgb_files[k] + '\n')
