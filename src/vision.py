# For vision parsing
# Probably won't actually end up using this, left it for now in case I changem my mind
# 
# https://answers.opencv.org/question/94459/seperate-touching-objects/


import numpy as np
import cv2, mss, time, json, imutils

# Gets the countours of the image "hsv" by filtering out all colour not in the range from cLower to cUpper
# Also does a small amount of processing to smooth out image
def getCnts(hsv, cLower, cUpper):
	# construct a mask for the color, then perform a series of dilations and erosions to remove any small blobs left in the mask
	mask = cv2.inRange(hsv, cLower, cUpper)
	# mask = cv2.dilate(mask, None, iterations=1)
	# mask = cv2.erode(mask, None, iterations=1)

	mask = cv2.GaussianBlur(mask, (3, 3), 0)
	mask = cv2.GaussianBlur(mask, (3, 3), 0)
	# thresh = cv2.threshold(mask, 60, 255, cv2.THRESH_BINARY)[1]

	output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
	num_labels = output[0]
	# The second cell is the label matrix
	labels = output[1]
	# The third cell is the stat matrix
	stats = output[2]
	# The fourth cell is the centroid matrix
	centroids = output[3]

	cca = mask.copy()
	minarea = 800
	height, width = cca.shape

	for i in range(height):
		p = labels[i]
		for j in range(width):
			if stats[p[j], cv2.CC_STAT_AREA] < minarea:
				cca[i,j] = 0

	for i in range(num_labels):
		if stats[i, cv2.CC_STAT_AREA] >= minarea:
			left = stats[i, cv2.CC_STAT_LEFT]
			top = stats[i, cv2.CC_STAT_TOP]
			width = stats[i, cv2.CC_STAT_WIDTH]
			height = stats[i, cv2.CC_STAT_HEIGHT]
			cv2.rectangle(mask,(left, top), (width+left, height+top),(255,255,255),2)

	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	cv2.imshow("mask", mask)

	# cv2.bitwise_not(mask, mask)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	# cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cnts = imutils.grab_contours(cnts)

	return cnts

# Random helper function that removes and element array from a parent array
# If you try the normal remove method in this situation, gives an error saying you can't compare arrays
def removeArray(L,arr):
    ind = 0
    size = len(L)
    while ind != size and not np.array_equal(L[ind],arr):
        ind += 1
    if ind != size:
        L.pop(ind)
    else:
        raise ValueError('array not found in list.')

def findCards(frame, hsv, cards, cmin, cmax):
	cLower = tuple(cmin)
	cUpper = tuple(cmax)

	cnts = getCnts(hsv, cLower, cUpper)

	for i in range(len(cnts)):
		c = max(cnts, key=cv2.contourArea)

		rect = cv2.minAreaRect(c)
		box = cv2.boxPoints(rect)
		box = np.int0(box)

		if cv2.contourArea(c) > 10:
			cv2.drawContours(frame,[box],0,(0,0,255),2)

		removeArray(cnts, max(cnts, key=cv2.contourArea))

if __name__ == "__main__":

	# Config Options
	f = open("./data/config.json")
	config = json.loads(f.read())
	f.close()

	cards = []

	mon = {'top': 230, 'left': 150, 'width': 1920-150, 'height': 620}

	while True:
		time.sleep(0.2)
		frame = np.asarray(mss.mss().grab(mon))
		frame = imutils.resize(frame, width=800)
		# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		findCards(frame, hsv, cards, config['magmaMin'], config['magmaMax'])

		# show the frame to our screen
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			break
