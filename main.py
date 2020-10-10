from matplotlib import pyplot as plt
import numpy as np
import cv2


capture = cv2.VideoCapture(0)


while True:
    ret, img = capture.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(gray)
    corners = cv2.goodFeaturesToTrack(gray, 27, 0.01, 10)
    corners = np.int0(corners)

    for i in corners:
        x, y = i.ravel()
        cv2.circle(img, (x, y), 3, 255, -1)
    plt.imshow(img), plt.show()



    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break


capture.release()
cv2.destroyAllWindows()