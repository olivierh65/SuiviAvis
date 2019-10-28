'''
Created on 28 oct. 2018

@author: Olivier
'''
from PyQt5.QtCore import QSettings, QVariant, QCoreApplication, Qt
from PyQt5.QtGui import  QGuiApplication, QCursor
from qgis.gui import QgsMessageBar
from qgis.core import Qgis, QgsMessageLog
import pyexcel as pe
import datetime

class updateSuivi():
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent= parent
    
    def update(self):
        
        self.parent.message ("Lecture tableur ...")
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        
        c=pe.get_book(file_name=self.parent.dlg.TabFileWidget.filePath())
        s = c.sheet_by_name(self.parent.dlg.TabOnglet.currentText())
            
        recep = s.row_at(0).index(self.parent.dlg.defNomColDateValide.displayText())
        insee = s.row_at(0).index(self.parent.dlg.defNomCodeInsee.displayText())

        observations = s.row_at(0).index(self.parent.dlg.defColNomObservations.displayText())
        layer = self.parent.dlg.TabLayer.currentData()
        self.parent.message ("Layer : {0}\n".format(layer.id()))
        attr_idx=-1
        note_idx=-1
        col_insee_exist=-1
        if (len(self.parent.dlg.defDbCodeInsee.displayText().strip()) > 0):
            col_insee = self.parent.dlg.defDbCodeInsee.displayText().strip()
        else:
            col_insee = "insee"
        self.parent.message("col_insee : {0}\n".format(col_insee))
        for i in layer.attributeList():
            if (layer.attributeDisplayName(i) == 'valide'):
                attr_idx=i
            elif (layer.attributeDisplayName(i) == 'note'):
                note_idx=i
            elif (layer.attributeDisplayName(i) == col_insee):
                col_insee_exist=i
        
        if (col_insee_exist == -1):
            self.parent.message("Pas de colonne '{0}'. Voir le journal de messages\n".format(col_insee))
            QgsMessageLog.logMessage("Pas de colonne '{0}'\n".format(col_insee))
            QgsMessageLog.logMessage("Colonnes existantes : ")
            lst_col=""
            for i in layer.attributeList():
                lst_col += "{0}{1}".format(',' if i > 0 else '', layer.attributeDisplayName(i))
            QgsMessageLog.logMessage(lst_col)
            QGuiApplication.restoreOverrideCursor()
            self.parent.iface.messageBar().pushMessage("Error", "Pas de colonne '{0}'\n Colonnes existantes : {1}".format(col_insee, lst_col), level=Qgis.Critical)
            return
        
        if (attr_idx == -1):
            self.parent.message("Pas de colonne 'valide'\n")
            QgsMessageLog.logMessage("Pas de colonne 'valide'\n")
            QGuiApplication.restoreOverrideCursor()
            self.parent.iface.messageBar().pushMessage("Error", "Pas de colonne 'valide'", level=Qgis.Critical)
            return
            
        layer.startEditing()
        for i in range(1, len(s.column_at(0))-1):
            if (s[i,recep]):
                print (s[i, insee])
                for f in layer.getFeatures("{0} = {1}".format(col_insee, s[i, insee])):
                    # convertit la date au format ISO
                    dd = s[i, recep].strftime("%Y-%m-%d")
                    print ("Insee : {0} ==> {1}\n".format(s[i, insee], dd))
                    layer.changeAttributeValue(f.id(), attr_idx, dd )
                    if(note_idx > 0):
                        layer.changeAttributeValue(f.id(), note_idx, s[i, observations])
        layer.commitChanges()

        QGuiApplication.restoreOverrideCursor()
        self.parent.message ("Done")