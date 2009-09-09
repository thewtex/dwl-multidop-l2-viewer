import numpy

from PyQt4 import QtGui, QtCore

import veusz.widgets as widgets
from veusz.windows.plotwindow import PlotWindow

class DWLPlotWindow(PlotWindow):
    def __init__(self, document, parent=None, menu=None):
        PlotWindow.__init__(self, document, parent, menu)

    def mouseReleaseEvent(self, event):
        """Adjust the x-axis location in the plot above to the location clicked
        plot."""
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

        if event.button() == QtCore.Qt.LeftButton and not self.ignoreclick:
            event.accept()
            self.scrolltimer.stop()
            if self.clickmode == 'select':
                # find axes which map to this position
                pos = self.mapToScene(event.pos())
                px, py = pos.x(), pos.y()

                vals = {}
                graph_to_adjust = ''
                for widget, bounds in self.widgetpositions:
                    # if widget is axis, and point lies within bounds
                    if( px>=bounds[0] and px<=bounds[2] and
                        py>=bounds[1] and py<=bounds[3] ):
                        if isinstance(widget, widgets.Axis):
                            # convert correct pointer position
                            if widget.settings.direction == 'horizontal':
                                val = px
                            else:
                                val = py
                            coords=widget.plotterToGraphCoords(bounds, numpy.array([val]))
                            vals[widget.name] = coords[0]
                        elif isinstance(widget, widgets.Graph):
                            if widget.name == "bottom_graph":
                                graph_to_adjust = 'middle_graph'
                            if widget.name == 'middle_graph':
                                graph_to_adjust = 'top_graph'
                if graph_to_adjust:
                    self.emit(QtCore.SIGNAL('sigAdjustGraphXLoc'), (vals,
                        graph_to_adjust))
            elif self.currentclickmode == 'scroll':
                # return the cursor to normal after scrolling
                self.clickmode = 'select'
                self.currentclickmode = None
                qt4.QApplication.restoreOverrideCursor()
            elif self.currentclickmode == 'graphzoom':
                self.zoomrect.hide()
                self.doZoomRect(self.mapToScene(event.pos()))
                self.grabpos = None
            elif self.currentclickmode == 'viewgetclick':
                self.clickmode = 'select'

