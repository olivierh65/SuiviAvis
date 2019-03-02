# -*- coding: utf-8 -*-
'''
Created on 28 oct. 2018

@author: Olivier
'''
from PyQt5 import QtCore
from PyQt5.QtCore import QSettings, QVariant, QCoreApplication, Qt
from PyQt5.QtGui import QColor, QGuiApplication, QCursor
from PyQt5.QtWidgets import QListWidgetItem

from qgis.core import (Qgis,
       QgsProcessingAlgorithm,
       QgsProcessingParameterNumber,
       QgsProcessingParameterFeatureSource,
       QgsProcessingParameterFeatureSink,
       QgsProcessingFeatureSourceDefinition,
       QgsVectorLayer,
       QgsProject,
       QgsRuleBasedRenderer,
       QgsSymbol,
       QgsFillSymbol,
       QgsLineSymbol,
       QgsSimpleLineSymbolLayer,
       QgsField ,
       )

from qgis.core import QgsSettings

from qgis.gui import QgsMessageBar

import processing

class extractPoly():
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent = parent
    
    def defStyle(self, layer):
        #
        # fs=l.renderer().rootRule().children()[1].symbols()[0]
        # sl ==> QgsSimpleLineSymbolLayer
        # sl=fs.symbolLayers()[0]
        # symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        # Exporterle Style (.qml) pour determiner les attributs
        symb_def = { 'color' : '53,227,47,77',
                    'joinstyle' : 'bevel',
                    'outline_color' : '0,0,0,255',
                    'outline_style' : 'dash',
                    'outline_width' :'0.5',
                    'outline_width_unit' : 'MM',
                    'style' : 'solid'}
        symbol = QgsFillSymbol.createSimple (symb_def)
        renderer = QgsRuleBasedRenderer(symbol)
        root_rule = renderer.rootRule()
        rule = root_rule.children()[0]
        rule.setLabel("Valide")
        rule.setFilterExpression("\"valide\" is not null and \"supprime\" is null")
        # root_rule.appendChild(rule)
        
        symb_def = { 'capstyle' : 'square',
                    'customdash' : '5;2',
                    'customdash_unit' : 'MM',
                    'customdash_unit' : '0',
                    'line_style' : 'dash',
                    'line_color' : '200,194,194,255',
                    'joinstyle' : 'bevel',
                    'line_width' : '0.80',
                    'line_width_unit' : 'MM',
                    'offset' : '0',
                    'use_custom_dash' : '1'}
        symbol = QgsFillSymbol.createSimple (symb_def)
        
        symbol.changeSymbolLayer(0, QgsSimpleLineSymbolLayer.create(symb_def))
        
        rule = QgsRuleBasedRenderer.Rule(symbol)
        rule.setLabel("En attente")
        rule.setFilterExpression("\"valide\" is null and \"supprime\" is null")
        root_rule.appendChild(rule)
        
        layer.setRenderer(renderer)
        
    def recherche(self):
        # Paramètres en entrée:
        # { 'INPUT' : 'C:/Olivier/Documents/Carto/References/Vecteur/communes-20140629-5m-shp/communes-20140629-5m.shp', 
        # 'INTERSECT' : QgsProcessingFeatureSourceDefinition('TraceMatin20160930224546251', True),
        # 'OUTPUT' : 'C:/Olivier/Documents/Collectif/Telethon 2018/Cartes/Enduro/SuiviValidation.shp', 
        # 'PREDICATE' : [0] }
        ss = False
        layers = []
        # print ("Lancement de la recherche\n")
        filter_invalid = processing.QgsSettings().value('Processing/Configuration/FILTER_INVALID_GEOMETRIES')
        # ignore les entites invalides
        processing.QgsSettings().setValue('Processing/Configuration/FILTER_INVALID_GEOMETRIES', '0')
        for ll_item in range(0, self.parent.dlg.MasqueLignePoint.count()):
            item=self.parent.dlg.MasqueLignePoint.item(ll_item)
            if (item.checkState() != Qt.Checked):
                continue
            # print ("Layer : {0}\n".format(item.text()))
            ll=item.data(QtCore.Qt.UserRole)
            if (self.parent.dlg.selectionSeulement.isChecked()):
                self.parent.iface.messageBar().pushMessage ("Selection seulement dans {0}".format(ll.name()), Qgis.MessageLevel.Info)
                self.parent.iface.messageBar().update()
                ss=True
                # print (ll.selectedFeatureCount())
                if (ll.selectedFeatureCount() == 0):
                    self.parent.iface.messageBar().pushCritical ("Erreur", "Pas d entite selectionnee dans {0}".format(ll.name()))
        
            self.parent.message ("Recherche ...")
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            
            paramin = { 'INPUT' : self.parent.dlg.MasqueListeCouches.currentData().id(),
            'INTERSECT' : QgsProcessingFeatureSourceDefinition(ll.id(), ss),
            'OUTPUT' : 'memory:',
            'PREDICATE' : [0] }
            try:
                res= processing.run ('native:extractbylocation', paramin)
                # verifier si erreur
                # print ("Extract {0} : {1}\n".format(item.text(), res['OUTPUT']))
                layers.append(res['OUTPUT'])
            except Exception as err:
                self.parent.iface.messageBar().pushCritical ("Erreur", "Exception : {0}".format(err))
                processing.QgsSettings().setValue('Processing/Configuration/FILTER_INVALID_GEOMETRIES', filter_invalid)
                QGuiApplication.restoreOverrideCursor()
        
        print ("Nombre de layers : {0}\n".format(len(layers)))
        if (len(layers) > 1 ):
            paramin = { 'LAYERS' : layers, 'CRS' : None, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
            res = processing.run ('native:mergevectorlayers', paramin)
            l=res['OUTPUT']
            # print ("Merge : {0}\n".format(l))
        elif (len(layers) == 1):
            l=layers[0]

        QGuiApplication.restoreOverrideCursor()
        processing.QgsSettings().setValue('Processing/Configuration/FILTER_INVALID_GEOMETRIES', filter_invalid)

        # Ajout des champs
        res=l.dataProvider().addAttributes([QgsField("valide", QVariant.Date), QgsField("note", QVariant.String), \
                                           QgsField("supprime", QVariant.Date), QgsField("ajoute", QVariant.Date)])
        l.updateFields()
        if (not res):
            # print ("Erreur creation attributs")
            self.parent.iface.messageBar().pushCritical ("Erreur", "Erreur de creation des attributs")
        
        if (len(self.parent.dlg.MasqueNomCouche.displayText().strip()) > 0):
            l.setName(self.parent.dlg.MasqueNomCouche.displayText().strip())

        self.defStyle(l)
        
        QgsProject.instance().addMapLayer(l)
        QGuiApplication.restoreOverrideCursor()
        self.parent.message ("Done")
        