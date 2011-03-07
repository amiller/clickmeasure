import cv
import freenect
from matplotlib.cm import get_cmap
import numpy as np
import pylab

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


def build_depthlut():
    """Builds a pretty lookup table that maps range(2048) depth data to
    RGB range(256) data for display. I ended up not using this because
    it's too slow to be worthwhile using indexing, i.e. lut[depth] took 60ms
    """
    from scipy.interpolate import interp1d
    cm = get_cmap()
    x = np.linspace(0,2048,256)
    y = np.array([cm(i) for i in range(256)])[:,:3]
    interps = [interp1d(x,y[:,i]) for i in range(3)]
    lut = np.vstack([[interp(_) for _ in range(2048)] for interp in interps])
    lut = lut.astype('f').transpose()
    return lut
if not 'lut' in globals():
    lut = build_depthlut()


def show_depth(depth=depth):
    """Although opencv supports numpy directly,
    i.e. cv.ShowImage('depth',depth), it leaks memory. This is a workaround
    """
    im = cv.CreateImage((640,480),32,1)
    cv.SetData(im, (depth.astype('f')%256 / 256.).tostring())
    cv.ShowImage('depth',im)


def on_click(event, x, y, flags, param):
    if not event == cv.CV_EVENT_LBUTTONDOWN: return
    global clickpts
    if len(clickpts) < 2:
        clickpts.append((x,y))
    if len(clickpts) == 2:
        print "ok"
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
    #cv.WaitKey(10)
    pylab.waitforbuttonpress(0.01)
    import time
    time.sleep(0.01)


if __name__ == '__main__':
    pass
    #go()  # Uncomment this if you want to run it without ipython
