import cv
import freenect
import numpy as np
import pylab
import sys

depth = None
rgb = None
clickpts = []


def xyz_matrix():
    fx = 583.0
    fy = 583.0
    cx = 321
    cy = 249
    a = -0.0028300396
    b = 3.1006268
    mat = np.array([[1/fx, 0, 0, -cx/fx],
                  [0, -1/fy, 0, cy/fy],
                  [0, 0, 0, -1],
                  [0, 0, a, b]])
    return mat
xyz_matrix = xyz_matrix().astype('f')


def show_depth(depth=depth):
    """Although opencv supports numpy directly,
    i.e. cv.ShowImage('depth',depth), it leaks memory. This is a workaround
    """
    im = cv.CreateImage((640,480),32,1)
    cv.SetData(im, (depth.astype('f')%256 / 256.).tostring())
    cv.ShowImage('depth',im)


def estimate_measurement():
    """Get the average depth in the area around the clicks
    """
    def pt(x,y):
        d = depth[y-10:y+10,x-10:x+10]
        meand = d[d<2047].max()
        return x,y,meand,1
    pt1 = pt(*clickpts[0])
    pt2 = pt(*clickpts[1])
    pt1 = np.dot(xyz_matrix, pt1); pt1 = pt1[:3]/pt1[3]
    pt2 = np.dot(xyz_matrix, pt2); pt2 = pt2[:3]/pt2[3]
    diff = pt1-pt2
    print "Distance from camera (m): ", -pt1[2]
    print "Distance between points (m): ", np.sqrt(np.dot(diff,diff))


def on_click(event, x, y, flags, param):
    if not event == cv.CV_EVENT_LBUTTONDOWN: return
    global clickpts
    if len(clickpts) < 2:
        clickpts.append((x,y))
    if len(clickpts) == 2:
        estimate_measurement()
        clickpts = []
    sys.stdout.flush()
cv.NamedWindow('depth',0)
cv.SetMouseCallback('depth', on_click)


def go():
    """Run in a loop.
    """
    while 1: advance()


def advance():
    """Grab a frame, show the image, wait for a bit to pump events
    """
    global depth, rgb
    (depth,_),(rgb,_) = freenect.sync_get_depth(), freenect.sync_get_video()
    show_depth(depth)
    #pylab.waitforbuttonpress(0.01)
    cv.WaitKey(10)


if __name__ == '__main__':
    pass
    go()
