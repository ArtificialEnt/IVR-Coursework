#!/usr/bin/env python3
# N

import roslib
import sys
import rospy
import cv2
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Image
from std_msgs.msg import Float64MultiArray, Float64
from cv_bridge import CvBridge, CvBridgeError


class image_converter:

  # Defines publisher and subscriber
  def __init__(self):
    # initialize the node named image_processing
    rospy.init_node('image_processing', anonymous=True)
    # initialize a publisher to send images from camera2 to a topic named image_topic2
    self.image_pub2 = rospy.Publisher("image_topic2",Image, queue_size = 1)
    # initialize a subscriber to recieve messages rom a topic named /robot/camera1/image_raw and use callback function to recieve data
    self.image_sub2 = rospy.Subscriber("/camera2/robot/image_raw",Image,callback=self.callback2)
    #self.joints_pub = rospy.Publisher("camera2/robot/joints_pos",Float64MultiArray, queue_size=10, latch=True)
    self.pos_pub = rospy.Publisher("camera2/robot/spheres_pos",Float64MultiArray, queue_size=10, latch=True)
    self.target_pub = rospy.Publisher("camera2/robot/target_pos",Float64MultiArray, queue_size=10, latch=True)
    # initialize the bridge between openCV and ROS
    self.bridge = CvBridge()

  def detect_target(self,image):
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      mask = cv2.inRange(hsv, (25, 80, 30), (35, 100, 90))
      return self.detect_chamfer(mask)
      #bgr = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
      #gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
      #circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)
      #if circles is not None:
        #return circles[0,0][0:2]
      #else:
      #  raise ValueError

  def detect_chamfer(self,image):
      return np.array([0,0])

  def detect_red(self,image):
      mask = cv2.inRange(image, (0, 0, 100), (0, 0, 255))
      kernel = np.ones((5, 5), np.uint8)
      mask = cv2.dilate(mask, kernel, iterations=3)
      M = cv2.moments(mask)
      if(M['m00'] != 0):
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
      else:
        cx = 0
        cy = 0
      return np.array([cx, cy])
 

  def detect_green(self,image):
      mask = cv2.inRange(image, (0, 100, 0), (0, 255, 0))
      kernel = np.ones((5, 5), np.uint8)
      mask = cv2.dilate(mask, kernel, iterations=3)
      M = cv2.moments(mask)
      if(M['m00'] != 0):
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
      else:
        cx = 0
        cy = 0 
      return np.array([cx, cy])


  def detect_blue(self,image):
      mask = cv2.inRange(image, (100, 0, 0), (255, 0, 0))
      kernel = np.ones((5, 5), np.uint8)
      mask = cv2.dilate(mask, kernel, iterations=3)
      M = cv2.moments(mask)
      if(M['m00'] != 0):
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
      else:
        cx = 0
        cy = 0 
      return np.array([cx, cy])

  def detect_yellow(self,image):
      mask = cv2.inRange(image, (0, 100, 100), (0, 255, 255))
      kernel = np.ones((5, 5), np.uint8)
      mask = cv2.dilate(mask, kernel, iterations=3)
      M = cv2.moments(mask)
      if(M['m00'] != 0):
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
      else:
        cx = 0
        cy = 0
      return np.array([cx, cy])


  # Calculate the conversion from pixel to meter
  def pixel2meter(self,image):
      # Obtain the centre of each coloured blob
      circle1Pos = self.detect_yellow(image)
      circle2Pos = self.detect_blue(image)
      # find the distance between two circles
      dist = np.sum((circle1Pos - circle2Pos)**2)
      return 2.5 / np.sqrt(dist)

  def detect_sphere_locations(self, image):
    a = self.pixel2meter(image)
    # Obtain the centre of each coloured blob 
    center = a * self.detect_yellow(image)
    circle1Pos = a * self.detect_blue(image) 
    circle2Pos = a * self.detect_green(image) 
    circle3Pos = a * self.detect_red(image)
    return np.array([center, circle1Pos, circle2Pos, circle3Pos])

  # Recieve data, process it, and publish
  def callback2(self,data):
    # Recieve the image
    try:
      self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)
    # Uncomment if you want to save the image
    #cv2.imwrite('image_copy.png', cv_image)
    #im2=cv2.imshow('window2', self.cv_image)
    #a = self.detect_joint_angles(self.cv_image)
    b = self.detect_sphere_locations(self.cv_image)
    c = self.detect_target(self.cv_image)
    cv2.waitKey(1)

    #self.joints = Float64MultiArray()
    self.spheres = Float64MultiArray()
    self.target = Float64MultiArray()
    #self.joints.data = a
    self.spheres.data = np.reshape(b,(8))
    self.target.data = c

    # Publish the results
    try: 
      self.image_pub2.publish(self.bridge.cv2_to_imgmsg(self.cv_image, "bgr8"))
      #self.joints_pub.publish(self.joints)
      self.pos_pub.publish(self.spheres)
      self.target_pub.publish(self.target)
    except CvBridgeError as e:
      print(e)
    rospy.sleep(1)

# call the class
def main(args):
  ic = image_converter()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

# run the code if the node is called
if __name__ == '__main__':
    main(sys.argv)


