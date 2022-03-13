This is the code I used for the triangulation video: https://www.youtube.com/watch?v=sW4CVI51jDY

I last tested this code using OpenCV 4.4.0 and Python 3.8 on Linux on March 11, 2022. All good.

**IMPORTANT:** If you are using a different version of OpenCV. The output from cv2.findContours may have changed. Go to line 557|558 (line the error will say) and change `frame3,contours,hierarchy` to `contours,hierarchy` (or the other way around).

