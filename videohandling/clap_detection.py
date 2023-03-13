import cv2
import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(
    '/home/amit9021/AgadoDB/raw_data/2023-02-06_google-for-startups/angle3/20230206_105853.mp4')
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    last_position = None
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        claps = 0
        if results.multi_hand_world_landmarks:
            for hand_landmarks in results.multi_hand_world_landmarks:

                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_one_x, hand_one_y = results.multi_hand_world_landmarks[0].landmark[
                    0].x, results.multi_hand_world_landmarks[0].landmark[0].y
                if len(results.multi_hand_world_landmarks) > 1:
                    hand_two_x, hand_two_y = results.multi_hand_world_landmarks[1].landmark[
                        0].x, results.multi_hand_world_landmarks[0].landmark[0].y

                    print(hand_one_x, hand_two_x, hand_one_y, hand_two_y)

                    if abs(abs(hand_one_x) - abs(hand_two_x)) <= 0.001 and abs(abs(hand_one_y) - abs(hand_two_y)) <= 0.001:
                        claps += 1
                        print(f'clap {claps}')
                # if last_position and abs(cur_position - last_position) > 0.1:
                #     print('Clap detected!')
                # last_position = cur_position
        image = cv2.resize(image, (700, 500))
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()


image = cv2.resize(image, (500, 500))
