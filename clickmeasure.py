import cv
import freenect
import numpy as np
import pylab
import sys
import colormap
import measure


depth = None
rgb = None
clickpts = []
frozen = None


def show_depth(depth=depth,name='depth'):
    """Although opencv supports numpy directly,
    i.e. cv.ShowImage('depth',depth), it leaks memory. This is a workaround
    """
    im = cv.CreateImage((640,480),8,3)
    cv.SetData(im, colormap.color_map(depth).tostring())

    if len(clickpts)==1:
        pt1 = np.array(clickpts[0],'i4')
        cv.Rectangle(im, tuple(pt1-measure.sample_side/2),
                     tuple(pt1+measure.sample_side/2), (255,255,0))

    if len(clickpts)==2:
        pt1 = np.array(clickpts[0],'i4')
        pt2 = np.array(clickpts[1],'i4')
        cv.Rectangle(im, tuple(pt1-measure.sample_side/2),
                     tuple(pt1+measure.sample_side/2), (255,0,255))
        cv.Rectangle(im, tuple(pt2-measure.sample_side/2),
                     tuple(pt2+measure.sample_side/2), (255,0,255))
        cv.Line(im, tuple(pt1),tuple(pt2), (255,0,255))

        dist = measure.estimate_distance(depth, *clickpts)
        cv.PutText(im, '%.3f meters' % dist,
                   tuple(np.minimum(pt1,pt2)-(10,10)),
                   cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.7, 0.7),
                   (255,255,255))

    cv.ShowImage(name,im)


def on_click(event, x, y, flags, param):
    if not event == cv.CV_EVENT_LBUTTONDOWN: return
    global clickpts
    if len(clickpts) == 2:
        clickpts = []
    clickpts.append((x,y))
    if len(clickpts) == 2:
        # Draw the snapshot
        show_depth(depth, 'snapshot')

    sys.stdout.flush()
cv.NamedWindow('depth',0)
cv.NamedWindow('snapshot',0)
cv.SetMouseCallback('depth', on_click)


def go():
    """Run in a loop.
    """
    while 1: advance()


def advance():
    """Grab a frame, show the image, wait for a bit to pump events
    """
    global depth, rgb
    global frozen
    if not frozen:
        (depth,_) = freenect.sync_get_depth()
        (rgb,_) = freenect.sync_get_video()
    show_depth(depth)
    #pylab.waitforbuttonpress(0.005)
    c = cv.WaitKey(10)
    if c == ord('f'):
        frozen = not frozen


if __name__ == '__main__':
    pass
    go()
