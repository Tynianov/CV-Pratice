import cv2
import numpy

from skimage.morphology import skeletonize, thin
from scipy import ndimage
from scipy import signal


def normalise(img, mean, std):
    normed = (img - numpy.mean(img)) / (numpy.std(img))
    return normed


import math
import scipy.ndimage


# import cv2
def frequest(im, orientim, windsze, minWaveLength, maxWaveLength):
    rows, cols = numpy.shape(im)

    # Find mean orientation within the block. This is done by averaging the
    # sines and cosines of the doubled angles before reconstructing the
    # angle again.  This avoids wraparound problems at the origin.

    cosorient = numpy.mean(numpy.cos(2 * orientim))
    sinorient = numpy.mean(numpy.sin(2 * orientim))
    orient = math.atan2(sinorient, cosorient) / 2

    # Rotate the image block so that the ridges are vertical

    # ROT_mat = cv2.getRotationMatrix2D((cols/2,rows/2),orient/numpy.pi*180 + 90,1)
    # rotim = cv2.warpAffine(im,ROT_mat,(cols,rows))
    rotim = scipy.ndimage.rotate(
        im,
        orient / numpy.pi * 180 + 90,
        axes=(1, 0),
        reshape=False,
        order=3,
        mode="nearest",
    )

    # Now crop the image so that the rotated image does not contain any
    # invalid regions.  This prevents the projection down the columns
    # from being mucked up.

    cropsze = int(numpy.fix(rows / numpy.sqrt(2)))
    offset = int(numpy.fix((rows - cropsze) / 2))
    rotim = rotim[offset : offset + cropsze][:, offset : offset + cropsze]

    # Sum down the columns to get a projection of the grey values down
    # the ridges.

    proj = numpy.sum(rotim, axis=0)
    dilation = scipy.ndimage.grey_dilation(proj, windsze, structure=numpy.ones(windsze))

    temp = numpy.abs(dilation - proj)

    peak_thresh = 2

    maxpts = (temp < peak_thresh) & (proj > numpy.mean(proj))
    maxind = numpy.where(maxpts)

    rows_maxind, cols_maxind = numpy.shape(maxind)

    # Determine the spatial frequency of the ridges by divinding the
    # distance between the 1st and last peaks by the (No of peaks-1). If no
    # peaks are detected, or the wavelength is outside the allowed bounds,
    # the frequency image is set to 0

    if cols_maxind < 2:
        freqim = numpy.zeros(im.shape)
    else:
        NoOfPeaks = cols_maxind
        waveLength = (maxind[0][cols_maxind - 1] - maxind[0][0]) / (NoOfPeaks - 1)
        if waveLength >= minWaveLength and waveLength <= maxWaveLength:
            freqim = 1 / numpy.double(waveLength) * numpy.ones(im.shape)
        else:
            freqim = numpy.zeros(im.shape)

    return freqim


