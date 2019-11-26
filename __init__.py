# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuerySelection
                                 A QGIS plugin
 query_selection_plugin
                             -------------------
        begin                : 2018-03-12
        copyright            : (C) 2018 by Tom Sawyer/Flexatel
        email                : info@flexatel.ru
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QuerySelection class from file QuerySelection.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .selection_plugin import QuerySelection
    return QuerySelection(iface)
