import get_traffic_count as gtc
import specify_roi as roi
import cv2 as cv
import os
import multiprocessing
import time
import enum

# class traffic_light(enum.Enum):
#     red = 1
#     orange = 2
#     green = 3

def initialize_camera(cap):
    _, frame = cap.read()
    return frame 

lanes = ["lane videos/lane_1.mp4", "lane videos/lane_2.mp4", "lane videos/lane_3.mp4"]

caps = [None]*len(lanes)
fpss = []
durations = []
masks = []
for i in range(len(lanes)):
    
    caps[i] = cv.VideoCapture(lanes[i])
    name = os.path.basename(lanes[i])
    name = os.path.splitext(name)[0]
    mask_image = "mask images/mask_"+name+".png"

    fps = caps[i].get(cv.CAP_PROP_FPS)
    #print("frame rate = " + str(fps))
    frame_count =   int(caps[i].get(cv.CAP_PROP_FRAME_COUNT))
    #print("frame count = " + str(frame_count))
    duration = frame_count/fps
    #print("duration = "+str(int(duration/60))+ ":"+ str(duration-int(duration/60)*60))
    
    fpss.append(fps)
    durations.append(duration)

    if not os.path.exists(mask_image):
        image = initialize_camera(caps[i])
        roi.name = name
        roi.image = image
        mask = roi.specify_roi()
        masks.append(mask)
        cv.imshow(mask_image,mask)
        cv.waitKey()
    else:
        mask = cv.imread(mask_image)
        masks.append(mask)
        cv.imshow(mask_image,mask)
        cv.waitKey()

cv.destroyAllWindows()

print(durations)
t = 0
pool = multiprocessing.Pool(processes=len(lanes))

while (all(x > t for x in durations)):
    inputs = []
    start = time.time()
    for i in range(len(lanes)):
        frame_no = t * fpss[i]
        caps[i].set(cv.CAP_PROP_POS_FRAMES,frame_no)
        ret, frame = caps[i].read()
        frame = cv.bitwise_or(frame, masks[i])
        inputs.append([frame, t])

    outputs = pool.starmap(gtc.get_traffic_count, inputs)
    counts, images = zip(*outputs)
    end = time.time()
    print("Time taken is", float(end-start))
    print(counts)
    for i in range(len(lanes)):
        cv.imshow("output_"+str(i+1),images[i])
        cv.waitKey()
    cv.destroyAllWindows()
    t+=20