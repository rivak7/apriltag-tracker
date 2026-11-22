"""
Calibrates the camera using the images in calibration_images/

Script adapted from
https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html.
"""

import numpy as np
import cv2 as cv
import glob

CALIBRATION_FILE = "calibration.txt"

def locate_chessboard_corners():
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob('calibration_images/*.jpg')
    if len(images) == 0:
        raise FileNotFoundError("missing calibration images")

    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (7,6), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            cv.drawChessboardCorners(img, (7,6), corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(500)

    cv.destroyAllWindows()

    if len(objpoints) == 0:
        raise RuntimeError("chessboard not found in any calibration image")

    return objpoints, imgpoints, gray.shape[::-1]

def save_calibration(path, mtx, dist, image_size, rms, num_images):
    """Save the calibration values in calibration.txt"""
    k1, k2, p1, p2, k3 = dist.ravel()
    values = [
        ("image_width", image_size[0]),
        ("image_height", image_size[1]),
        ("fx", mtx[0, 0]),
        ("fy", mtx[1, 1]),
        ("cx", mtx[0, 2]),
        ("cy", mtx[1, 2]),
        ("k1", k1),
        ("k2", k2),
        ("p1", p1),
        ("p2", p2),
        ("k3", k3),
        ("reprojection_error_px", rms),
        ("num_images", num_images),
    ]
    with open(path, "w") as file:
        for name, value in values:
            file.write(f"{name} {value}\n")

if __name__ == "__main__":
    objpoints, imgpoints, image_size = locate_chessboard_corners()
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
        objpoints, imgpoints, image_size, None, None
    )

    # ret is the RMS reprojection error in pixels
    print(f"Images used: {len(objpoints)}")
    print(f"Image size: {image_size[0]}x{image_size[1]}")
    print(f"fx = {mtx[0, 0]:.2f}")
    print(f"fy = {mtx[1, 1]:.2f}")
    print(f"cx = {mtx[0, 2]:.2f}")
    print(f"cy = {mtx[1, 2]:.2f}")
    print(
        f"Distortion (k1, k2, p1, p2, k3): {np.round(dist.ravel(), 4).tolist()}"
    )
    print(f"Reprojection error: {ret:.3f} px")

    save_calibration(CALIBRATION_FILE, mtx, dist, image_size, ret, len(objpoints))
    print(f"Saved calibration to {CALIBRATION_FILE}")
