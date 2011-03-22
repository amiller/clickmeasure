import cv
import freenect
import numpy as np
import pylab
import sys


depth = None
rgb = None
clickpts = []
sample_side = 10
frozen = None


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


def show_depth(depth=depth,name='depth'):
    """Although opencv supports numpy directly,
    i.e. cv.ShowImage('depth',depth), it leaks memory. This is a workaround
    """
    im = cv.CreateImage((640,480),8,3)
    cv.SetData(im, np.ascontiguousarray(np.dstack(\
        3*[(depth % 256).astype('u1')])).tostring())

    if len(clickpts)==1:
        pt1 = np.array(clickpts[0],'i4')
        cv.Rectangle(im, tuple(pt1-sample_side/2),
                     tuple(pt1+sample_side/2), (255,255,0))

    if len(clickpts)==2:
        pt1 = np.array(clickpts[0],'i4')
        pt2 = np.array(clickpts[1],'i4')
        cv.Rectangle(im, tuple(pt1-sample_side/2),
                     tuple(pt1+sample_side/2), (255,0,255))
        cv.Rectangle(im, tuple(pt2-sample_side/2),
                     tuple(pt2+sample_side/2), (255,0,255))
        cv.Line(im, tuple(pt1),tuple(pt2), (255,0,255))

        dist = estimate_measurement()
        cv.PutText(im, '%.3f meters' % dist,
                   tuple(np.minimum(pt1,pt2)-(10,10)),
                   cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.7, 0.7),
                   (255,255,255))

    cv.ShowImage(name,im)


def estimate_measurement():
    """Get the average depth in the area around the clicks
    """
    def pt(x,y):
        t = sample_side
        d = depth[y-t:y+t,x-t:x+t]
        meand = d[d<2047].max()
        return x,y,meand,1
    try:
        pt1 = pt(*clickpts[0])
        pt2 = pt(*clickpts[1])
    except:
        return np.inf
    pt1 = np.dot(xyz_matrix, pt1); pt1 = pt1[:3]/pt1[3]
    pt2 = np.dot(xyz_matrix, pt2); pt2 = pt2[:3]/pt2[3]
    diff = pt1-pt2
    return np.sqrt(np.dot(diff,diff))
    #print "Distance from camera (m): ", -pt1[2]
    #print "Distance between points (m): ", np.sqrt(np.dot(diff,diff))


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
