#Batch export of orthophotos based on individual cameras or user selected cameras
#creates custom menu item

#compatibility Agisoft PhotoScan Pro 1.1.0
#no arguments required

import os
import time
import random
import PhotoScan
from PySide import QtCore, QtGui


def intersect(p0, pn, l0, l):
    d = ((p0 - l0) * pn) / (l * pn)
    return d * l + l0


class ExportOrthoDlg(QtGui.QDialog):

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)

        self.blend_types = {"Average": PhotoScan.BlendingMode.AverageBlending, "Mosaic": PhotoScan.BlendingMode.MosaicBlending, "Min intensity": PhotoScan.BlendingMode.MinBlending, "Max Intensity": PhotoScan.BlendingMode.MaxBlending}

        self.setWindowTitle("Export individual orthophotos")

        self.btnQuit = QtGui.QPushButton("Quit")
        self.btnQuit.setFixedSize(130,50)

        self.btnP1 = QtGui.QPushButton("Export")
        self.btnP1.setFixedSize(130,50)

        self.pBar = QtGui.QProgressBar()
        self.pBar.setTextVisible(False)
        self.pBar.setFixedSize(150, 50)


        self.resTxt = QtGui.QLabel()
        self.resTxt.setText("Export resolution (m/pix):")
        self.resTxt.setFixedSize(130, 25)

        self.blendTxt = QtGui.QLabel()
        self.blendTxt.setText("Blending mode:")
        self.blendTxt.setFixedSize(130, 25)

        self.blendCmb = QtGui.QComboBox()  #texture type values
        self.blendCmb.setFixedSize(100, 25)
        for type in self.blend_types.keys():
            self.blendCmb.addItem(type)

        self.resEdt = QtGui.QLineEdit()
        self.resEdt.setPlaceholderText("export resolution (m/pix), e.g 0.01")
        self.resEdt.setFixedSize(100, 25)

        self.selTxt = QtGui.QLabel()
        self.selTxt.setText("Export for:")
        self.selTxt.setFixedSize(100, 25)

        self.radioBtn_all = QtGui.QRadioButton("all cameras")
        self.radioBtn_sel = QtGui.QRadioButton("selected cameras")
        self.radioBtn_rnd = QtGui.QRadioButton("random 10 cameras")

        self.radioBtn_all.setChecked(True)
        self.radioBtn_rnd.setChecked(False)
        self.radioBtn_sel.setChecked(False)

        layout = QtGui.QGridLayout()   #creating layout
        layout.addWidget(self.resTxt, 0, 1)
        layout.addWidget(self.resEdt, 0, 2)
        layout.addWidget(self.blendTxt, 1, 1)
        layout.addWidget(self.blendCmb, 1, 2)
        layout.addWidget(self.selTxt, 0, 0)
        layout.addWidget(self.radioBtn_all, 1, 0)
        layout.addWidget(self.radioBtn_sel, 2, 0)
        layout.addWidget(self.radioBtn_rnd, 3, 0)
        layout.addWidget(self.btnP1, 4, 1)
        layout.addWidget(self.btnQuit, 4, 2)
        layout.addWidget(self.pBar, 3, 0, 5, 1)
        self.setLayout(layout)

        proc_exp = lambda : self.exp_ortho()

        QtCore.QObject.connect(self.btnP1, QtCore.SIGNAL("clicked()"), proc_exp)
        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))

        self.exec()

    def surf_height(self, chunk, photo):

        points_h = list()
        point_cloud = chunk.point_cloud
        points = point_cloud.points
        npoints = len(points)
        num_valid = 0

        point_index = 0
        for proj in point_cloud.projections[photo]:

            track_id = proj.track_id
            while point_index < npoints and points[point_index].track_id < track_id:
                point_index += 1
            if point_index < npoints and points[point_index].track_id == track_id:
                if not points[point_index].valid:
                    continue

            v = points[point_index].coord
            vt = chunk.transform.matrix.mulp(v)
            if chunk.crs:
                vt = chunk.crs.project(vt)
            points_h.append(vt[2])
            num_valid += 1

        points_h.sort()
        height = points_h[num_valid // 2]

        return height

    def exp_ortho(self):

        doc = PhotoScan.app.document
        chunk = doc.chunk
        path = doc.path.rsplit("\\", 1)[0]

        if not chunk.model:
            PhotoScan.app.messageBox("No mesh generated!\n")
            return False

        try:
            resolution = float(self.resEdt.text())
        except(ValueError):
            PhotoScan.app.messageBox("Incorrect export resolution! Please use point delimiter.\n")
            print("Script aborted.")
            return False

        print("Export started...")  #information message

        self.btnP1.setDisabled(True)
        self.btnQuit.setDisabled(True)
        self.pBar.setMinimum(0)
        self.pBar.setMaximum(100)

        export_list = list()
        if self.radioBtn_sel.isChecked():
            for photo in chunk.cameras:
                if photo.selected:
                    export_list.append(photo)
        elif self.radioBtn_all.isChecked():
            export_list = list(chunk.cameras)
        elif self.radioBtn_rnd.isChecked():
            random_cams = random.sample(range(len(chunk.cameras)), 10) #number of random cameras
            for i in range (0, p_num):
                export_list.append(chunk.cameras[random_cams[i]])
        for photo in chunk.cameras:
            photo.enabled = False

        blending_mode = self.blend_types[self.blendCmb.currentText()]

        processed = 0
        t0 = time.time()

        for i in range (0, len(chunk.cameras)):
            photo = chunk.cameras[i]
            photo.enabled = False

        PhotoScan.app.update()

        for photo in export_list: 

            if not photo.transform:
                continue

            x0 = x1 = x2 = x3 = PhotoScan.Vector((0.0,0.0,0.0))

            width = photo.sensor.width
            height = photo.sensor.height
            calibration = photo.sensor.calibration

            # vectors corresponding to photo corners

            v0 = PhotoScan.Vector(( -calibration.cx / calibration.fx, -calibration.cy / calibration.fy, 1))
            v1 = PhotoScan.Vector(( (width - calibration.cx) / calibration.fx, -calibration.cy / calibration.fy, 1))
            v2 = PhotoScan.Vector(( -calibration.cx / calibration.fx, (height - calibration.cy) / calibration.fy, 1))
            v3 = PhotoScan.Vector(( (width - calibration.cx) / calibration.fx, (height - calibration.cy) / calibration.fy, 1))
            vc = photo.center

            v0.size = v1.size = v2.size = v3.size = vc.size = 4
            v0[3] = v1[3] = v2[3] = v3[3] = 0
            vc[3] = 1

            M = chunk.transform.matrix * photo.transform

            v0_gc = M * v0
            v1_gc = M * v1
            v2_gc = M * v2
            v3_gc = M * v3
            vc_gc = chunk.transform.matrix * vc

            v0_gc.size = v1_gc.size = v2_gc.size = v3_gc.size = vc_gc.size = 3

            # surface normal

            cen_p = photo.center
            cen_t = chunk.transform.matrix.mulp(cen_p)
            if chunk.crs:
                cen_t = chunk.crs.project(cen_t)

            h = self.surf_height(chunk, photo)

            vloc = PhotoScan.Vector((cen_t[0], cen_t[1], h))
            vloc_h = PhotoScan.Vector((cen_t[0], cen_t[1], h))
            vloc_h[2] += 1

            if chunk.crs:
                vloc_gc = chunk.crs.unproject(vloc)
                vloc_h_gc = chunk.crs.unproject(vloc_h)
                surf_n =  vloc_h_gc - vloc_gc
            else:
                vloc_gc = vloc
                vloc_h_gc = vloc_h
                surf_n = vloc_h - vloc

            surf_n.normalize()
            v0_gc.normalize()
            v1_gc.normalize()
            v2_gc.normalize()
            v3_gc.normalize()

            #intersection with the surface

            x0 = intersect(vloc_gc, surf_n, vc_gc, v0_gc)
            x1 = intersect(vloc_gc, surf_n, vc_gc, v1_gc)
            x2 = intersect(vloc_gc, surf_n, vc_gc, v2_gc)
            x3 = intersect(vloc_gc, surf_n, vc_gc, v3_gc)

            if chunk.crs:
                x0 = chunk.crs.project(x0)
                x1 = chunk.crs.project(x1)
                x2 = chunk.crs.project(x2)
                x3 = chunk.crs.project(x3)

            x_0 = min(x0[0],  x1[0], x2[0], x3[0])
            x_1 = max(x0[0],  x1[0], x2[0], x3[0])
            y_0 = min(x0[1],  x1[1], x2[1], x3[1])
            y_1 = max(x0[1],  x1[1], x2[1], x3[1])

            x_0 -= (x_1 - x_0) / 20.
            x_1 += (x_1 - x_0) / 20.
            y_0 -= (y_1 - y_0) / 20.
            y_1 += (y_1 - y_0) / 20.

            reg = (x_0, y_0, x_1, y_1)

            photo.enabled = True
            PhotoScan.app.update()
            p_name = photo.photo.path.rsplit("/", 1)[1].rsplit(".",1)[0]
            p_name = "ortho_" + p_name

            if chunk.crs:
                proj = chunk.crs   ##export in chunk coordinate system
            else:
                proj = PhotoScan.Matrix().diag([1,1,1,1]) #TopXY
            d_x = d_y = resolution

            #recalculating WGS84 resolution from degrees into meters if required
            if chunk.crs:
                if ('UNIT["degree"' in proj.wkt):
                    crd = photo.reference.location

                    #longitude
                    v1 = PhotoScan.Vector((crd[0], crd[1], 0) )
                    v2 = PhotoScan.Vector((crd[0] + 0.001, crd[1], 0))
                    vm1 = chunk.crs.unproject(v1)
                    vm2 = chunk.crs.unproject(v2)
                    res_x = (vm2 - vm1).norm() * 1000

                    #latitude
                    v2 = PhotoScan.Vector( (crd[0], crd[1] + 0.001, 0))
                    vm2 = chunk.crs.unproject(v2)
                    res_y = (vm2 - vm1).norm() * 1000

                    pixel_x = pixel_y = resolution  #export resolution (meters/pix)
                    d_x = pixel_x / res_x
                    d_y = pixel_y / res_y


            if chunk.exportOrthophoto(path + "\\" + p_name + ".tif", format = "tif", blending = blending_mode, color_correction = False, projection = proj, region = reg, dx = d_x, dy = d_y, write_world = True):
                processed +=1
            photo.enabled = False
            self.pBar.setValue(int(processed / len(export_list) * 100))

        for i in range (0, len(chunk.cameras)):
            photo = chunk.cameras[i]
            photo.enabled = True

        PhotoScan.app.update()


        self.btnP1.setDisabled(False)
        self.btnQuit.setDisabled(False)

        t1 = time.time()

        t1 -= t0
        t1 = int(t1)

        PhotoScan.app.messageBox("Processing finished.\nProcessed "+ str(processed) +" images to orthophotos.\nProcessing time: "+ str(t1)  +" seconds.\nPress OK.")  #information message

        return 1

def main():

    global doc
    doc = PhotoScan.app.document

    app = QtGui.QApplication.instance()
    parent = app.activeWindow()

    dlg = ExportOrthoDlg(parent)


PhotoScan.app.addMenuItem("Custom/Export individual orthophotos", main)
