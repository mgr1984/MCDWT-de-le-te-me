#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standar and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import cv2
import numpy as np
import pywt
import math
import sys
if __debug__:
    import time

sys.path.insert(0, "..")
from src.IO import image
from src.IO import pyramid

class DWT:

    def forward(self, image):
        '''2D 1-iteration forward DWT of a color image.

        Input:
        -----

            image: an array[y, x, component] with a color image.

                  x
             +---------------+
             |               |-+ component
           y |               | |-+
             |               | | |
             |               | | |
             |               | | |
             |               | | |
             |               | | |
             +---------------+ | |
               +---------------+ |
                 +---------------+


        Output:
        ------

            pyramid: a tuple (L, H), where L  (low-frequencies subband) is an array[y, x, component], and H (high-frequencies subbands) is a tuple (LH, HL, HH), where LH, HL, HH are array[y, x, component], with the color pyramid.

                 x
             +-------+-------+
             |       |       |-+ component
           y |  LL   |  HL   | |-+
             |       |       | | |
             +-------+-------+ | |
             |       |       |-+ |
             |  LH   |  HH   | |-+
             |       |       | | |
             +-------+-------+ | |
               +-------+-------+ |
                 +-------+-------+
        '''

        if __debug__:
            cv2.imshow("image", image)
            while cv2.waitKey(1) & 0xFF != ord('q'):
                time.sleep(0.1)
       
        y = math.ceil(image.shape[0]/2)
        x = math.ceil(image.shape[1]/2)
        LL = np.ndarray((y, x, 3), np.float64)
        LH = np.ndarray((y, x, 3), np.float64)
        HL = np.ndarray((y, x, 3), np.float64)
        HH = np.ndarray((y, x, 3), np.float64)
        if __debug__:
            print("image: max={} min={}".format(np.amax(image), np.amin(image)))
        for c in range(3):
            LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(image[:,:,c], 'db5', mode='per')
        if __debug__:
            print("LL: max={} min={}".format(np.amax(LL), np.amin(LL)))
            print("LH: max={} min={}".format(np.amax(LH), np.amin(LH)))
            print("HL: max={} min={}".format(np.amax(HL), np.amin(HL)))
            print("HH: max={} min={}".format(np.amax(HH), np.amin(HH)))
            cv2.imshow("LL", LL/256)
            cv2.imshow("LH", LH/16)
            cv2.imshow("HL", HL/16)
            cv2.imshow("HH", HH/16)
            while cv2.waitKey(1) & 0xFF != ord('q'):
                time.sleep(0.1)

        pyramid = (LL, (LH, HL, HH))
        return pyramid

    #def backward(I = "/tmp/p000.png", i = "/tmp/i000.png"):
    def backward(self, pyramid):
        '''2D 1-iteration inverse DWT of a color pyramid.

        Input:
        -----

            pyramid: the input pyramid (see forward transform).

        Output:
        ------

            image: the inversely transformed image (see forward transform).
        '''

        LL = pyramid[0]
        LH = pyramid[1][0]
        HL = pyramid[1][1]
        HH = pyramid[1][2]
        if __debug__:
            cv2.imshow("LL pyramid", LL/256)
            cv2.imshow("LH pyramid", LH/16)
            cv2.imshow("HL pyramid", HL/16)
            cv2.imshow("HH pyramid", HH/16)
            while cv2.waitKey(1) & 0xFF != ord('q'):
                time.sleep(0.1)
        image = np.ndarray((LL.shape[0]*2, LL.shape[1]*2, 3), np.float64)
        for c in range(3):
            image[:,:,c] = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), 'db5', mode='per')
        if __debug__:
#            for y in range(50):
#                for x in range(50):
#                    print(image[y+50,x+50,0], end=' ')
            cv2.imshow("image pyramid", image/256)
            while cv2.waitKey(1) & 0xFF != ord('q'):
                time.sleep(0.1)
        return image

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  rm -rf /tmp/stockholm/\n"
        "  mkdir /tmp/stockholm\n"
        "  cp ../sequences/stockholm/000 /tmp/stockholm/\n"
        "  ./DWT.py    -i /tmp/stockholm/000 -p /tmp/stockholm_000 # Forward transform\n"
        "  rm /tmp/stockholm/000                                   # Not really necessary\n"
        "  ./DWT.py -b -p /tmp/stockholm_000 -i /tmp/stockholm/000 # Backward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true',
                        help="Performs backward transform")

    parser.add_argument("-i", "--image",
                        help="Image to be transformed", default="/tmp/stockholm/000")

    parser.add_argument("-p", "--pyramid",
                        help="Pyramid to be transformed", default="/tmp/stockholm_000")

    args = parser.parse_args()

    d = DWT()
    if args.backward:
        if __debug__:
            print("Backward transform")
        p = pyramid.read("{}".format(args.pyramid))
        i = d.backward(p)
        np.clip(i, 0, 255)
        image.write8(i, "{}".format(args.image))
    else:
        if __debug__:
            print("Forward transform")
        i = image.read("{}".format(args.image))
        #for y in range(50):
        #    for x in range(50):
        #        print(i[y+50,x+50,0], end=' ')
        p = d.forward(i)
        pyramid.write(p, "{}".format(args.pyramid))
