""" TO RUN the code: streamlit run app.py"""

import ast
import streamlit
from data_parsing import *
from data_generation import *
import matplotlib.pyplot as plt
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'

if ros_path in sys.path:
    sys.path.remove(ros_path)

inria = plt.imread("/home/mahmoud-ali/PycharmProjects/ficha_app.py/app_images/inria.png")
st.sidebar.image(inria)
st.sidebar.write("--------------------------------")
st.title("Recycling Errors Project")
rec = plt.imread("/home/mahmoud-ali/PycharmProjects/ficha_app.py/app_images/rec2.jpg")
st.image(rec)
st.write("--------------------------------")

st.write("### Please Select Operation")
choice = st.selectbox("Select Operation", ("Select Operation", "Data Parsing", "Data Generation"))
st.write("--------------------------------")

if choice == "Data Parsing":
    show_parsing_page()
elif choice == "Data Generation":
    show_blend_page()
else:
    st.sidebar.write("### WELCOME TO RECYCLING ERRORS")
    st.sidebar.write("Computer vision system for automatic monitoring of trash for garbage collection trucks."
                     "The goal of the vision system is to assess the ratio of recyclable and non-recyclable garbage.")
    st.sidebar.write("--------------------------------")
    name = "MAHMOUD ALI"
    date = "21/07/2021"
    st.sidebar.write("#### CREATED BY:", name)
    st.sidebar.write("#### Date:", date)
