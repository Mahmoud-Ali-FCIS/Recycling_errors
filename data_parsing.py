""" TO RUN the code:
python data_parsing.py
-input_path './files_for_test_pratique/files_for_test_pratique/raw_images.bin'
-width 640
-height 480
 """

import numpy as np
import argparse
import streamlit as st
import tempfile
from data_generation import create_download_zip
import os
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'

if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2


def image_parsing_from_bayer_to_rgb2(input_path, w, h, out_path):

    """
    This function......................
    :param input_path: path of the raw images [Beyer file] .bin string format
    :param w: width of image in int format
    :param h: height of image in int format
    :param out_path: path of folder to save images string format
    :return: list of the extracted images form file
    """
    if not os.path.isdir(f"{out_path}/parsing"):
        os.mkdir(f"{out_path}/parsing")

    list_of_out_images = []
    row_image = w * h
    with open(input_path, mode='rb') as f:
        d = np.fromfile(f, dtype=np.uint8)

    number_of_images = int(len(d) / row_image)

    for i in range(number_of_images):
        start = i * row_image
        end = (i * row_image) + row_image
        out_image = d[start: end]
        out_image = out_image.reshape(h, w)
        out_image = np.array(out_image)
        out_image = cv2.cvtColor(out_image, cv2.COLOR_BAYER_BG2RGB)
        list_of_out_images.append(out_image)
        cv2.imwrite(f'{out_path}/parsing/compressed_image{i+1}.png', out_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])

        # check that image saved and loaded again image is the same as original one
        # saved_img = cv2.imread('compressed.png')
        # assert saved_img.all() != out_image.all()

    return list_of_out_images


def load_bayer_file():
    """

    :return:
    """
    st.write(f"### Upload Bayer")
    f = st.file_uploader(f"Upload Bayer")
    file_name = ""
    if f is None:
        return "", ""
    path = ""
    if f is not None:
        file_name = f.name
        tfile = tempfile.NamedTemporaryFile(delete=False)
        path = tfile.name
        tfile.write(f.read())

    return path, file_name


def show_parsing_page():
    """
    This function to show the page of DATA PARSING in web app
    """
    st.title("Data Parsing")
    st.sidebar.write("### Description of Data Parsing")
    st.sidebar.write("Parsing raw_images.bin file into RGB images and save the result using as lossless-compressed	image."
                     "The file contains one or more images in RAW 8bit Bayer format recorded with an "
                     "OpenMV cam M7 at a resolution of 640x480 px.")
    st.sidebar.write("-------------------------------------")
    file_path, file_name = load_bayer_file()
    st.write("--------------------------------")
    st.write("Resolution of Image")
    w = st.text_input("Width of Image", 640)
    h = st.text_input("Height of Image", 480)
    st.write("--------------------------------")
    parsing = st.button("Parsing")
    if parsing:
        if file_path != "":
            file_format = file_name.split(".")
            if len(file_format) == 1:
                st.error("Please Upload File with Right Format (.bin)!")
            elif file_format[1] == "bin":
                out_images = image_parsing_from_bayer_to_rgb2(file_path, int(w), int(h), "/home/mahmoud-ali/PycharmProjects/"
                                                                                         "ficha_app.py")
                if len(out_images) == 0:
                    st.warning(f"File is empty")
                elif len(out_images) == 1:
                    st.success(f"Success Parsing 1 Image")
                else:
                    st.success(f"Success Parsing {len(out_images)} Images")
                    st.write("-----------------------------------")
                    st.write("### Download Generated Data and Annotation File:")
                    href = create_download_zip("/home/mahmoud-ali/PycharmProjects/ficha_app.py/parsing",
                                               "/home/mahmoud-ali/PycharmProjects/ficha_app.py/parsing.zip",
                                               filename='Parsing Data.zip')
                    st.markdown(href, unsafe_allow_html=True)
                    st.write("-----------------------------------")

                for i in range(len(out_images)):
                    st.write(f"Image # {i+1}")
                    st.image(out_images[i])
                    st.write(f"--------------------------------")
            else:
                st.error("Please Upload File with Right Format (.bin)!")
        else:
            st.error("Please Upload File!")


if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-input_path", "--path_input_raw_images", type=str,
                    default='./files_for_test_pratique/files_for_test_pratique/raw_images.bin',
                    help="path of the raw images [Beyer file] .bin format")
    ap.add_argument("-width", "--width_image", type=int, default=640,
                    help="width of image in int format")
    ap.add_argument("-height", "--height_image", type=int, default=480,
                    help="height of image in int format")

    args = vars(ap.parse_args())

    w = args["width_image"]
    h = args["height_image"]
    path_in = args["path_input_raw_images"]

    image_parsing_from_bayer_to_rgb2(path_in, w, h, ".")
