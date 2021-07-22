""" TO RUN the code:
python data_generation.py
--path_background "./files_for_test_pratique/files_for_test_pratique/background.png"
--path_object "./files_for_test_pratique/files_for_test_pratique/object.png"
--size_of_data 1000 """

import os
from PIL import Image
import random
import numpy as np
import pickle
import argparse
import streamlit as st
import tempfile
from skimage import img_as_float, io
import base64
import shutil
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'

if ros_path in sys.path:
    sys.path.remove(ros_path)

import cv2


def create_download_zip(zip_directory, zip_path, filename='dataset.zip'):
    """
    This function for zip a folder of file and create link for downloading
        zip_directory (str): path to directory  you want to zip
        zip_path (str): where you want to save zip file
        filename (str): download filename for user who download this
        :return: href (str) is a link for downloading
    """
    shutil.make_archive(zip_directory, 'zip', zip_directory)
    with open(zip_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
            Download \
        </a>'
        return href


def basic_data_annotation_information(dictionary):
    """
    This function to set the basic information of the annotation file like info and categories
    :param dictionary: empty annotation dictionary
    :return: (dictionary) dictionary after fill it with the basic information
    """
    dictionary["info"] = {"description": "Trash 2021 Dataset",
              "version": "1.0",
              "year": 2021,
              "date_created": "2021/07/17"}
    dictionary["categories"] = [{"supercategory": "trash", "id": 1, "name": "bottle"}]
    return dictionary


def generate_data_using_blend_two_images2(pth1, pth2, size, visualize_bbox, path_out):
    """
    This function to generate the data using blend to images [background and object] and create and save COCO style
    annotation file
    :param pth1: (str) the path of the background image
    :param pth2: (str) the path of the object image
    :param size: (int) the number which refer to the size of generated data
    :param visualize_bbox: (boolean) flag to determine save images with bbox
    :param path_out:(str) the path of output generated images
    :return:
    out_images: (list) list of output generated images
    out_images_bbox: (list) list of output generated images with bbox
    out_images_mask: (list) list of mask of output generated images
    """
    data_annotations = dict()
    data_annotations = basic_data_annotation_information(data_annotations)
    list_annotate_images = []
    list_images_info = []
    out_images = []
    out_images_bbox = []
    out_images_mask = []
    if not os.path.isdir(f"{path_out}/dataset"):
        os.mkdir(f"{path_out}/dataset")
    if visualize_bbox:
        if not os.path.isdir(f"{path_out}/dataset/data_bbox"):
            os.mkdir(f"{path_out}/dataset/data_bbox")
    if not os.path.isdir(f"{path_out}/dataset/data_mask"):
        os.mkdir(f"{path_out}/dataset/data_mask")
    if not os.path.isdir(f"{path_out}/dataset/data"):
        os.mkdir(f"{path_out}/dataset/data")
    for i in range(size):
        back = Image.open(pth1)
        back = back.convert('RGBA')
        x, y = back.size

        front = Image.open(pth2)
        angle = random.randint(0, 360)
        front = front.convert('RGBA').rotate(angle, expand=True, resample=Image.BICUBIC)
        x2, y2 = front.size

        if x*y < x2*y2:
            return [], [], []
        r1 = random.randint(0, x-x2)
        r2 = random.randint(0, y-y2)

        r, g, b, alpha = front.split()
        image_copy = back.copy()
        position = (r1, r2)
        image_copy.paste(front, position, alpha)

        mask = Image.new('RGB', (x, y), (0, 0, 0))
        mask.paste(front, position, alpha)
        # mask.show()
        mask = np.array(mask)
        mask[mask > 0] = 255
        cv2.imwrite(f"{path_out}/dataset/data_mask/mask_image{i}.png", mask)
        out_images_mask.append(mask)
        # cv2.waitKey(0)

        if visualize_bbox:
            im = image_copy.copy()
            im = np.array(im)
            cv2.rectangle(im, (r1, r2), (r1 + x2, r2 + y2), (0, 255, 0), 2)
            out_images_bbox.append(im)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f"{path_out}/dataset/data_bbox/image{i}.png", im)

        annotate_image = dict()
        annotate_image["id"] = i
        annotate_image["bbox"] = [r1, r2, x2, y2]
        annotate_image["image_id"] = i
        annotate_image["segmentation"] = mask
        annotate_image["category_id"] = 1
        list_annotate_images.append(annotate_image)
        image_copy.save(f"{path_out}/dataset/data/image{i}.png")
        out_images.append(np.array(image_copy))

        images_info = dict()
        images_info["id"] = i
        images_info["width"] = x
        images_info["height"] = y
        images_info["file_name"] = f"image{i}.png"
        list_images_info.append(images_info)

    data_annotations["annotations"] = list_annotate_images
    data_annotations["images"] = list_images_info
    with open(f'{path_out}/dataset/data_annotations.json', 'wb') as fp:
        pickle.dump(data_annotations, fp)

    return out_images, out_images_bbox, out_images_mask


