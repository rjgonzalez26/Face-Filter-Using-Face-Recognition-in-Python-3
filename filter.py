#Working on python3.5.2 Ubuntu 16.04 as of Nov 26, 7:37 PM
#REQUIRES IMUTILS, CV2, and FACE_RECOGNITION MODULES

'''
INSTRUCTIONS:

Press A key to change mask
Press Q key to quit

Open your mouth to release a pop up message

TIP: Keey your head straight up for a better experience
'''

import cv2
import numpy as np
import face_recognition
from imutils.video import VideoStream
import time
import imutils

faces=[]

vs = VideoStream(src=0).start()
time.sleep(2.0)

class Face:
	def __init__(self, face_location, face_landmarks):
		self.location = face_location
		self.landmarks = face_landmarks
        
	def move(self,face_location, face_landmarks):
		self.location = face_location
		self.landmarks = face_landmarks
       
	def getPosition(self):
		print(self.location)
		return self.location[0], self.location[1], self.location[2], self.location[3]

	def getLandmark(self, part):
		if part=="eyemask":
			#t = int(0.5 * (self.landmarks['left_eye'][1][1] + self.location[0]))
			t = self.location[0]			
			r = self.location[1]
			b = self.landmarks['nose_bridge'][1][1]
			l = self.location[3]
			return t,r,b,l

	def isMouthOpen(self):
		tolerance = 0.5

		lipPart = abs(self.landmarks['top_lip'][10][1] - self.landmarks['bottom_lip'][3][1])
		lip_width = tolerance*abs(self.landmarks['top_lip'][6][0]-self.landmarks['top_lip'][0][0])

		if lipPart > lip_width:
			return True

		return False

	#def detMouthClosedState(self, part):
		
					
   
class Facemask:
	def __init__(self):
		self.masks = ['silver_mask.png','gold_mask.png','galaxy_mask.png','snow_mask.png','christmas_mask.png']
		self.curr_index = 0

	def current(self):
		return self.masks[self.curr_index]

	def next(self):
		self.curr_index = self.curr_index+1 if self.curr_index<len(self.masks)-1 else 0

#Defined as Separate Function (for it's used before instantiation of Face class)
def inCamBoundary(location, cam_width, cam_height):

	if location[0] > 0 and location[1] < cam_width and location[2] < cam_height and location[3] > 0:
		return True
	return False
 
prev_detected=0
curr_facemask = Facemask()
while True:
	cam_width = 600
	cam_height = 600

	frame = vs.read()
	frame = imutils.resize(frame, width=cam_width, height=cam_height)

	#Read Face Information
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	face_locations = face_recognition.face_locations(gray)
	face_landmarks_list = face_recognition.face_landmarks(gray)
    
	curr_detected = 0
	if face_locations!=[]:
		#Delete non full face in the array of faces
		for i in range(len(face_locations)):
			if not inCamBoundary(face_locations[i], cam_width, cam_height):
				del(face_locations[i])

		curr_detected=len(face_locations)
        
		#Detect if there are changes in the number of full faces
		for i in range(curr_detected):
			if prev_detected != curr_detected:
				faces.append(Face(face_locations[i], face_landmarks_list[i]))
				#print("New Face Detected") 
			else:
				faces[i].move(face_locations[i],face_landmarks_list[i])

		#Graphics Part
		for i in range(len(face_locations)):
			t,r,b,l = faces[i].getLandmark('eyemask')
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

			#Mouth Open Effect
			if faces[i].isMouthOpen():
				mssg = cv2.imread('message_pop.png',-1)
				mssg = cv2.resize(mssg,(200,200))
				w,h,c = mssg.shape

				#Show Popup Message
				for i in range(0,w):
					for j in range(0,h):
						if mssg[i,j][3] !=0:
							frame[i,j] = mssg[i,j]

			scale_x = 1.1
			scale_y = 1.5
			msk = cv2.imread(curr_facemask.current(),-1)
			msk = cv2.resize(msk, ( int(scale_x*(r-l)) , int(scale_y*(b-t)) ))
			w,h,c = msk.shape

			left_adjust = int(0.5*(scale_x-1)*(r-l))

			#Mask Overlay
			for i in range(0,w):
				for j in range(0,h):
					if msk[i,j][3] !=0:
						frame[t+i,l-left_adjust+j] = msk[i,j]


			
	else:
	        prev_detected=0
	        faces=[]

	prev_detected=curr_detected
	
	cv2.imshow('frame',frame)
	key = cv2.waitKey(1) & 0xFF
	if key==ord('q'):
		break
	elif key==ord('a'):
		curr_facemask.next()

cv2.destroyAllWindows()
vs.stop()

