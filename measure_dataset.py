import numpy as np
import glob
import os
import measure


def run_one_file(filename):
    dirname, fname = os.path.split(filename)

    # Chop off the file extension, split the name into important parts
    i,_,x1,y1,x2,y2,real = fname.split('.')[0].split('_')

    # Parse them as ints
    i,x1,y1,x2,y2,real = map(int, (i,x1,y1,x2,y2,real))

    # Read the depth image
    with open(os.path.join(dirname, '%d_depth.bin' % i),'rb') as f:
        depth = np.fromfile(f, dtype='i2').reshape(480,640)

    # Measure the distance, compare to known distance
    dist = measure.estimate_distance(depth, (x1,y1), (x2,y2))

    print('[%03.0fmm]/[%03dmm] (est/actual) %s' %
          (dist*1000,real,filename))


def run_all_files():
    # Load the test data
    # Run a file for all the files in here
    filenames = glob.glob('data/*/*_calib_*.png')
    for filename in filenames:
        run_one_file(filename)


if __name__ == '__main__':
    run_all_files()
