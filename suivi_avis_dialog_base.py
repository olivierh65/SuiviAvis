# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'suivi_avis_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_suiviAvisDialogBase(object):
    def setupUi(self, suiviAvisDialogBase):
        suiviAvisDialogBase.setObjectName("suiviAvisDialogBase")
        suiviAvisDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(suiviAvisDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.extractPolyButton = QtWidgets.QPushButton(suiviAvisDialogBase)
        self.extractPolyButton.setGeometry(QtCore.QRect(40, 30, 121, 23))
        self.extractPolyButton.setObjectName("extractPolyButton")
        self.updateMapButton = QtWidgets.QPushButton(suiviAvisDialogBase)
        self.updateMapButton.setGeometry(QtCore.QRect(40, 70, 121, 23))
        self.updateMapButton.setObjectName("updateMapButton")

        self.retranslateUi(suiviAvisDialogBase)
        self.button_box.accepted.connect(suiviAvisDialogBase.accept)
        self.button_box.rejected.connect(suiviAvisDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(suiviAvisDialogBase)

    def retranslateUi(self, suiviAvisDialogBase):
        _translate = QtCore.QCoreApplication.translate
        suiviAvisDialogBase.setWindowTitle(_translate("suiviAvisDialogBase", "Suivi Avis"))
        self.extractPolyButton.setText(_translate("suiviAvisDialogBase", "Extract Polygonnes"))
        self.updateMapButton.setText(_translate("suiviAvisDialogBase", "Update Map"))

