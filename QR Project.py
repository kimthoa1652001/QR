import cv2
import numpy as np
from pyzbar.pyzbar import decode
# READING DATA
def solvedata(data):
    id = data.find('|')
    cmnd = data[:id]

    data = data[id + 1:]
    id = data.find('|')
    name = data[:id]

    data = data[id + 1:]
    id = data.find('|')
    so_mui = data[:id]

    #gioitinh = data[id + 1:]
    return cmnd, name, so_mui

# DETECT QR CODE
def detectQRcode(image):
    # convert the color image to gray scale image
    Gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # create QR code object
    objectQRcode = decode(Gray)

    if objectQRcode == []:
        return None,None,None,None

    for obDecoded in objectQRcode:
        x, y, w, h = obDecoded.rect
        points = obDecoded.polygon
        data = obDecoded.data.decode('utf-8')
        pts = np.array([obDecoded.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (20,20,20), 3)
        return points,data,x,y

# SORT
def Sort(points):
    p1,p2,p3,p4 = points
    if p1[1] > p3[1]:
        return p4,p1,p2,p3
    else:
        return p1,p2,p3,p4

# PUT TEXT WITH BOUNDING BOX
def textBGoutline(img, text, position, fonts=cv2.FONT_HERSHEY_TRIPLEX, scaling=1, text_color=(0, 0, 0), thickness=1,
                  bg_color=(16,226,244)):
    #img_h, img_w = img.shape[:2]
    x, y = position
    (w, h), p = cv2.getTextSize(text, fonts, scaling, thickness)

    cv2.rectangle(img, (x - p, y + p), (x + w + p, y - h - p), bg_color, -1)
    cv2.rectangle(img, (x - p, y + p), (x + w + p, y - h - p), text_color, thickness, cv2.LINE_AA)

    cv2.putText(img, text, position, fonts, scaling, text_color, thickness, cv2.LINE_AA)

#  GET GIF WITH ITS COLORS
def green_tick():
    myGif = cv2.VideoCapture('1.mp4')
    pts   = np.float32([[0,400],[400,400],[0,0],[400,0]]).reshape(-1,1,2)
    return pts,myGif
def red_tick():
    myGif = cv2.VideoCapture('2.mp4')
    pts   = np.float32([[0, 600], [600, 600], [0, 0], [600, 0]]).reshape(-1, 1, 2)
    return pts, myGif
def yellow_tick():
    myGif = cv2.VideoCapture('3.mp4')
    pts   = np.float32([[0, 450], [450, 450], [0, 0], [450, 0]]).reshape(-1, 1, 2)
    return pts, myGif

# SHOW GIF AND DATA
def show_gif(points,imgWebcam,myImage, pts1,myData,flag,x,y, somui):
    p1,p2,p3,p4 = Sort(points)
    pts2 = np.float32([[p2[0], p2[1]], [p3[0], p3[1]], [p1[0], p1[1]], [p4[0], p4[1]]]).reshape(-1, 1, 2)
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWrap = cv2.warpPerspective(myImage, matrix, (imgWebcam.shape[1], imgWebcam.shape[0]))

    maskNew = np.zeros((imgWebcam.shape[0], imgWebcam.shape[1]), np.uint8)
    cv2.fillPoly(maskNew, [np.int32(points)], (255, 255, 255))
    mskInv = cv2.bitwise_not(maskNew)
    imgAug = cv2.bitwise_and(imgWebcam, imgWebcam, mask=mskInv)
    #imgAug1 = cv2.bitwise_and(imgWebcam, imgWebcam, mask=mskInv)
    imgAug = cv2.bitwise_or(imgWrap, imgAug)

    if flag == 1:
        textBGoutline(imgAug, myData, (x,y), scaling=0.6, text_color=(0, 0, 0))
        textBGoutline(imgAug, f'OPTICAL FLOW', (30, 50), scaling=0.6, text_color=(9,95,254), thickness=1,
                  bg_color=(0,0,0))
        p3 = p3.astype(int)
    else:
        textBGoutline(imgAug, myData, (x, y), scaling=0.6, text_color=(0, 0, 0))
        textBGoutline(imgAug, f' PYZBAR', (30, 50), scaling=0.6, text_color=(4,252,0), thickness=1,
                  bg_color=(0,0,0))
    cv2.circle(imgAug, (p3[0], p3[1]), 20, (0, 0, 0), cv2.FILLED)
    cv2.putText(imgAug,somui, (p3[0]-10, p3[1]+10), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
    return imgAug

cap = cv2.VideoCapture('thu.mp4')
#take first frame
success, old_frame = cap.read()
#convert to gray
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
# Set params
lk_params = dict(winSize=(50, 50),
                 maxLevel=4,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.01))

frame_counter = 0
old_points = np.array([[]])
cap = cv2.VideoCapture('thu.mp4')
qr_detected = False
old_data = ''
print(" Welcome to my Project <3 ")

while True:
    success, frame = cap.read()
    if not success:
        break
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = frame.copy()
    ok = False
    # DETECT PYZBAR
    points, data, x, y = detectQRcode(frame)

    if data == old_data:
        ok = True
    stop_code = False
    if points is not None:
        if ok == False:
            cmnd, name, so_mui = solvedata(data)
            myData = "Name: " + str((name.upper())) + " / CMND: " + str(cmnd)
            if so_mui == '':
                print(" Error!", so_mui)
                break
            if int(so_mui) == 0:
                pts1, mygif = red_tick()
            if int(so_mui) == 1:
                pts1, mygif = yellow_tick()
            if int(so_mui) > 1:
                pts1, mygif = green_tick()
            success, myImage = mygif.read()

        stop_code = True
        qr_detected = True
        p1, p2, p3, p4 = [item for item in points]
        old_points = np.array([p1,p2,p3,p4], dtype=np.float32)
        old_x, old_y = x,y
        old_data = data

        if ok == True:
            success, myImage = mygif.read()
            frame_counter += 1

        if frame_counter == mygif.get(cv2.CAP_PROP_FRAME_COUNT):
            mygif.set(cv2.CAP_PROP_POS_FRAMES,0)
            frame_counter = 0
            success, myImage = mygif.read()

        pts = np.array([points], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 0, 0), 3)
        frame = show_gif(points,frame,myImage,pts1,myData,0,x,y, so_mui)
    # OPTICAL FLOW
    if qr_detected and stop_code == False:
        # calculate optical flow with available function
        new_points, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, old_points, None, **lk_params)
        old_points = new_points

        pts = new_points.astype(int)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 0, 0), 3)
        frame = show_gif(new_points,frame,myImage,pts1,myData,1,old_x,old_y, so_mui)

    old_gray = frame_gray.copy()
    key = cv2.waitKey(1)

    if key == ord("q"):
        break
    cv2.imshow('Result ',frame)
cv2.destroyAllWindows()
cap.release()
