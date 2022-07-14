import cv2
import numpy as np
import random
from PIL import Image

img_path = "render_4"

def get_random_offset():
    return (-1 * (random.random() < 0.5)) * random.random() * 8;

# img_path = "/mnt/c/User/Petingo/Downloads/Building-Dataset-Generator/Simple-House/5/sketches/render_0.png"


image = cv2.imread(img_path + ".png")

def distort_image(image):
    distorted = np.zeros_like(image)

    # Convert image to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    
    # Use canny edge detection
    edges = cv2.Canny(gray,50,150,apertureSize=3)

    cv2.imwrite('canny.png',edges)

    # Apply HoughLinesP method to
    # to directly obtain line end points
    lines = cv2.HoughLinesP(
                edges, # Input edge image
                3, # Distance resolution in pixels
                np.pi/180, # Angle resolution in radians
                threshold=30, # Min number of votes for valid line
                minLineLength=15, # Min allowed length of line
                maxLineGap=10 # Max allowed gap between line for joining them
                )

    lines_list = []

    # Iterate over points
    for points in lines:
        # if random.random() < 0.05:
        #     continue

        # Extracted points nested in the list
        for i in range(len(points[0])):
            v = points[0][i]
            v += get_random_offset()
            if v <= 0:
                v = 0
            
            if i%2 == 0: # x
                if v > image.shape[1] - 1:
                    v = image.shape[1] - 1
            else: #y
                if v > image.shape[0] - 1:
                    v = image.shape[0] - 1

            points[0][i] = v

        x1,y1,x2,y2=points[0]
        # Draw the lines joing the points
        # On the original image
        cv2.line(distorted,(x1,y1),(x2,y2),(255,255,255),1)
        # Maintain a simples lookup list for points
        lines_list.append([(x1,y1),(x2,y2)])
        
    # distorted = cv2.dilate(distorted, np.ones((5,5), 'uint8'), iterations=2)
    # distorted = cv2.GaussianBlur(distorted, (9,9), 5)
    # distorted = cv2.erode(distorted, np.ones((9,9), 'uint8'))
    # distorted = cv2.erode(distorted, np.ones((5,5), 'uint8'))
    # distorted = cv2.erode(distorted, np.ones((3,3), 'uint8'))
    # _, distorted = cv2.threshold(distorted, 180, 255, cv2.THRESH_BINARY)
    # distorted = cv2.erode(distorted, np.ones((3,3), 'uint8'))
    # Save the result image
    cv2.imwrite('detectedLines.png',distorted)
    comb = (np.logical_or(image[:, :, 0], distorted[:,:,0]) * 255).astype('uint8')
    print(comb)
    cv2.imwrite("comb.png", comb)
    contours, hierarchy = cv2.findContours(comb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print(contours)
    distorted_mask = np.zeros((distorted.shape[0], distorted.shape[1]))
    distorted_mask = cv2.drawContours(distorted_mask, contours, -1, 255, -1)
    distorted_trans = np.zeros((distorted.shape[0], distorted.shape[1], 4))
    distorted_trans[:, :, :3] = distorted
    distorted_trans[:, :, 3] = distorted_mask
    # distorted = np.concatenate([distorted, distorted_mask], axis=2)

    return distorted_trans

cv2.imwrite(img_path + "_distort_2.png", distort_image(image))