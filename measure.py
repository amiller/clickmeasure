import numpy as np


def _xyz_matrix():
    """Construct a calibration matrix from known default parameters
    """
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
# Just build this matrix once and keep it in the module
xyz_matrix = _xyz_matrix().astype('f')

# This is a parameter for the width of the sampling window
sample_side = 20


def estimate_distance(depth, pt1, pt2, method='median'):
    """
    Args:
      depth: a kinect depth image, 16 bit numpy array
      pt1, pt2: points in the image that the user clicked on and wants to
          measure

    Returns:
      The distance between the two indicated points, in meters

    This implementation uses the 'average' of a sample window. A better
    version will use a local patch feature like MSER to find the important
    edge.
    """

    def pt(x,y):
        """Take the mean of a sample neighborhood, discarding
        any invalid (depth == 2047) pixels
        """
        t = sample_side
        d = depth[y-t:y+t,x-t:x+t]

        # This is where I choose which point in the sample to use. I take
        # the minimum, which is the nearest pixel. Other possibilities
        # are median, mean, etc.
        if method=='median':
            meand = np.median(d[d<2047])
        if method=='mean':
            meand = np.mean(d[d<2047])
        if method=='min':
            meand = d[d<2047].min()
        return x,y,meand,1

    # Sample neighborhood
    try:
        pt1,pt2 = pt(*pt1), pt(*pt2)
    except ValueError:
        return np.inf

    # Convert to metric coordinates
    pt1 = np.dot(xyz_matrix, pt1); pt1 = pt1[:3]/pt1[3]
    pt2 = np.dot(xyz_matrix, pt2); pt2 = pt2[:3]/pt2[3]

    # Compute the distance
    diff = pt1-pt2
    dist = np.sqrt(np.dot(diff,diff))
    return dist
