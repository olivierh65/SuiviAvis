# -*- coding: utf-8 -*-
'''
Created on 28 oct. 2018

@author: Olivier
'''
from PyQt5.QtCore import QSettings, QVariant, QCoreApplication, Qt
from PyQt5.QtGui import QColor, QGuiApplication, QCursor
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
        
        ll=self.parent.dlg.MasqueLignePoint.currentData()
        if (self.parent.dlg.selectionSeulement.isChecked()):
            self.parent.iface.messageBar().pushMessage ("Selection seulement dans {0}".format(ll.name()), Qgis.MessageLevel.Info)
            self.parent.iface.messageBar().update()
            ss=True
            print (ll.selectedFeatureCount())
            if (ll.selectedFeatureCount() == 0):
                self.parent.iface.messageBar().pushCritical ("Erreur", "Pas d entite selectionnee dans {0}".format(ll.name()))
        
        self.parent.message ("Recherche ...")
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        
        paramin = { 'INPUT' : self.parent.dlg.MasqueListeCouches.currentData().id(),
        'INTERSECT' : QgsProcessingFeatureSourceDefinition(ll.id(), ss),
        'OUTPUT' : 'memory:',
        'PREDICATE' : [0] }
        res= processing.run ('native:extractbylocation', paramin)
        # verifier si erreur
        print (res['OUTPUT'])
        l=res['OUTPUT']
        
        # Ajout des champs
        res=l.dataProvider().addAttributes([QgsField("valide", QVariant.Date), QgsField("note", QVariant.String), \
                                           QgsField("supprime", QVariant.Date), QgsField("ajoute", QVariant.Date)])
        l.updateFields()
        if (not res):
            print ("Erreur creation attributs")
            self.parent.iface.messageBar().pushCritical ("Erreur", "Erreur de creation des attributs")
        
        if (len(self.parent.dlg.MasqueNomCouche.displayText().strip()) > 0):
            l.setName(self.parent.dlg.MasqueNomCouche.displayText().strip())
            
        self.defStyle(l)
        
        QgsProject.instance().addMapLayer(l)
        
        QGuiApplication.restoreOverrideCursor()
        self.parent.message ("Done")
        