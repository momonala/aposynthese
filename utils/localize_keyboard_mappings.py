import cv2
import os
import numpy as np
import pandas as pd
from scipy.spatial import KDTree


"""
Utils script to localize the keypoints of each key in the keyboard (88). 
Use corner detection and clustering to find corners of each key, and gives 
pixel location. Can use the fact of even spacing between octaves to extrapolate 
same keys. 
"""

# get color and grayscale versions of piano
img = cv2.cvtColor(cv2.imread(os.path.join('utils', 'piano.jpg')), cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

# detect corners, isolate centroids of clusters, get corner points
dst = cv2.cornerHarris(gray, 3, 3, 0.04)
thresh = 0.02
ret, dst = cv2.threshold(dst, 0.1*dst.max(), 255, 0)
dst = np.uint8(dst)
_, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
# img[dst>thresh*dst.max()]=[255,0,255]

# map points to lie on same line
corners = corners.astype(int)[1:]
corners = np.unique(corners, axis=1)
for i, row in enumerate(corners):
    if row[1] < 12 and row[1] > 6:
        corners[i, 1] = 8
    if row[1] < 164 and row[1] > 160:
        corners[i, 1] = 162
    if row[1] < 226 and row[1] > 222:
        corners[i, 1] = 224
        
# remove close points
for i, row1 in enumerate(corners):
    for j, row2 in enumerate(corners):
        dist = np.linalg.norm(corners[i]-corners[j])
        if dist < 6 and dist != 0:
            corners[j] = np.array([0, 0])
            
# some filtering and sorting    
df = pd.DataFrame(corners, columns=['1', '0'])
df = df.sort_values(['0', '1'], ascending=[True, True])
df = df[['0', '1']]
df = df.drop_duplicates()
corners = df.values

# for quick look ups
tree = KDTree(corners)


def find_closest_corner(event, x, y):
    """Find closest corner on double click and append to global list."""
    global arr
    if event == cv2.EVENT_LBUTTONDBLCLK:
        q = tree.query(np.array([y, x]))
        loc = tree.data[q[1]]
        arr.append(loc)
        print(loc)


# to visualize
for c in corners: 
    cv2.circle(img, tuple(c[::-1]), 2, [255, 0, 0], 2)
    
# to stay on track
freqs = pd.read_csv(os.path.join('assets', 'freqs.csv'))
freqs = freqs.iloc[1:, :4]
freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.replace('′', ''))
freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.replace('͵', ''))
freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.split(' ')[0])
freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.upper())
freqs['Frequency (Hz)'] = freqs['Frequency (Hz)'].astype(np.float16)
freqs['Keynumber'] = freqs['Keynumber'].astype(np.uint8)
freqs = freqs[freqs.Keynumber <= 88]
freqs = freqs.sort_values('Keynumber', ascending=False)
freqs.index = range(1, 89)
freqs.head()

# -------------------------------------------------------------------------------
# Loop and interact with image.

cv2.namedWindow('image')
cv2.setMouseCallback('image', find_closest_corner)

i = 1
df = pd.DataFrame(columns=['1', '2', '3', '4', '5', '6', '7', '8'])
arr = list()
while 1:
    cv2.imshow('image', img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break
    elif k == ord('a'):
        df.loc[i] = arr + [0]*(df.shape[1]-len(arr))
        i += 1
        arr = list()
        print(freqs.iloc[88-i])
