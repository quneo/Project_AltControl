import cv2 as cv

def get_available_cameras(max_cameras=4):
    available_cameras = []
    for i in range(max_cameras):
        try:
            cap = cv.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
            cap.release()
        except Exception as e:
            # Здесь можно игнорировать ошибку или логировать
            pass
    return available_cameras
