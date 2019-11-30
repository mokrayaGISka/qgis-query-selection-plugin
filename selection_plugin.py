# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuerySelection
                                 A QGIS plugin
 query_selection_plugin
                              -------------------
        begin                : 2018-03-12
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Tom Sawyer/Flexatel
        email                : info@flexatel.ru
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from selection_plugin_dockwidget import QuerySelectionDockWidget
import os.path
from qgis.gui import QgsMessageBar
from qgis.core import QgsMapLayerRegistry


class QuerySelection:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.QgsMapLayerRegistry = QgsMapLayerRegistry

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QuerySelection_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Query Selection')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Query Selection')
        self.toolbar.setObjectName(u'Query Selection')

        #print "** INITIALIZING QuerySelection"

        self.pluginIsActive = False
        self.dockwidget = None


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
        return QCoreApplication.translate('QuerySelection', message)


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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/QuerySelection/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Query Selection'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def changeLayer(self):
        sLayerIndex = self.dockwidget.layerComboBox.currentIndex()
        self.sLayer = self.curLayers[sLayerIndex]
        # print self.sLayer 
        # print self.sLayer.name()  
        #print "change"
    
    def selectButton(self):
        #print "click"
        sF = []
        sFeatures = self.sLayer.selectedFeatures()
        if len (sFeatures)>0:
            for f in sFeatures:
                sF.append(f.id())
        else:
            sFeatures = self.sLayer.getFeatures()
            for f in sFeatures:
                sF.append(f.id())
        exp = str(sF).replace("[","(").replace("]",")").replace('L','')
        #print exp
        self.sLayer.setSubsetString("fid in " + exp)

    def Warning_Message(self):
        #print "lalala" 
        msg = self.iface.messageBar().createMessage('WARNING', 'Would you like to clear the selection?')

        button1 = QPushButton(msg)
        button2 = QPushButton(msg)
        button1.setText('Ok') 
        button2.setText('Cancel') 
        msg.layout().addWidget(button1)
        msg.layout().addWidget(button2)
        self.iface.messageBar().pushWidget(msg, QgsMessageBar.WARNING)


        def Ok():
            self.sLayer.setSubsetString('')

        button1.pressed.connect(Ok)
        button1.pressed.connect(self.iface.messageBar().close)
        button2.pressed.connect(self.iface.messageBar().close)
    
    def onLegendChange(self):
        self.dockwidget.layerComboBox.clear()
        lyrNames = []
        self.curLayers = self.QgsMapLayerRegistry.instance().mapLayers().values()
        if len(self.curLayers) > 0:
            self.dockwidget.pushButton.setEnabled(True)
            self.sLayer = self.curLayers[0]
            for n in self.curLayers:
                lyrNames.append(n.name())
            self.dockwidget.layerComboBox.addItems(lyrNames)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        print "** CLOSING QuerySelection"
        self.dockwidget.layerComboBox.clear()

        # disconnects
        self.dockwidget.pushButton.clicked.disconnect(self.selectButton)
        self.dockwidget.layerComboBox.currentIndexChanged.disconnect(self.changeLayer)
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.onLegendChange)
        self.QgsMapLayerRegistry.instance().layersRemoved.connect(self.onLegendChange)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        print "** UNLOAD QuerySelection"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&QuerySelection'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            print "** STARTING QuerySelection"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = QuerySelectionDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            #print dir(self.dockwidget)
            self.dockwidget.layerComboBox.currentIndexChanged.connect(self.changeLayer)
            self.dockwidget.pushButton.clicked.connect(self.selectButton)
            lyrNames = []
            self.curLayers = self.QgsMapLayerRegistry.instance().mapLayers().values()
            if len(self.curLayers) > 0:
                self.dockwidget.pushButton.setEnabled(True)
                self.sLayer = self.curLayers[0]
                for n in self.curLayers:
                    lyrNames.append(n.name())
                self.dockwidget.layerComboBox.addItems(lyrNames)
            self.dockwidget.pushButton_2.clicked.connect(self.Warning_Message)
            self.QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.onLegendChange)
            self.QgsMapLayerRegistry.instance().layersRemoved.connect(self.onLegendChange)