def load_image(type):
    """
    This function to read and load image in web app
    :param type: (str) determine the name of laded image
    :return:
    img:(ndarray) ndarray of float for the loaded image
    path:(str) the full path for uploaded image
    file_name:(str) the name of image
    """
    st.write(f"### Upload {type} Image")
    f = st.file_uploader(f"Upload {type} Image")
    img = None
    path = ""
    file_name = ""
    if f is None:
        return "", "", ""
    if f is not None:
        file_name = f.name
        format_file = file_name.split(".")
        if len(format_file) == 1:
            return "_", "_", "_"
        elif format_file[1] not in ["png", "jpg", "jpeg"]:
            return "_", "_", "_"
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(f.read())
        path = tfile.name
        img = img_as_float(io.imread(tfile.name))
        st.write(f"### {type} Image")
        st.write(f"Shape of {type} Image: ", img.shape)
        im = st.image(img)
    return img, path, file_name


def check_files_format(file_name_back, file_name_object):
    """
    This function for check the format of the loaded images
    :param file_name_back: (str) name of background image
    :param file_name_object: (str) name of object image
    :return:
    check: (boolean) flag refer to the format of the files correctly or not
    """
    format_back = file_name_back.split(".")
    format_object = file_name_object.split(".")
    if len(format_back) == 1 or len(format_object) == 1:
        check = False
    elif format_back[1] in ["png", "jpg", "jpeg"] and format_object[1] in ["png", "jpg", "jpeg"]:
        check = True
    else:
        check = False
    return check


def show_blend_page():
    """
    This function to show the page of DATA GENERATION in web app
    """
    st.title("Data Generation")
    st.sidebar.write("### Description of Data Generation")
    st.sidebar.write("Create a dataset of a synthetic images composed of a textured	background and "
                     "between 0 and 4 instances of an object. The data created by blending the object with background at "
                     "random positions and at random angles. "
                     "Then create an COCO-style annotations for object detection for the generated dataset.")
    st.sidebar.write("-------------------------------------")
    st.write("### Size of Data")
    size = st.text_input("Size of Data", 6)
    st.write("-------------------------------------")
    _, pth_back, file_name_back = load_image("Background")
    st.write("-------------------------------------")
    _, pth_front, file_name_object = load_image("Object")
    path_out = "/home/mahmoud-ali/PycharmProjects/ficha_app.py"
    st.write("-------------------------------------")
    generate = st.button("Generate Data")
    if generate:
        if file_name_back == "" or file_name_object == "":
            st.error("Please upload the requirement images!")
        elif file_name_back == "_" or file_name_object == "_":
            st.error("Please Upload File with Right Format [png, jpg, jpeg]!")
        else:
            if file_name_back == "_" or file_name_object == "_":
                st.error("Please Upload File with Right Format [png, jpg, jpeg]!")
            else:
                if check_files_format(file_name_back, file_name_object):
                    list_of_image,  list_of_image_bbox, list_of_image_mask = generate_data_using_blend_two_images2(
                        pth_back, pth_front, int(size), True, path_out)
                    if len(list_of_image) != 0:
                        st.success(f'success Generate {len(list_of_image)} images')
                        st.write("-----------------------------------")
                        st.write("### Download Generated Data and Annotation File:")
                        href = create_download_zip("/home/mahmoud-ali/PycharmProjects/ficha_app.py/dataset",
                                                   "/home/mahmoud-ali/PycharmProjects/ficha_app.py/dataset.zip",
                                                   filename='dataset.zip')
                        st.markdown(href, unsafe_allow_html=True)
                        st.write("-----------------------------------")
                        st.write("Sample of New Data")
                        sample_images = list_of_image[:3]
                        indices_on_page = ["Sample #1", "Sample #2", "Sample #3"]
                        st.image(sample_images, width=232, caption=indices_on_page)
                        st.write("Sample of New Data with BBox")
                        sample_images_bbox = list_of_image_bbox[:3]
                        indices_on_page_bbox = ["Sample bbox #1", "Sample bbox #2", "Sample bbox #3"]
                        st.image(sample_images_bbox, width=232, caption=indices_on_page_bbox)
                        st.write("Sample of Mask for New Data")
                        sample_images_mask = list_of_image_mask[:3]
                        indices_on_page_mask = ["Sample mask #1", "Sample mask #2", "Sample mask #3"]
                        st.image(sample_images_mask, width=232, caption=indices_on_page_mask)
                    else:
                        st.error("Please upload the requirement images correctly! [You upload Object image in place of "
                                 "Background image]")
                else:
                    st.error("Please Upload File with Right Format [png, jpg, jpeg]!")


if __name__ == '__main__':

    ap = argparse.ArgumentParser()

    ap.add_argument("-path_back", "--path_background", type=str,
                    default="./files_for_test_pratique/files_for_test_pratique/background.png",
                    help="path of the background image.")

    ap.add_argument("-path_obj", "--path_object", type=str,
                    default="./files_for_test_pratique/files_for_test_pratique/object.png",
                    help="path of the object image.")

    ap.add_argument("-size_data", "--size_of_data", type=int, default=1000,
                    help="size of generated data")

    args = vars(ap.parse_args())

    pth_background = args["path_background"]
    pth_object = args["path_object"]
    pth_out = args["size_of_data"]

    generate_data_using_blend_two_images2(pth_background, pth_object, pth_out, True, ".")
