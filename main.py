import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
import time
from math import sqrt
import win32api
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For static images:
IMAGE_FILES = []
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))

# For webcam input:
cap = cv2.VideoCapture(1)
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image_height, image_width, _ = image.shape
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # print(results)
    if results.multi_hand_landmarks != None:
      for hand_landmarks in results.multi_hand_landmarks:
        for point in mp_hands.HandLandmark:

          normalizedLandmark = hand_landmarks.landmark[point]
          pixelCoordinateLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, image_width, image_height)

          point = str(point)
          if point == 'HandLandmark.INDEX_FINGER_TIP':
            try:
              indexfingertip_x = pixelCoordinateLandmark[0]
              indexfingertip_y = pixelCoordinateLandmark[1]
              win32api.SetCursorPos((indexfingertip_x*4,indexfingertip_y*5))

            except:
              pass

          elif point=='HandLandmark.THUMB_TIP':
            try:
              thumbfingertip_x = pixelCoordinateLandmark[0]
              thumbfingertip_y = pixelCoordinateLandmark[1]
              
            except:
              pass

          try:
            Distance_x = indexfingertip_x-thumbfingertip_x
            Distance_y = indexfingertip_y-thumbfingertip_y
            Distance = sqrt(Distance_x**2 + Distance_y**2)
            # print(Distance)
            if int(Distance) < 30:
              print("Single Click")
              pyautogui.click()

          except:
            pass



    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF in (ord('q'), 27,):
      break
cap.release()
