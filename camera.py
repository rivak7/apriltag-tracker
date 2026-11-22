"""
Shared webcam settings so every script captures in the same mode, since
camera intrinsics depend on resolution.
"""

import cv2 as cv

# Use my MacBook's webcam at 1080p
CAMERA_INDEX = 0
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080


def open_camera():
    """
    Open the webcam at FRAME_WIDTH x FRAME_HEIGHT and return the VideoCapture
    """
    capture =cv.VideoCapture(CAMERA_INDEX, cv.CAP_AVFOUNDATION)
    if not capture.isOpened():
        raise RuntimeError(
            f"Could not open camera {CAMERA_INDEX}"
        )

    capture.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # The first few frames can be dark while auto-exposure settles.
    for _ in range(10):
        ok, frame = capture.read()
    if not ok:
        capture.release()
        raise RuntimeError("Camera opened but returned no frames")

    height, width = frame.shape[:2]
    if (width, height) != (FRAME_WIDTH, FRAME_HEIGHT):
        capture.release()
        raise RuntimeError(
            f"Requested {FRAME_WIDTH}x{FRAME_HEIGHT}"
            f" but camera gave {width}x{height}"
        )

    return capture
