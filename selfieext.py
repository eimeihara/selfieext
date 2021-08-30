import argparse
import numpy as np
from enum import Enum

import cv2
import serial.tools.list_ports
import mediapipe as mp
import pyvirtualcam
from pyvirtualcam import PixelFormat


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--width", help='cap width', type=int, default=1280)
    parser.add_argument("--height", help='cap height', type=int, default=720)

    parser.add_argument("--model_type", help='model type', type=int, default=1)
    parser.add_argument("--score_th", help='score threshold', type=float, default=0.5)
    parser.add_argument("--bg_color", help='background color ex.\'BLACK\',\'GRAY\',\'WHITE\'', type=str, default='GRAY')
    parser.add_argument("--bg_path", help='background image path', type=str, default=None)

    args = parser.parse_args()

    return args

def serial_find():
    ports =[]
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p.name, '- Port ID : '+str(p.hwid[-1]))

    print(f'Number of connected serial: {len(ports)}')

class bg_color(Enum):
    BLACK = (0,0,0)
    GRAY = (192,192,192)
    WHITE = (255,255,255)

if __name__ == '__main__':
    args = get_args()
    serial_find()

    port_id = input('select port ID : ')
    if not port_id.isnumeric():
        raise ValueError("error port ID")
                            
    # only windows
    cap = cv2.VideoCapture(int(port_id), cv2.CAP_DSHOW)
    print("cap.isOpened() :", cap.isOpened())

    if not cap.isOpened():
        raise ValueError("error opening cam port")
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    BG_COLOR = None
    for color in bg_color:
        if color.name == args.bg_color:
            BG_COLOR = color.value

    # create background image
    if args.bg_path == None:
        bg_image = np.zeros((height, width, 3), dtype=np.uint8)
        bg_image[:] = BG_COLOR
    else:
        bg_image = cv2.imread(args.bg_path)
        bg_image = cv2.resize(bg_image, (width, height))
    

    mp_drawing = mp.solutions.drawing_utils
    mp_selfie_segmentation = mp.solutions.selfie_segmentation

    with mp_selfie_segmentation.SelfieSegmentation(model_selection=args.model_type) as selfie_segmentation:
        with pyvirtualcam.Camera(width, height, fps=30, fmt=PixelFormat.BGR) as cam:
            print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')
            count = 0

            while cap.isOpened():
                # Restart video on last frame
                if count == length:
                    count = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                ret, frame = cap.read()
                if not ret:
                    raise RuntimeError('Error fetching frame')

                frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                results = selfie_segmentation.process(frame)

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > args.score_th
                output_image = np.where(condition, frame, bg_image)
                
                cam.send(output_image)
                cam.sleep_until_next_frame()
                
                count += 1
            
    cap.release()