def ridge_filter(im, orient, freq, kx, ky):
    angleInc = 3
    im = numpy.double(im)
    rows, cols = im.shape
    newim = numpy.zeros((rows, cols))

    freq_1d = numpy.reshape(freq, (1, rows * cols))
    ind = numpy.where(freq_1d > 0)

    ind = numpy.array(ind)
    ind = ind[1, :]

    # Round the array of frequencies to the nearest 0.01 to reduce the
    # number of distinct frequencies we have to deal with.

    non_zero_elems_in_freq = freq_1d[0][ind]
    non_zero_elems_in_freq = (
        numpy.double(numpy.round((non_zero_elems_in_freq * 100))) / 100
    )
    # print('<<<', non_zero_elems_in_freq)
    unfreq = numpy.unique(non_zero_elems_in_freq)

    # Generate filters corresponding to these distinct frequencies and
    # orientations in 'angleInc' increments.
    # print('>>>', unfreq)
    sigmax = 1 / unfreq[0] * kx
    sigmay = 1 / unfreq[0] * ky

    sze = numpy.round(3 * numpy.max([sigmax, sigmay]))

    x, y = numpy.meshgrid(
        numpy.linspace(-sze, sze, int(2 * sze + 1)),
        numpy.linspace(-sze, sze, int(2 * sze + 1)),
    )

    reffilter = numpy.exp(
        -(
            (
                (numpy.power(x, 2)) / (sigmax * sigmax)
                + (numpy.power(y, 2)) / (sigmay * sigmay)
            )
        )
    ) * numpy.cos(2 * numpy.pi * unfreq[0] * x)
    # this is the original gabor filter

    filt_rows, filt_cols = reffilter.shape

    gabor_filter = numpy.array(
        numpy.zeros((int(180 / angleInc), int(filt_rows), int(filt_cols)))
    )

    for o in range(0, int(180 / angleInc)):
        # Generate rotated versions of the filter.  Note orientation
        # image provides orientation *along* the ridges, hence +90
        # degrees, and imrotate requires angles +ve anticlockwise, hence
        # the minus sign.

        rot_filt = scipy.ndimage.rotate(reffilter, -(o * angleInc + 90), reshape=False)
        gabor_filter[o] = rot_filt

    # Find indices of matrix points greater than maxsze from the image
    # boundary

    maxsze = int(sze)

    temp = freq > 0
    validr, validc = numpy.where(temp)

    temp1 = validr > maxsze
    temp2 = validr < rows - maxsze
    temp3 = validc > maxsze
    temp4 = validc < cols - maxsze

    final_temp = temp1 & temp2 & temp3 & temp4

    finalind = numpy.where(final_temp)

    # Convert orientation matrix values from radians to an index value
    # that corresponds to round(degrees/angleInc)

    maxorientindex = numpy.round(180 / angleInc)
    orientindex = numpy.round(orient / numpy.pi * 180 / angleInc)

    # do the filtering

    for i in range(0, rows):
        for j in range(0, cols):
            if orientindex[i][j] < 1:
                orientindex[i][j] = orientindex[i][j] + maxorientindex
            if orientindex[i][j] > maxorientindex:
                orientindex[i][j] = orientindex[i][j] - maxorientindex
    finalind_rows, finalind_cols = numpy.shape(finalind)
    sze = int(sze)
    for k in range(0, finalind_cols):
        r = validr[finalind[0][k]]
        c = validc[finalind[0][k]]

        img_block = im[r - sze : r + sze + 1][:, c - sze : c + sze + 1]

        newim[r][c] = numpy.sum(img_block * gabor_filter[int(orientindex[r][c]) - 1])

    return newim


def ridge_segment(im, blksze, thresh):
    rows, cols = im.shape

    im = normalise(im, 0, 1)
    # normalise to get zero mean and unit standard deviation

    new_rows = numpy.int(
        blksze * numpy.ceil((numpy.float(rows)) / (numpy.float(blksze)))
    )
    new_cols = numpy.int(
        blksze * numpy.ceil((numpy.float(cols)) / (numpy.float(blksze)))
    )

    padded_img = numpy.zeros((new_rows, new_cols))
    stddevim = numpy.zeros((new_rows, new_cols))

    padded_img[0:rows][:, 0:cols] = im

    for i in range(0, new_rows, blksze):
        for j in range(0, new_cols, blksze):
            block = padded_img[i : i + blksze][:, j : j + blksze]

            stddevim[i : i + blksze][:, j : j + blksze] = numpy.std(block) * numpy.ones(
                block.shape
            )

    stddevim = stddevim[0:rows][:, 0:cols]

    mask = stddevim > thresh

    mean_val = numpy.mean(im[mask])

    std_val = numpy.std(im[mask])

    normim = (im - mean_val) / (std_val)

    return (normim, mask)


def ridge_freq(im, mask, orient, blksze, windsze, minWaveLength, maxWaveLength):
    rows, cols = im.shape
    freq = numpy.zeros((rows, cols))

    for r in range(0, rows - blksze, blksze):
        for c in range(0, cols - blksze, blksze):
            blkim = im[r : r + blksze][:, c : c + blksze]
            blkor = orient[r : r + blksze][:, c : c + blksze]

            freq[r : r + blksze][:, c : c + blksze] = frequest(
                blkim, blkor, windsze, minWaveLength, maxWaveLength
            )

    freq = freq * mask
    freq_1d = numpy.reshape(freq, (1, rows * cols))
    ind = numpy.where(freq_1d > 0)

    ind = numpy.array(ind)
    ind = ind[1, :]

    non_zero_elems_in_freq = freq_1d[0][ind]

    meanfreq = numpy.mean(non_zero_elems_in_freq)
    medianfreq = numpy.median(non_zero_elems_in_freq)
    # does not work properly
    return (freq, meanfreq)


