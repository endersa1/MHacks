import time

import cv2
import dlib
import pyautogui
import csv
import beepy

pyautogui.FAILSAFE = False

# Open a CSV file for writing eye gaze coordinates
# csv_file = open('eye_gaze_coordinates.csv', 'w', newline='')
# csv_writer = csv.writer(csv_file)
# csv_writer.writerow(['Timestamp', 'Normalized X', 'Normalized Y', 'On Screen', 'Awake', 'Blinking', 'Blinks', 'Score'])

def get_bounding_box(landmarks):
    # Find min and max landmarks based on X coordinate, and then select the X coordinate
    min_x = min(landmarks, key=lambda p: p.x).x
    max_x = max(landmarks, key=lambda p: p.x).x
    # Find min and max landmarks based on Y coordinate, and then select the Y coordinate
    min_y = min(landmarks, key=lambda p: p.y).y
    max_y = max(landmarks, key=lambda p: p.y).y

    return min_x, max_x, min_y, max_y


def filter_for_iris(eye_image):
    # Convert to grayscale
    eye_image = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)

    # Blur frame
    eye_image = cv2.bilateralFilter(eye_image, 10, 15, 15)

    # Adjust brightness
    eye_image = cv2.equalizeHist(eye_image)

    # Find dark parts of frame
    iris_image = 255 - \
        cv2.threshold(eye_image, 50, 255, cv2.THRESH_BINARY)[1]

    return iris_image


