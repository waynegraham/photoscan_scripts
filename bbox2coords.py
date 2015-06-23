#rotates chunks' bounding box in accordance of coordinate system for active chunk
#bounding box size is kept
#compatibility: Agisoft PhotoScan Professional 1.1.0

import PhotoScan
import math

doc = PhotoScan.app.document
chunk = doc.chunk

T = chunk.transform.matrix

v_t = T * PhotoScan.Vector( [0,0,0,1] )
v_t.size = 3

if chunk.crs:
    m = chunk.crs.localframe(v_t)
else:
    m = PhotoScan.Matrix().diag([1,1,1,1])

m = m * T

s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor

R = PhotoScan.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])

R = R * (1. / s)

reg = chunk.region
reg.rot = R.t()
chunk.region = reg
