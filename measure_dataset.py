import numpy as np
import glob
import os
import measure


def run_one_file(filename,method='median'):
    dirname, fname = os.path.split(filename)

    # Chop off the file extension, split the name into important parts
    i,_,x1,y1,x2,y2,real = fname.split('.')[0].split('_')

    # Parse them as ints
    i,x1,y1,x2,y2,real = map(int, (i,x1,y1,x2,y2,real))

    # Read the depth image
    with open(os.path.join(dirname, '%d_depth.bin' % i),'rb') as f:
        depth = np.fromfile(f, dtype='i2').reshape(480,640)

    # Measure the distance, compare to known distance
    dist = measure.estimate_distance(depth, (x1,y1), (x2,y2), method)

    return dist, real/1000.0


def run_all_files():
    # Load the test data
    # Run a file for all the files in here
    filenames = glob.glob('data/*/*_calib_*.png')

    for filename in filenames:
        dist,real = run_one_file(filename)

        print('[%03.0fmm]/[%03dmm] (est/actual) %s' %
          (dist*1000,real,filename))


def results():
    filenames = glob.glob('data/*/*_calib_*.png')

    import pylab
    global dists, reals, err
    pylab.figure(1)
    pylab.clf()

    methods = ['mean','median','min']
    for i, method in zip(range(len(methods)),methods):
        r = [run_one_file(filename, method) for filename in filenames]
        dists, reals = np.array(r).transpose()
        err = (dists-reals)/reals
        pylab.subplot(len(methods),1,i+1)
        pylab.hist(err.clip(-.2,0.3),bins=30, alpha=0.6, label=method)
        pylab.xlim([-.2,0.3])
        pylab.legend()

    pylab.subplot(len(methods),1,1)
    pylab.title('Error distributions of clickmeasure methods')
    pylab.subplot(len(methods),1,3)
    pylab.xlabel('percent error (est-real)/(real)')
    pylab.subplot(len(methods),1,2)
    pylab.ylabel('frequency')

if __name__ == '__main__':
    run_all_files()
