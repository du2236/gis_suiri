from PIL import Image
import numpy as np
import cv2
import os

image_folder = arcpy.GetParameterAsText(0)
output_video = arcpy.GetParameterAsText(1)
fps = arcpy.GetParameter(2)

list_file_name = []
for file_name in os.listdir(image_folder):
    if file_name.endswith('jpg'):
        list_file_name.append(os.path.join(image_folder, file_name))

list_file_name.sort()

image_files = list_file_name

first_frame = Image.open(os.path.join(image_folder, image_files[0]))

width, height = first_frame.size
size = (width, height)

fourcc = cv2.VideoWriter_fourcc(*"MP4V")
out = cv2.VideoWriter(output_video, fourcc, fps, size)

for file_name in image_files:
    img_pil = Image.open(os.path.join(image_folder, file_name))

    img_np = np.array(img_pil)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    out.write(img_bgr)

out.release()