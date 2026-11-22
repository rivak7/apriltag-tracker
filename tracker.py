"""
Detects AprilTags (36h11) in the webcam feed, outlines each one, and shows
its ID and distance from the camera.

Pose estimation adapted from
https://docs.opencv.org/4.13.0/d5/dae/tutorial_aruco_detection.html.
"""

import numpy as np
import cv2 as cv

from calibrate import CALIBRATION_FILE
from camera import FRAME_HEIGHT, FRAME_WIDTH, open_camera

TAG_SIZE_MM = 100.0             # printed AprilTag is 100x100 mm
WINDOW = "AprilTag tracker"

# top left, top right, bottom right, and bottom left corners
# of the tag in its own frame ([0, 0, 0] is the center)
half = TAG_SIZE_MM / 2
TAG_CORNERS = np.array([
    [-half,  half, 0],
    [ half,  half, 0],
    [ half, -half, 0],
    [-half, -half, 0],
], dtype=np.float32) # you need it this way for solvePnP


def load_calibration(path):
    values = {}
    with open(path) as file:
        for line in file:
            name, value = line.split()
            values[name] = float(value)

    size = (int(values["image_width"]), int(values["image_height"]))
    if size != (FRAME_WIDTH, FRAME_HEIGHT):
        raise RuntimeError(
            f"Calibration is for {size[0]}x{size[1]}"
            f" but the camera is set to {FRAME_WIDTH}x{FRAME_HEIGHT}"
        )

    mtx = np.array([
        [values["fx"], 0, values["cx"]],
        [0, values["fy"], values["cy"]],
        [0, 0, 1],
    ])
    dist = np.array([values[k] for k in ("k1", "k2", "p1", "p2", "k3")])
    return mtx, dist


def make_detector():
    # I printed family tag36h11, ID 0, so we want cv to look for that family
    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_36h11)
    params = cv.aruco.DetectorParameters()
    # refines corner coords like we did using cornerSubPix for the chessboard
    # in calibrate.py
    params.cornerRefinementMethod = cv.aruco.CORNER_REFINE_SUBPIX
        # I tried CORNER_REFINE_APRILTAG but it was slow
    return cv.aruco.ArucoDetector(dictionary, params)


def main():
    mtx, dist = load_calibration(CALIBRATION_FILE)
    detector = make_detector()
    capture = open_camera()

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Lost the camera feed")
                break

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                cv.aruco.drawDetectedMarkers(frame, corners, None)

                for tag_corners, tag_id in zip(corners, ids.ravel()):
                    # rvec = rotation
                    # tvec = translation
                    found, rvec, tvec = cv.solvePnP(
                        TAG_CORNERS, tag_corners, mtx, dist,
                        flags=cv.SOLVEPNP_IPPE_SQUARE,
                    )
                    if not found:
                        continue

                    distance_cm = np.linalg.norm(tvec) / 10
                    cv.drawFrameAxes(frame, mtx, dist, rvec, tvec, half)

                    x, y = tag_corners[0][0].astype(int)  # top left
                    cv.putText(frame, f"ID {tag_id}: {distance_cm:.1f} cm",
                               (x, y - 15), cv.FONT_HERSHEY_SIMPLEX, 1,
                               (0, 255, 255), 3)

            cv.imshow(WINDOW, frame)
            cv.waitKey(1)
    finally:
        capture.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
