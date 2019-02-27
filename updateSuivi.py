'''
Created on 28 oct. 2018

@author: Olivier
'''
from PyQt5.QtCore import QSettings, QVariant, QCoreApplication, Qt
from PyQt5.QtGui import  QGuiApplication, QCursor
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
        attr_idx=-1
        note_idx=-1
        for i in layer.attributeList():
            if (layer.attributeDisplayName(i) == 'valide'):
                attr_idx=i
            elif (layer.attributeDisplayName(i) == 'note'):
                 note_idx=i
        
        if (attr_idx == -1):
            print("PAs de colonne 'valide'")        
            return
        layer.startEditing()
        for i in range(1, len(s.column_at(0))-1):
            if (s[i,recep]):
                print (s[i, insee])
                for f in layer.getFeatures("insee = {0}".format(s[i, insee])):
                    # convertit la date au format ISO
                    dd = s[i, recep].strftime("%Y-%m-%d")
                    layer.changeAttributeValue(f.id(), attr_idx, dd )
                    if(note_idx > 0):
                        layer.changeAttributeValue(f.id(), note_idx, s[i, observations])
        layer.commitChanges()

        QGuiApplication.restoreOverrideCursor()
        self.parent.message ("Done")