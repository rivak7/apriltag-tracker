# apriltag-tracker
A CV project that tracks, IDs, and finds the distance to an AprilTag using my MacBook's calibrated webcam. This was made for a [UWROV](https://uwrov.org/) demo.

The tracker draws an outline around each AprilTag in the live camera feed, labels it with its ID, and shows its distance from the camera.

## What you need
- A webcam (this project uses my MacBook's built-in camera at 1920x1080)
- A printout of [`chessboard_and_apriltag.pdf`](chessboard_and_apriltag.pdf), printed at 100% ("Actual size", Fit to Page off):
  - **Page 1:** calibration chessboard, 8 x 7 squares (7 x 6 inner corners), 25 mm squares. Attach it to something flat and stiff, like cardstock or cardboard.
  - **Page 2:** AprilTag, family tag36h11, ID 0, 100 mm black square. Check that it measures 100 mm.

## Setup
Clone the repository and run:
```bash
conda env create
conda activate apriltag-tracker
```

Run all scripts from the repository root. Allow camera access for your terminal or IDE if needed.

## Camera settings
`camera.py` opens the camera for every script, so calibration and tracking always use the same settings:
- `CAMERA_INDEX = 0`
- `FRAME_WIDTH x FRAME_HEIGHT = 1920 x 1080`

Change these values if you like.

A camera's intrinsics depend on resolution. If you change any of these settings, recalibrate.

## 1. Calibrate the camera
Depending on the specific hardware you're using, you will need to calibrate your camera before you can use the tracker. Do this by:

1. **Taking photos of the chessboard.** Save 15-25 photos at 1920x1080 as `.jpg` files in `calibration_images/`. Vary the board's tilt (up to about 45°), its distance (about 30-100 cm), and its position in the frame, including the corners. Keep the board flat, fully in view, and sharp.
2. **Running the calibration:**
   ```bash
   python calibrate.py
   ```
   This finds the chessboard corners in each photo, calibrates the camera, prints the results, and saves them to `calibration.txt`.

`calibration.txt` stores one `name value` pair per line: the image size, the focal lengths and optical center (`fx`, `fy`, `cx`, `cy`), the distortion coefficients (`k1`, `k2`, `p1`, `p2`, `k3`), and the RMS reprojection error. The tracker reads this file.

## 2. Track an AprilTag
```bash
python tracker.py
```
For each tag36h11 tag in view, the tracker:
1. detects it with OpenCV's `ArucoDetector` (`DICT_APRILTAG_36h11`) and refines its corners to sub-pixel accuracy
2. estimates its pose with `cv.solvePnP` (`SOLVEPNP_IPPE_SQUARE`) on the original, not undistorted, frame, using the calibration from `calibration.txt`
3. draws the tag's outline and 3D axes, and labels it with its ID and its distance (the length of the translation vector, from the camera to the tag's center)

Press Ctrl+C in the terminal to quit.

If your printed tag isn't exactly 100 mm, set `TAG_SIZE_MM` in `tracker.py` to the size you measured. Any error in the tag size will result in the same percentage error in distance.

## Files
| File | Purpose |
|---|---|
| `camera.py` | Opens the webcam at the fixed resolution used everywhere |
| `calibrate.py` | Calibrates the camera from `calibration_images/` and writes `calibration.txt` |
| `calibration.txt` | Calibration results for my MacBook M5 Pro webcam at 1920x1080 (you can try using these defaults, but they may be inaccurate especially if using a different camera) |
| `tracker.py` | Live AprilTag detection, ID, and distance |
| `chessboard_and_apriltag.pdf` | Printable calibration chessboard and AprilTag |
| `environment.yml` | Conda environment (Python 3.12, NumPy, OpenCV) |

## References
- [OpenCV camera calibration tutorial](https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html)
- [OpenCV ArUco marker detection tutorial](https://docs.opencv.org/4.13.0/d5/dae/tutorial_aruco_detection.html)