def ridge_orient(im, gradientsigma, blocksigma, orientsmoothsigma):
    rows, cols = im.shape
    # Calculate image gradients.
    sze = numpy.fix(6 * gradientsigma)
    if numpy.remainder(sze, 2) == 0:
        sze = sze + 1

    gauss = cv2.getGaussianKernel(numpy.int(sze), gradientsigma)
    f = gauss * gauss.T

    fy, fx = numpy.gradient(f)
    # Gradient of Gaussian

    # Gx = ndimage.convolve(numpy.double(im),fx);
    # Gy = ndimage.convolve(numpy.double(im),fy);

    Gx = signal.convolve2d(im, fx, mode="same")
    Gy = signal.convolve2d(im, fy, mode="same")

    Gxx = numpy.power(Gx, 2)
    Gyy = numpy.power(Gy, 2)
    Gxy = Gx * Gy

    # Now smooth the covariance data to perform a weighted summation of the data.

    sze = numpy.fix(6 * blocksigma)

    gauss = cv2.getGaussianKernel(numpy.int(sze), blocksigma)
    f = gauss * gauss.T

    Gxx = ndimage.convolve(Gxx, f)
    Gyy = ndimage.convolve(Gyy, f)
    Gxy = 2 * ndimage.convolve(Gxy, f)

    # Analytic solution of principal direction
    denom = (
        numpy.sqrt(numpy.power(Gxy, 2) + numpy.power((Gxx - Gyy), 2))
        + numpy.finfo(float).eps
    )

    sin2theta = Gxy / denom
    # Sine and cosine of doubled angles
    cos2theta = (Gxx - Gyy) / denom

    if orientsmoothsigma:
        sze = numpy.fix(6 * orientsmoothsigma)
        if numpy.remainder(sze, 2) == 0:
            sze = sze + 1
        gauss = cv2.getGaussianKernel(numpy.int(sze), orientsmoothsigma)
        f = gauss * gauss.T
        cos2theta = ndimage.convolve(cos2theta, f)
        # Smoothed sine and cosine of
        sin2theta = ndimage.convolve(sin2theta, f)
        # doubled angles

    orientim = numpy.pi / 2 + numpy.arctan2(sin2theta, cos2theta) / 2
    return orientim


def removedot(invertThin):
    temp0 = numpy.array(invertThin[:])
    temp0 = numpy.array(temp0)
    temp1 = temp0 / 255
    temp2 = numpy.array(temp1)
    temp3 = numpy.array(temp2)

    enhanced_img = numpy.array(temp0)
    filter0 = numpy.zeros((10, 10))
    W, H = temp0.shape[:2]
    filtersize = 6

    for i in range(W - filtersize):
        for j in range(H - filtersize):
            filter0 = temp1[i : i + filtersize, j : j + filtersize]

            flag = 0
            if sum(filter0[:, 0]) == 0:
                flag += 1
            if sum(filter0[:, filtersize - 1]) == 0:
                flag += 1
            if sum(filter0[0, :]) == 0:
                flag += 1
            if sum(filter0[filtersize - 1, :]) == 0:
                flag += 1
            if flag > 3:
                temp2[i : i + filtersize, j : j + filtersize] = numpy.zeros(
                    (filtersize, filtersize)
                )

    return temp2


def image_enhance(img):
    blksze = 16
    thresh = 0.1
    normim, mask = ridge_segment(img, blksze, thresh)
    # normalise the image and find a ROI

    gradientsigma = 1
    blocksigma = 7
    orientsmoothsigma = 7
    orientim = ridge_orient(normim, gradientsigma, blocksigma, orientsmoothsigma)
    # find orientation of every pixel

    blksze = 38
    windsze = 5
    minWaveLength = 5
    maxWaveLength = 15
    freq, medfreq = ridge_freq(
        normim, mask, orientim, blksze, windsze, minWaveLength, maxWaveLength
    )
    # find the overall frequency of ridges

    freq = medfreq * mask
    kx = 0.65
    ky = 0.65
    newim = ridge_filter(normim, orientim, freq, kx, ky)
    # create gabor filter and do the actual filtering

    # th, bin_im = cv2.threshold(np.uint8(newim),0,255,cv2.THRESH_BINARY);
    return newim < -3


def get_descriptors(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = image_enhance(img)
    img = numpy.array(img, dtype=numpy.uint8)
    # Threshold
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    # Normalize to 0 and 1 range
    img[img == 255] = 1

    # Thinning
    skeleton = skeletonize(img)
    skeleton = numpy.array(skeleton, dtype=numpy.uint8)
    skeleton = removedot(skeleton)
    # Harris corners
    harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
    harris_normalized = cv2.normalize(
        harris_corners, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32FC1
    )
    threshold_harris = 125
    # Extract keypoints
    keypoints = []
    for x in range(0, harris_normalized.shape[0]):
        for y in range(0, harris_normalized.shape[1]):
            if harris_normalized[x][y] > threshold_harris:
                keypoints.append(cv2.KeyPoint(y, x, 1))
    # Define descriptor
    orb = cv2.ORB_create()
    # Compute descriptors
    _, des = orb.compute(img, keypoints)
    return des
