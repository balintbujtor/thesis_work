from os import listdir
from os.path import isfile, join
import random
import os


# folders where carla images contained per type
folder_path_ims = "/home/balint/PyTorch-YOLOv3/data/custom/images/"
folder_path_labels = "/home/balint/PyTorch-YOLOv3/data/custom/labels/"


# listing all and only the files in the folder
im_files = [f for f in listdir(folder_path_ims) if isfile(join(folder_path_ims, f))]

# listing all and only the files in the folder
label_files = [f for f in listdir(folder_path_labels) if isfile(join(folder_path_labels, f))]

print(len(im_files), len(label_files))

for file in label_files:
    if os.stat(folder_path_labels + str(file)).st_size == 0:
        print("van ures: ", file)
        name, _ = os.path.splitext(file)
        im_name = name + ".jpg"
        print(im_name)
        os.remove(folder_path_ims + im_name)
        os.remove(folder_path_labels + file)

        print("removed images and annotations without objects")

match = False
no = 0

for image in im_files:
    for label in label_files:
        im_id, _ = os.path.splitext(image)
        label_id, _ = os.path.splitext(label)
        if im_id == label_id:
            match = True
            no += 1
            break

    if match is True:
        match = False
        continue

print(no)
