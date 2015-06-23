#resizes all bounding boxes to Active chunk bounding box

#creates Custom Menu item.
#can be put to the autostart script folder


#compatibility PhotoScan Pro 1.1.0

import PhotoScan

def main():

    doc = PhotoScan.app.document

    chunk = doc.chunk
    T0 = chunk.transform.matrix

    region = chunk.region
    R0 = region.rot
    C0 = region.center
    s0 = region.size

    for chunk in doc.chunks:

        if chunk == doc.chunk:
            continue

        T = chunk.transform.matrix.inv() * T0

        R = PhotoScan.Matrix( [[T[0,0],T[0,1],T[0,2]], [T[1,0],T[1,1],T[1,2]], [T[2,0],T[2,1],T[2,2]]])

        scale = R.row(0).norm()
        R = R * (1/scale)

        region.rot = R * R0
        c = T.mulp(C0)
        region.center = c
        region.size = s0 * scale / 1.

        chunk.region = region

    print("Script finished. Bounding box copied.\n")

PhotoScan.app.addMenuItem("Custom menu/Copy bounding box", main)
