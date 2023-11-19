import streamlit as st
import time
import cv2
import dlib
import pyautogui
import csv

def page_track():
    st.header("Productivity Tracking")
    if st.button("End Tracking", kry="one"):
        st.session_state.page = "analyze"

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
    blinks = [0 for i in range(30)]

    while True:
        _, frame = cap.read()

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
                            blinks[int(time.time()) % 30] = 0
                        else:
                            blinks[int(time.time()) % 30] = 1
                            # print("YOU'RE AWAKE GOOD JOB!")
                        print(blinks)
                        if(sum(blinks) > 20):
                            print("WAKE UP!")
                            awake = True
                        else:
                            print("YOU'RE AWAKE GOOD JOB!")
                            awake = False
                        if(sum(blinks) < 6):
                            print("REST YOUR EYES!")
                            blinking = True
                        else:
                            print("YOU'RE RESTED GOOD JOB!")
                            blinking = False
                        normalized_x = 1920 * (average_offset[0] - min_x) / (max_x - min_x)
                        normalized_y = 1080 * (average_offset[1] - min_y) / (max_y - min_y)
                        if normalized_x < 0 or normalized_x > 1920 or normalized_y < 0 or normalized_y > 1080:
                            print("User is looking off-screen!")
                            onScreen = False
                        else:
                            print("User is looking at the screen!")
                            onScreen = True
                        # Write eye gaze coordinates to the CSV file
                        timestamp = time.time()
                        csv_writer.writerow([timestamp, normalized_x, normalized_y, onScreen, awake, blinking])

                    # pyautogui.moveTo(
                    #     1920 * (average_offset[0] - min_x) / (max_x - min_x), 1080 * (average_offset[1] - min_y) / (max_y - min_y))

        cv2.imshow('frame', frame)

        if st.button("End Tracking", kry="one"):
            st.session_state.page = "analyze"
        #if cv2.waitKey(1) & 0xFF == ord('q'):
            csv_file.close()
            break

def page_analyze():
    st.header("Productivity Analytics")
    if st.button("Start Tracking"):
        st.session_state.page = "track"
    st.write(st.session_state.page)

def main():
    # Set page configuration to avoid script rerun on every interaction
    st.set_page_config(page_title="Multi-Page App", page_icon="🅰️")

    if "page" not in st.session_state:
        st.session_state.page = "analyze"
    if st.session_state.page == "track":
        page_track()
    elif st.session_state.page == "analyze":
        page_analyze()
    

if __name__ == "__main__":
    main()