def find_iris_location(iris_image):
    # Find contours
    contours, _ = cv2.findContours(
        iris_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort in ascending order by area
    contours = sorted(contours, key=cv2.contourArea)

    try:
        # Find center of largest contour
        moments = cv2.moments(contours[-1])
        # m[i, j] = Sum(x ^ i * y ^ j * brightness at (x, y))
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
    except (IndexError, ZeroDivisionError):
        # Assume there is no iris
        return None

    return x, y


def crop(image, bbox):
    return image[bbox[2]:bbox[3], bbox[0]:bbox[1]]


find_faces = dlib.get_frontal_face_detector()
find_landmarks = dlib.shape_predictor(
    './shape_predictor_68_face_landmarks.dat')

cap = cv2.VideoCapture(0)

top_left_average_offset = None
bottom_right_average_offset = None
last_time_i_told_the_user_to_look_somewhere = None
left_eye_width = None
left_eye_height = None
right_eye_height = None
right_eye_width = None
score = 100
blinks = []
not_on_task_count = 0

while True:
    _, frame = cap.read()

    if(len(find_faces(frame)) == 0 and top_left_average_offset is not None and bottom_right_average_offset is not None):
        print("NOT ON TASK!")
        score -= 1
        not_on_task_count += 1
        if(not_on_task_count == 10):
            beepy.beep(sound=4)
            not_on_task_count = 0
    else:
        not_on_task_count = 0

    for face_bounding_box in find_faces(frame):
        landmarks = find_landmarks(frame, face_bounding_box).parts()

        left_bbox = get_bounding_box(landmarks[36:42])
        right_bbox = get_bounding_box(landmarks[42:48])

        left_eye_frame = crop(frame, left_bbox)
        right_eye_frame = crop(frame, right_bbox)

        left_iris = filter_for_iris(left_eye_frame)
        right_iris = filter_for_iris(right_eye_frame)

        left_iris_location = find_iris_location(left_iris)
        right_iris_location = find_iris_location(right_iris)

        left_eye_center = (
            (landmarks[36].x + landmarks[39].x) // 2 -
            left_bbox[0]), ((landmarks[36].y + landmarks[39].y) // 2 - left_bbox[2])

        right_eye_center = (
            (landmarks[42].x + landmarks[45].x) // 2 -
            right_bbox[0]), ((landmarks[42].y + landmarks[45].y) // 2 - right_bbox[2])

        curr_left_eye_width = left_bbox[1] - left_bbox[0]
        curr_left_eye_height = left_bbox[3] - left_bbox[2]
        curr_right_eye_width = right_bbox[1] - right_bbox[0]
        curr_right_eye_height = right_bbox[3] - right_bbox[2]
        awake = False
        blinking = False
        onScreen = False

        left_iris_offset = None
        right_iris_offset = None

        if left_iris_location is not None:
            left_iris_offset = (
                left_iris_location[0] - left_eye_center[0], left_iris_location[1] - left_eye_center[1])

            cv2.circle(left_eye_frame, left_iris_location, 2, (0, 0, 255), -1)

        if right_iris_location is not None:
            right_iris_offset = (
                right_iris_location[0] - right_eye_center[0], right_iris_location[1] - right_eye_center[1])

            cv2.circle(right_eye_frame, right_iris_location,
                       2, (0, 0, 255), -1)

        if left_iris_offset is not None and right_iris_offset is not None:
            average_offset = (left_iris_offset[0] + right_iris_offset[0]) // 2,\
                (left_iris_offset[1] + right_iris_offset[1]) // 2

            needs_calibration = (top_left_average_offset is None) or (
                bottom_right_average_offset is None) or (left_eye_width is None) or (right_eye_width is None) or (left_eye_height is None) or (right_eye_height is None)

            if needs_calibration:
                if last_time_i_told_the_user_to_look_somewhere is None:
                    if top_left_average_offset is None:
                        print("Look at top left corner")
                    elif bottom_right_average_offset is None:
                        print("Look at bottom right corner")
                    else:
                        print("Look at center")

                    last_time_i_told_the_user_to_look_somewhere = time.time()
                elif time.time() >= last_time_i_told_the_user_to_look_somewhere + 5:
                    if top_left_average_offset is None:
                        top_left_average_offset = average_offset
                    elif bottom_right_average_offset is None:
                        bottom_right_average_offset = average_offset
                    elif left_eye_width is None:
                        # print("HERE")
                        left_eye_width = curr_left_eye_width
                        left_eye_height = curr_left_eye_height
                        right_eye_width = curr_right_eye_width
                        right_eye_height = curr_right_eye_height

                    last_time_i_told_the_user_to_look_somewhere = None
            else:
                min_x, min_y = top_left_average_offset
                max_x, max_y = bottom_right_average_offset
                # print(left_eye_width, left_eye_height, right_eye_width, right_eye_height, curr_left_eye_width, curr_left_eye_height, curr_right_eye_width, curr_right_eye_height)
                if left_eye_height is not None and right_eye_height is not None and left_eye_width is not None and right_eye_width is not None and curr_left_eye_height is not None and curr_right_eye_height is not None and curr_left_eye_width is not None and curr_right_eye_width is not None:
                    if (left_eye_height)/(left_eye_width)*0.8 > (curr_left_eye_height)/(curr_left_eye_width) and (right_eye_height)/(right_eye_width)*0.8 > (curr_right_eye_height)/(curr_right_eye_width):
                        # print("WAKE UP!")
                        if len(blinks) == 120:
                            blinks.pop(0)
                        blinks.append(1)
                    else:
                        if len(blinks) == 120:
                            blinks.pop(0)
                        blinks.append(0)
                        # print("YOU'RE AWAKE GOOD JOB!")
                    # print(blinks)
                    if(sum(blinks) > 20):
                        print("WAKE UP!")
                        awake = True
                        score -= 1
                    else:
                        print("YOU'RE AWAKE GOOD JOB!")
                        awake = False
                        # score += 1
                    if(sum(blinks) < 6):
                        print("REST YOUR EYES!")
                        blinking = True
                        score -= 1
                    else:
                        print("YOU'RE RESTED GOOD JOB!")
                        blinking = False
                        score += 1
                    normalized_x = 1920 * (average_offset[0] - min_x) / (max_x - min_x)
                    normalized_y = 1080 * (average_offset[1] - min_y) / (max_y - min_y)
                    if normalized_x < -1920 or normalized_x > 1920 or normalized_y < -1080 or normalized_y > 1080:
                        print("User is looking off-screen!")
                        score -= 1
                        onScreen = False
                    else:
                        print("User is looking at the screen!")
                        onScreen = True
                        # score += 1
                    # Write eye gaze coordinates to the CSV file
                    timestamp = time.time()
                    # csv_writer.writerow([timestamp, normalized_x, normalized_y, onScreen, awake, blinking, sum(blinks), score])

                # pyautogui.moveTo(
                #     1920 * (average_offset[0] - min_x) / (max_x - min_x), 1080 * (average_offset[1] - min_y) / (max_y - min_y))
        else:
            print("User is looking off-screen! no iris")
            score -= 1

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        csv_file.close()
        break
