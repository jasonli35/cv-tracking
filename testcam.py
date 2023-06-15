import cv2
cap=cv2.VideoCapture(0)
cap.set(3,640)#width
cap.set(4,480)#height
cap.set(10,100)#brightness
while True:
    success, img = cap.read()
    if success:
        print(img)#getting None
        print(success)#getting False
        cv2.imshow("video", img)
        cv2.waitKey(1)
        if 0xFF == ord('q') :
            break