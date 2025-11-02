import numpy as np
import cv2 #pip install opencv-python i think lmao (laughing my ah off)
import tkinter as kt
import VideoLoop
from datetime import datetime
import os
from screeninfo import get_monitors

"""organize monitor displaying"""
live = cv2.VideoCapture(0) 
monitors = get_monitors()
two = False
two = len(monitors) > 1

cv2.namedWindow('Live Video', cv2.WINDOW_NORMAL)
cv2.namedWindow('Replay', cv2.WINDOW_NORMAL)


if two: #replay will be on the big screen.
    cv2.moveWindow('Replay', monitors[1].x, monitors[1].y)
    cv2.setWindowProperty('Replay', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.resizeWindow('Live Video', monitors[0].width, monitors[0].height)
    cv2.moveWindow('Live Video', 0, 0)
else: #replay will be windowed fullscreen if theres only 1 monitor. hide live action.
    cv2.resizeWindow('Replay', monitors[0].width, monitors[0].height)
    cv2.moveWindow('Replay', 0, 0)




"""create files"""

os.makedirs('clips', exist_ok=True)
pathname = "clips\\" + 'session ' + str(datetime.now().strftime('%b-%d-%y'))
os.makedirs(pathname, exist_ok=True)
name = 'stream ' + str(datetime.now().strftime('%H-%M')) + '.mp4'
fullpath = os.path.join(pathname, name)

#handle someone creating a new stream directly after a previous one so stuff isnt deleted
nm=0
while os.path.exists(fullpath):
    name = 'stream ' + str(nm) + ' ' + str(datetime.now().strftime('%H-%M')) + '.mp4'
    fullpath = os.path.join(pathname,name)
    nm+=1




#get fps of camera
fps = live.get(cv2.CAP_PROP_FPS)
if(fps <= 0):
    fps = 30

fourcc = cv2.VideoWriter.fourcc(*'mp4v')
out = cv2.VideoWriter(fullpath, fourcc, fps, (int(live.get(3)),int(live.get(4)))) #write to file

jumpSize = int(fps * 5)
stepSize = int(2 * fps / 30)
clipLength = int(fps * 5) #clip length 5 seconds each direction

"""declare methods lmao (laughing my ah off)"""
play = True
toEnd = False 
jumpBack5 = False
jumpForward5 = False
stepFore = False
stepBack = False
clip = False

frameCur = -1
lbound = 0
rbound = -1
clipCount = 0

videoQueue = VideoLoop.CircularQueue(int(fps * 600)) # 10 minutes

"""infinite loop ran 30 times per second due live.read(). """
while 1:
    ret, frame = live.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    out.write(frame)
    rbound += 1

    if videoQueue.isFull():
        lbound += 1
        videoQueue.dequeue()

    videoQueue.enqueue(frame)
    
    """ \"methods\" """
    if play:
        frameCur+=1
    else:
        frameCur = lbound if lbound >= frameCur else frameCur #max of lbound and framecur

    if toEnd:
        frameCur = rbound
        toEnd = False

    if jumpBack5:
        #go back jumpSize frames. in the actual video, stop at the back and prevent wrapping
        frameCur = lbound if lbound > frameCur - jumpSize else frameCur - jumpSize # max of lbound and (framecur-jumpsize)
        jumpBack5 = False

    if jumpForward5:
        #go forward jumpSize frames. in the actual video, stop at the front and prevent wrapping
        frameCur = rbound if rbound < frameCur + jumpSize else frameCur + jumpSize #min of rbound and (framecur+jumpsize)
        jumpForward5 = False

    if stepBack:
        #go back jumpSize frames. in the actual video, stop at the back and prevent wrapping
        frameCur = lbound if lbound > frameCur - stepSize else frameCur - stepSize
        stepBack = False

    if stepFore:
        #go forward jumpSize frames. in the actual video, stop at the front and prevent wrapping
        frameCur = rbound if rbound < frameCur + stepSize else frameCur + stepSize 
        stepFore = False

    if clip:
        strt = max(frameCur - clipLength, lbound)
        end = min(frameCur + clipLength, rbound)
        name = 'clip-' + str(clipCount) + ' ' + str(datetime.now().strftime('%H-%M-%S')) + '.mp4'
        fullpath = os.path.join(pathname, name)
        clipFile = cv2.VideoWriter(fullpath, fourcc, fps, (int(live.get(3)),int(live.get(4))))
        for i in range(strt, end):
            clipFile.write(videoQueue.get(i%videoQueue.maxSize))

        cv2.putText(frame, 'clip', (30,30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)
        print('clip ' + str(clip) + ' was made.')

        clipFile.release()
        clipCount += 1
        
        clip = False



    """show screen"""
    playback = videoQueue.get(frameCur % videoQueue.maxSize)
    cv2.imshow("Replay", playback)
    if two: #show only if theres 2 monitors
        cv2.imshow("Live Video", frame)


    """keybinds"""
    k = cv2.waitKey(1)
    if k == 13: #enter key, toLive
        toEnd = True
    if k == ord(' '): #start/stop
        play = not play
    if k == ord('o'): #left arrow doesnt work. jump backwards 5 seconds
        jumpBack5 = True
    if k == ord('p'): #right arrow doesnt work. jump forwards 5 seconds
        jumpForward5 = True 
    if k == ord(','): #step backwards 2 frames
        stepBack = True
    if k == ord('.'): #step forwards 2 frames
        stepFore = True
    if k == ord('c'):
        clip = True
    if k == ord('q'): #escape
            break
    

live.release()
out.release()
cv2.destroyAllWindows()