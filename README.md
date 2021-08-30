# selfieext
This is a selfieext Python software for hiding background except your face and body.
selfieext.py is based on three state-of-the-art libraries including mediapipe library for segmenting a human from the original image, opencv library for superimposing faces and backgrounds, pyvirtualcam library for outputting the result image to virtual cam.

# How to install selfieext
You need to install OBS studio: 
https://obsproject.com/download

You also need to install pyserial, mediapipe, opencv and pyvirtualcam:

$ pip install pyserial

$ pip install mediapipe

$ pip install opencv-python

$ pip install pyvirtualcam

# How to run selfieext
Run selfieext without any options, background color will be GRAY.
If there are two options BG_COLOR and BG_PATH, BG_PATH option will be treated as priority.

$ python selfieext.py [-h] [--width WIDTH] [--height HEIGHT] [--model_type MODEL_TYPE] [--score_th SCORE_TH]
                      [--bg_color BG_COLOR] [--bg_path BG_PATH]

Run OBS studio and select the popped image as source.
Then press the "start virtual camera" button in OBS studio.
Run any remote meeting application and select OBS virtual camera in video source selection.
