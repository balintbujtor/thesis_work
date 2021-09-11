import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
import json


def connected_component_labeling(image, class_no):
    """
    this function calculates the connected component labeling

    :param image: the image to process
    :param class_no: which class to be highlighted
    :return: the no of components and the a numpy array containing each component,
            each components is labeled with the number of it
    """

    # storing only the red channel and creating ones where a pixel is equal to a given category
    red = image[:, :, 2]
    binary = (red == int(class_no)).astype('uint8')

    # 1 to 255 conversion
    _, im_thres = cv2.threshold(binary, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow('threshold', im_thres)
    # cv2.waitKey(0)

    # calculating the components
    num_labels, labels_im = cv2.connectedComponents(im_thres)

    return num_labels, labels_im


def im_show_components(labels):
    """
    this function highlights the components

    source of the code:
    https://stackoverflow.com/questions/46441893/connected-component-labeling-in-python

    :param labels: the connected component labels
    :return: the colored image

    """

    # Map component labels to hue val
    label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    # set bg label to black
    labeled_img[label_hue == 0] = 0

    # cv2.imshow('labeled.png', labeled_img)
    # cv2.waitKey(0)


# global variable for testing
all_bboxes = 0


def create_bounding_box(label_num, label_im):
    """
    this function creates the bounding boxes from the labelled images

    :param label_num: the total number of components in the images
    :param label_im: the labelled image, each component has a unique id associated to it
    :return: a list of the bounding boxes
    """
    global all_bboxes

    # the returning list containing the bounding boxes
    bboxes = []
    # bbox_im = []

    # going through all components in an image
    for component in range(1, label_num):
        # new_comp = False
        # print(component)

        # binarizing the image then converting it to 255
        binary = (label_im == component).astype('uint8')
        _, im_thres = cv2.threshold(binary, 0, 255, cv2.THRESH_BINARY)

        # generating the bounding boxes
        x, y, w, h = cv2.boundingRect(im_thres)

        # if the area of the bounding box is bigger than a threshold the we save the bbox
        if h*w > 50:
            # new_comp = True
            bboxes.append([x, y, w, h])
            all_bboxes += 1
            # bbox_im = cv2.rectangle(img_conv, (x, y), (x + w, y + h), (0, 0, 255), 1)
        # if component == label_num - 1 and new_comp is True:
            # cv2.imshow('bbox', bbox_im)
            # cv2.waitKey(0)

    return bboxes


# category dictionary for carla classes
category_dict = {4: "Pedestrian", 10: "Vehicles", 12: "TrafficSign", 18: "TrafficLight"}

carla_dataset = {
    "info": {
        "description": "Carla 2020 Dataset",
        "url": "",
        "version": "1.0",
        "year": 2020,
        "contributor": "Balint Bujtor",
        "date_created": "20120/10/29"
    },
    "licenses": "https://carla.org/",
    "images": [],
    "categories": [
        {"supercategory": "person", "id": 1, "name": "person"},
        {"supercategory": "vehicle", "id": 2, "name": "vehicle"},
        {"supercategory": "outdoor", "id": 3, "name": "traffic sign"},
        {"supercategory": "outdoor", "id": 4, "name": "traffic light"}
    ],
    "annotations": []
}

# -------------------------
# toolchain:
# -------------------------

# folders where carla images contained per type
folder_path_sem = "/home/balint/carla_images/semantic/all/"
folder_path_conv = "/home/balint/carla_images/converted/all/"
folder_path_rgb = "/home/balint/carla_images/rgb/all/"

# unique annotation id number
cur_ann = 1

# listing all and only the files in the folder
sem_files = [f for f in listdir(folder_path_sem) if isfile(join(folder_path_sem, f))]
conv_files = [f for f in listdir(folder_path_conv) if isfile(join(folder_path_conv, f))]
rgb_files = [f for f in listdir(folder_path_rgb) if isfile(join(folder_path_rgb, f))]

sem_files.sort()
conv_files.sort()
rgb_files.sort()

# checking
print(len(sem_files), len(conv_files), len(rgb_files))
if len(sem_files) == len(conv_files) == len(rgb_files):
    pass
else:
    raise Exception

# looping through all images
for i in range(len(sem_files)):

    # creating full path
    full_path_sem = folder_path_sem + sem_files[i]
    full_path_conv = folder_path_conv + conv_files[i]

    # print(sem_files[i], conv_files[i])

    # condition if we are in town10 / the file name is different in that case
    TOWN_NO = int(sem_files[i][4] + sem_files[i][5])
    IM_NO = int(sem_files[i][10] + sem_files[i][11] + sem_files[i][12] + sem_files[i][13])
    IM_ID = TOWN_NO*10000 + IM_NO

    print(TOWN_NO, IM_NO, IM_ID)

    # image dict to append carla data
    new_im_dict = {
      "license": "",
      "file_name": str(rgb_files[i]),
      "coco_url": "",
      "height": 576,
      "width": 1024,
      "date_captured": "",
      "flickr_url": "",
      "id": IM_ID
    }
    carla_dataset["images"].append(new_im_dict)

    # print(new_im_dict)

    # reading the image
    img = cv2.imread(full_path_sem)
    img_conv = cv2.imread(full_path_conv)
    # print(full_path_sem)
    # print(rgb_files[i])

    # cv2.imshow('orig', img_conv)
    # cv2.waitKey(0)

    # cycling through the category dict to check if a picture has that kind of object in it
    for key in category_dict:
        # print(key)

        # saving the number of labels and the labelled image of a given cat
        no_labels, im_labels = connected_component_labeling(img, key)
        im_show_components(im_labels)

        # acquiring the compponents
        bounding_boxes = create_bounding_box(no_labels, im_labels)

        # appending the annotations with all of the bounding boxes
        for j in range(len(bounding_boxes)):
            # area calculation
            area = bounding_boxes[j][2]*bounding_boxes[j][3]

            # category_dict = {4: "Pedestrian", 10: "Vehicles", 12: "TrafficSign", 18: "TrafficLight"}
            if key == 4:
                cat_id = 1
            elif key == 10:
                cat_id = 2
            elif key == 12:
                cat_id = 3
            elif key == 18:
                cat_id = 4
            else:
                print(cat_id)
                raise Exception

            new_ann_dict = {'segmentation': [[]],
                            'area': area,
                            'iscrowd': 0,
                            'image_id': IM_ID,
                            'bbox': bounding_boxes[j],
                            'category_id': cat_id,
                            'id': cur_ann
                            }

            # print(new_ann_dict)

            carla_dataset["annotations"].append(new_ann_dict)
            cur_ann += 1

# check
print(all_bboxes, len(carla_dataset["annotations"]))
if all_bboxes != len(carla_dataset["annotations"]):
    raise Exception

# saving the json file
with open('/home/balint/carla_annotations.json', 'w') as file:
    json.dump(carla_dataset, file)
