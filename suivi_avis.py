# -*- coding: utf-8 -*-
"""
/***************************************************************************
 suiviAvis
                                 A QGIS plugin
 Outils d'aide au suivi des avis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-10-28
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Olivier
        email                : hertrich@club-internet.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QCursor, QGuiApplication
from PyQt5.QtWidgets import QAction, QFileDialog

from qgis.core import QgsVectorLayer, QgsProject, QgsMapLayer, QgsWkbTypes
from qgis.gui import QgsFileWidget

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .suivi_avis_dialog import suiviAvisDialog
import os.path

from .extractPoly import *

from .updateSuivi import *

import pyexcel as pe
from pyexcel_io import *


class suiviAvis:
    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'suiviAvis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = suiviAvisDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Suivi Avis')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'suiviAvis')
        self.toolbar.setObjectName(u'suiviAvis')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('suiviAvis', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/suivi_avis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Suivi Avis'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        self.dlg.tabWidget.currentChanged.connect(self.tab_changed)
        self.dlg.extractPolyButton.clicked.connect(self.extract)

        self.dlg.butGenCSV.clicked.connect(self.genCSV)
        self.dlg.butListInsee.clicked.connect(self.listInsee)
        
        self.dlg.updateMapButton.clicked.connect(self.lectureOffice)
        
        
    def tab_changed(self):
        tabName=self.dlg.tabWidget.tabText(self.dlg.tabWidget.currentIndex())
        try:
            self.dlg.TabFileWidget.fileChanged.disconnect()
        except:
            pass
        
        print ("tab changed, index {0} : {1}".format(self.dlg.tabWidget.currentIndex(), tabName))
        if (tabName == "Masque"):
            self.prep_extract()
        elif(tabName == "Tab2map"):
            self.prep_office()
    def genCSV(self):
        fs = QFileDialog()
        fs.setWindowTitle ("-- Tableur de suivi --")
        fs.setFileMode(QFileDialog.FileMode.ExistingFile)
        fs.setDirectory(os.path.dirname(os.path.dirname(QgsProject.instance().absolutePath())))
        fs.setNameFilter("SCalc (*.ods);; Excel(*.xls);; All Files (*.*)")
        fs.selectNameFilter("*.ods")
        ret = fs.exec()
        if (ret == QFileDialog.DialogCode.Accepted):
            print (fs.selectedFiles()[0])
            self.message ("Lecture tableur ...")
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        
            c=pe.get_book(file_name=fs.selectedFiles()[0])
            s = c.sheet_by_name(self.dlg.defNomOngletMailing.displayText())
            s.save_as(os.path.splitext(fs.selectedFiles()[0])[0] + ".csv")
            self.message ("CSV sauve ...")
            QGuiApplication.restoreOverrideCursor()
            
    def listInsee(self):
        pass
               
    def extract(self):
        print ("recherche")
        ee = extractPoly(self)
        ee.recherche()
    
    def lectureOffice(self):
        print("Update")
        ee=updateSuivi(self)
        ee.update()
    
    def prep_office(self):
        self.dlg.TabFileWidget.setDialogTitle ("-- Tableur de suivi --")
        self.dlg.TabFileWidget.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.TabFileWidget.setDefaultRoot(os.path.dirname(os.path.dirname(QgsProject.instance().absolutePath())))
        self.dlg.TabFileWidget.setFilter ("*.ods;;*.xls;;*.*")
        self.dlg.TabFileWidget.setSelectedFilter(".ods")
        
        self.dlg.TabFileWidget.fileChanged.connect(self.lecture_onglet)
        
        layers=QgsProject.instance().mapLayers()
        for k in layers:
            layer = layers[k]
            if (layer.type() == QgsMapLayer.LayerType.VectorLayer):
                if (QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.GeometryType.PolygonGeometry):
                    print (layer.name())
                    self.dlg.TabLayer.addItem(layer.name(), layer)
        idx = self.dlg.TabLayer.findText(self.dlg.defNomLayer.displayText())
        if (idx != -1):
            self.dlg.TabLayer.setCurrentIndex(idx)
     
    def lecture_onglet(self, chemin):
        print("fileChanged : " + chemin)
        self.message ("Lecture des onglets")
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        c=pe.get_book(file_name=chemin)
        self.dlg.TabOnglet.clear()
        for s in c.sheet_names():
            if (s.startswith("file:")):
                pass
            else:
                self.dlg.TabOnglet.addItem(s)
        QGuiApplication.restoreOverrideCursor()
        idx = self.dlg.TabOnglet.findText(self.dlg.defNomOngletSuivi.displayText())
        if (idx != -1):
            self.dlg.TabOnglet.setCurrentIndex(idx)
        self.message ("Done")
          
    def prep_extract(self):
        self.dlg.MasqueListeCouches.clear()
        self.dlg.MasqueLignePoint.clear()
        layers=QgsProject.instance().mapLayers()
        for k in layers:
            layer = layers[k]
            if (layer.type() == QgsMapLayer.LayerType.VectorLayer):
                if (QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.GeometryType.PolygonGeometry):
                    print (layer.name())
                    self.dlg.MasqueListeCouches.addItem(layer.name(), layer)
                elif (QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.GeometryType. PointGeometry) or \
                    (QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.GeometryType. LineGeometry):
                    if (QgsProject.instance().layerTreeRoot().findLayer(layer.id()).isVisible()):
                        self.dlg.MasqueLignePoint.addItem(layer.name(), layer)
        self.dlg.MasqueNomCouche.setText(self.dlg.defNomLayer.displayText())
                            
    def message(self, msg):
        self.dlg.Message.setText(msg)
        self.dlg.Message.repaint()
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Suivi Avis'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        
        self.tab_changed()
        # initialise le tab actif
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
       
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            
            pass

