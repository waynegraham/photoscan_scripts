#adds custom menu item
#allows to split the original chunk into multiple chunks with smaller bounding boxes forming a grid
#building dense cloud, mesh and merging the result back is optional

import PhotoScan
from PySide import QtGui, QtCore

class SplitDlg(QtGui.QDialog):

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Split in chunks")

        self.gridX = 2
        self.gridY = 2
        self.gridWidth = 198
        self.gridHeight = 198

        self.spinX = QtGui.QSpinBox()
        self.spinX.setMinimum(2)
        self.spinX.setMaximum(20)
        self.spinX.setFixedSize(75, 25)
        self.spinY = QtGui.QSpinBox()
        self.spinY.setMinimum(2)
        self.spinY.setMaximum(20)
        self.spinY.setFixedSize(75, 25)

        self.chkMesh = QtGui.QCheckBox("Build Mesh")
        self.chkMesh.setFixedSize(130,50)
        self.chkMesh.setToolTip("Generates mesh for each cell in grid")

        self.chkDense = QtGui.QCheckBox("Build Dense Cloud")
        self.chkDense.setFixedSize(130,50)
        self.chkDense.setWhatsThis("Builds dense cloud for each cell in grid")

        self.chkMerge = QtGui.QCheckBox("Merge Back")
        self.chkMerge.setFixedSize(90,50)
        self.chkMerge.setToolTip("Merges back the processing products formed in the individual cells")

        self.btnQuit = QtGui.QPushButton("Quit")
        self.btnQuit.setFixedSize(90,50)

        self.btnP1 = QtGui.QPushButton("Split")
        self.btnP1.setFixedSize(90,50)

        self.grid = QtGui.QLabel(" ")
        self.grid.resize(self.gridWidth, self.gridHeight)
        tempPixmap = QtGui.QPixmap(self.gridWidth, self.gridHeight)
        tempImage = tempPixmap.toImage()

        for y in range(self.gridHeight):
            for x in range(self.gridWidth):

                if not (x and y) or (x == self.gridWidth - 1) or (y == self.gridHeight - 1):
                    tempImage.setPixel(x, y, QtGui.qRgb(0, 0, 0))
                elif (x == self.gridWidth / 2) or (y == self.gridHeight / 2):
                    tempImage.setPixel(x, y, QtGui.qRgb(0, 0, 0))

                else:
                    tempImage.setPixel(x, y, QtGui.qRgb(255, 255, 255))

        tempPixmap = tempPixmap.fromImage(tempImage)
        self.grid.setPixmap(tempPixmap)
        self.grid.show()

        layout = QtGui.QGridLayout()   #creating layout
        layout.addWidget(self.spinX, 0, 0)
        layout.addWidget(self.spinY, 0, 1)

        layout.addWidget(self.chkDense, 0, 2)
        layout.addWidget(self.chkMesh, 0, 3)
        layout.addWidget(self.chkMerge, 0, 4)

        layout.addWidget(self.btnP1, 2, 2)
        layout.addWidget(self.btnQuit, 2, 3)
        layout.addWidget(self.grid, 1, 0, 2, 2)
        self.setLayout(layout)

        proc_split = lambda : self.splitChunks()

        self.spinX.valueChanged.connect(self.updateGrid)
        self.spinY.valueChanged.connect(self.updateGrid)

        QtCore.QObject.connect(self.btnP1, QtCore.SIGNAL("clicked()"), proc_split)
        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))

        self.exec()

    def updateGrid(self):
        """
        Draw new grid
        """

        self.gridX = self.spinX.value()
        self.gridY = self.spinY.value()

        tempPixmap = QtGui.QPixmap(self.gridWidth, self.gridHeight)
        tempImage = tempPixmap.toImage()
        tempImage.fill(QtGui.qRgb(240, 240, 240))

        for y in range(int(self.gridHeight / self.gridY) * self.gridY):
            for x in range(int(self.gridWidth / self.gridX) * self.gridX):
                if not (x and y) or (x == self.gridWidth - 1) or (y == self.gridHeight - 1):
                    tempImage.setPixel(x, y, QtGui.qRgb(0, 0, 0))
                elif y > int(self.gridHeight / self.gridY) * self.gridY:
                    tempImage.setPixel(x, y, QtGui.qRgb(240, 240, 240))
                elif x > int(self.gridWidth / self.gridX) * self.gridX:
                    tempImage.setPixel(x, y, QtGui.qRgb(240, 240, 240))
                else:
                    tempImage.setPixel(x, y, QtGui.qRgb(255, 255, 255))

        for y in range(0, int(self.gridHeight / self.gridY + 1) * self.gridY, int(self.gridHeight / self.gridY)):
            for x in range(int(self.gridWidth / self.gridX) * self.gridX):
                tempImage.setPixel(x, y, QtGui.qRgb(0, 0, 0))

        for x in range(0, int(self.gridWidth / self.gridX + 1) * self.gridX, int(self.gridWidth / self.gridX)):
            for y in range(int(self.gridHeight / self.gridY) * self.gridY):
                tempImage.setPixel(x, y, QtGui.qRgb(0, 0, 0))

        tempPixmap = tempPixmap.fromImage(tempImage)
        self.grid.setPixmap(tempPixmap)
        self.grid.show()

        return True

    def splitChunks(self):

        self.gridX = self.spinX.value()
        self.gridY = self.spinY.value()
        partsX = self.gridX
        partsY = self.gridY

        print("Script started")

        buildMesh = self.chkMesh.isChecked()
        buildDense = self.chkDense.isChecked()
        mergeBack = self.chkMerge.isChecked()

        doc = PhotoScan.app.document
        chunk = doc.chunk

        region = chunk.region
        r_center = region.center
        r_rotate = region.rot
        r_size = region.size

        x_scale = r_size.x / partsX
        y_scale = r_size.y / partsY
        z_scale = r_size.z

        offset = r_center - r_rotate * r_size /2.

        for j in range(1, partsY + 1):  #creating new chunks and adjusting bounding box
            for i in range(1, partsX + 1):
                new_chunk = chunk.copy()
                new_chunk.label = "Chunk "+ str(i)+ "\\" + str(j)
                new_chunk.model = None
                doc.addChunk(new_chunk)

                new_region = PhotoScan.Region()
                new_rot = r_rotate
                new_center = PhotoScan.Vector([(i - 0.5) * x_scale, (j - 0.5) * y_scale, 0.5 * z_scale])
                new_center = offset + new_rot * new_center
                new_size = PhotoScan.Vector([x_scale, y_scale, z_scale])
                new_region.size = new_size
                new_region.center = new_center
                new_region.rot = new_rot

                new_chunk.region = new_region

                PhotoScan.app.update()

                if buildDense:
                    new_chunk.buildDenseCloud(quality = PhotoScan.Quality.MediumQuality, filter = PhotoScan.FilterMode.AggressiveFiltering)

                if buildMesh:
                    if new_chunk.dense_cloud:
                        new_chunk.buildModel(surface = PhotoScan.SurfaceType.HeightField, source = PhotoScan.PointsSource.DensePoints, interpolation = PhotoScan.Interpolation.EnabledInterpolation, face_count = PhotoScan.FaceCount.HighFaceCount)
                    else:
                        new_chunk.buildModel(surface = PhotoScan.SurfaceType.HeightField, source = PhotoScan.PointsSource.SparsePoints, interpolation = PhotoScan.Interpolation.EnabledInterpolation, face_count = PhotoScan.FaceCount.HighFaceCount)

                new_chunk.depth_maps = None

        if mergeBack:
            for i in range(1, len(doc.chunks)):
                chunk = doc.chunks[i]
                chunk.remove(chunk.cameras)
            doc.chunks[0].model = None #removing model from original chunk, just for case
            doc.mergeChunks(doc.chunks, merge_dense_clouds = True, merge_models = True, merge_markers = True) #merging all smaller chunks into single one
            doc.remove(doc.chunks[1:-1]) #removing smaller chunks.

        print("Script finished")
        return True


def main():

    global doc
    doc = PhotoScan.app.document

    app = QtGui.QApplication.instance()
    parent = app.activeWindow()

    dlg = SplitDlg(parent)


PhotoScan.app.addMenuItem("Custom/Split in chunks", main)
