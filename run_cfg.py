

WORKING_PATH = '/home/amit9021/AgadoDB/raw_data/2023-02-15_expo_tel-aviv/wistle'

# ponka have different kind of annotations ponka_with_error is set to true if they annotated the error
PONKA_WITH_ERORR = True
ADD_EXTRA_TIME = 0
ADD_TIME_TO_END = 0

# CUTTED_VIDEO is set to true if we send to ponka cutted videos
# this will add and subtract the sound time to the video + 0.5 sec
CUTTED_VIDEO = False

# if we want to cut the video to the ponka annotations
TO_CUT = True

# "all" or "exercise_1" or "exercise_2" or "exercise_3" or "exercise_4"
EXERCISE = "exercise_1"


SESSION_DICT = dict(
    exercise_1={"name": "squats", "correct": "correct",
                "error_1": "back", "error_2": "knees"},
    exercise_2={"name": "sumosquats", "correct": "correct",
                "error_1": "back", "error_2": "knees"},
    exercise_3={"name": "bulgariansquats", "correct": "correct",
                "error_1": "back", "error_2": "heels"},
    exercise_4={"name": "planks", "correct": "correct",
                "error_1": "hige", "error_2": "low", "error_3": "headdown"},
)
