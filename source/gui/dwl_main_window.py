import os
import sys

from PyQt4 import QtCore, QtGui

import numpy

import veusz.setting
import veusz.windows.plotwindow 
import veusz.document as document
from veusz.document.commandinterface import CommandInterface

from dwl_multidop_exceptions import *
from fileparsing.dwl_multidop_tx import TX
from fileparsing.dwl_multidop_tw import TW
from gui.ui_dwl_main_window import Ui_DWLMainWindow

class DWLMainWindow(QtGui.QMainWindow):

    def __init__(self, file_prefix):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

# set up status bar
        self.statusBar().showMessage('Ready')
        self.current_subject_label = QtGui.QLabel(self.statusBar())
        self.statusBar().addPermanentWidget(self.current_subject_label)
        self.loading_label = QtGui.QLabel(self.statusBar())
        self.loading_progress_bar = QtGui.QProgressBar(self.statusBar())

# set up menu
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')

        open_action = QtGui.QAction(QtGui.QIcon('icons/open.png'), '&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open different fileset')
        self.connect(open_action, QtCore.SIGNAL('triggered()'), self.open_file)
        self.file_menu.addAction(open_action)

        self.exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Quit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.connect(self.exit_action, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.file_menu.addAction(self.exit_action)

        self.show()

# set up graph
        self.document = document.Document()
        self.plot = veusz.windows.plotwindow.PlotWindow(self.document, self)
        self.toolbar = self.plot.createToolbar(self, None)
        self.toolbar.show()
        self.setCentralWidget(self.plot)

# turn off anti-aliasing for speed
        veusz.setting.settingdb['plot_antialias'] = False

        self.interface = CommandInterface(self.document)
        i = self.interface
        i.Set('width', u'20cm')
        i.Set('height', u'27cm')
        i.To(i.Add('page', name='page1'))
        i.To(i.Add('grid', name='grid1'))
        i.Set('rows', 3)
        i.Set('columns', 1)
        i.Set('leftMargin', u'0.2cm')
        i.Set('bottomMargin', u'0.2cm')

# get initial velocity data
        self.load_file(file_prefix)


# @todo find out if this color scheme mimic the machine
        chan1color = u'green'
        chan2color = u'orange'

# add the graphs
        def add_graph(graphname, xmin, xmax):
            i.To('/page1/grid1')
            i.To(i.Add('graph', name=graphname, autoadd=False))
            i.To(i.Add('axis', name='x', autoadd=False))
            i.Set('min', xmin)
# bottom plot shows all
            if xmax > 0.0:
                i.Set('max', xmax)
            i.To('..')
            i.To(i.Add('axis', name='y', autoadd=False))
            i.Set('label', u'Velocity [\\emph{cm/s}]')
            i.Set('direction', 'vertical')
            i.To('..')

            i.Add('xy', name='chan1', autoadd=False)
            i.To('chan1')
            i.Set('xData', u'time')
            i.Set('yData', u'chan1_vel')
            i.Set('PlotLine/color', chan1color)
            i.Set('marker', u'none')
            i.To('..')

            i.Add('xy', name='chan2', autoadd=False)
            i.To('chan2')
            i.Set('xData', u'time')
            i.Set('yData', u'chan2_vel')
            i.Set('PlotLine/color', chan2color)
            i.Set('marker', u'none')

            i.To('..')
            i.Add('xy', name='hits', autoadd=False)
            i.To('hits')
            i.Set('xData', u'hit_times')
            i.Set('yData', u'hit_ys')
            i.Set('PlotLine/hide', True)
            i.Set('MarkerFill/color', u'grey')
            i.Set('labels', u'hit_labels')
            i.Set('Label/posnHorz', u'centre')
            i.Set('Label/posnVert', u'top')

        add_graph('topgraph', 0.0, 5.0)
        i.To('/page1/grid1/topgraph/x')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.75pt')
        i.To('../y')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.7pt')
        add_graph('middlegraph', 0.0, 20.0)
        add_graph('bottomgraph', 0.0, -1)
        



## 
# @brief read in the data from the .tx and tw files
# 
# @param file_prefix prefix to the files
# 
# @return 
    def load_file(self, file_prefix):
# find the filepath
        filepath = file_prefix
        if not os.path.isabs(file_prefix):
            filepath = os.path.abspath(file_prefix)
        tx_file = None
        tw_file = None
        if filepath[-2:] == '.t' or filepath[-2:] == '.T':
            filepath = filepath[:-2]
            tx_file = glob.glob(filepath + '.[Tt][Xx][0-9]')
            tw_file = glob.glob(filepath + '.[Tt][Ww][0-9]')
            if len(tx_file) > 1:
                print "More than one file encounterd; please specify full path."
                sys.exit(1)
        elif filepath[-4:-1] == '.tx' or filepath[-4:-1] == '.TX':
            tx_file = filepath
            other_file = filepath[:-1] + 'w' + filepath[-1:]
            if not os.path.exists(other_file):
                other_file = filepath[:-2] + 'W' + filepath[-1:]
            tw_file = other_file
        elif filepath[-4:-1] == '.tw' or filepath[-4:-1] == '.TW':
            tw_file = filepath
            other_file = filepath[:-1] + 'x' + filepath[-1:]
            if not os.path.exists(other_file):
                other_file = filepath[:-2] + 'X' + filepath[-1:]
            tx_file = other_file


        if not tw_file or not tx_file or tx_file[-1] == 't':
            e = ExtensionError(file_prefix, '.tx? and .tw? or .TX? and .TW?')
            raise e
            pass

        self.setWindowTitle('DWL Multidop L2 Viewer - ' + tx_file)

# load tx file
        self.statusBar().clearMessage()
        self.statusBar().insertWidget(0, self.loading_label)
        self.statusBar().insertWidget(1, self.loading_progress_bar)
        self.loading_label.setText('Loading metadata .TX file...')
        self.loading_label.show()
        self.loading_progress_bar.show()

        self.tx = TX(tx_file, self.loading_progress_bar)

# load tw file
        self.loading_label.setText('Loading velocity data from .TW FILE...')
        self.tw = TW(tw_file, self.tx.metadata['prf'], self.tx.metadata['doppler_freq_1'],
                self.tx.metadata['doppler_freq_2'], self.loading_progress_bar)
        self.current_subject_label.setText('Current Patient: ' +
                self.tx.metadata['patient_name'])

        self.statusBar().removeWidget(self.loading_label)
        self.statusBar().removeWidget(self.loading_progress_bar)

# import velocity data into plot
        i = self.interface
        i.SetData('chan1_vel', self.tw.chan1)
        i.SetData('chan2_vel', self.tw.chan2)
        sample_freq = float(self.tx.metadata['sample_freq'])
        time = numpy.arange(len(self.tw.chan1)) / sample_freq
        i.SetData('time', time)

# import hits data into plot
#        use_centisec_clock: whether to use the 1/100 sec clock recordings from the hits data file, or the hr:min:sec, values instead.  On our machine, we found that the there was a large discrepency as for long time period recordings
        use_centisec_clock = True
# we stagger the Y location of the hits so that they do not overlap
        chansmax = max([self.tw.chan1.max(), self.tw.chan2.max()])
        chansmin = min([self.tw.chan1.min(), self.tw.chan2.min()])
        hit_y_min = chansmax / 3.0
        hit_y_inc = chansmax / 8.0
        hit_y = hit_y_min
        hit_time = 0.0
        hit_ys = numpy.zeros(len(self.tx.metadata['hits']))
        hit_times = numpy.zeros(len(self.tx.metadata['hits']))
        hit_labels = []
        count = 0
        for hit in self.tx.metadata['hits']:
            if hit_y > chansmax* 3.0/4.0:
                hit_y = hit_y_min
            else:
                hit_y += hit_y_inc
            if use_centisec_clock:
                hit_time = float(hit[0]) / 100.0
            else:
      	    #### use the hr:min:sec recording
	            #startime[0] = hour
	            #starttime[1] = minute
	            #starttime[2] = second
                starttime = [ int(x) for x in metadata['start_time'].split(':') ]
                curtime = [ int(x) for x in hit[2].split(':') ]
                # deal with clock wrap around, assuming 
                # the examine takes less than 24 hrs :P
                if curtime[0] >=  starttime[0] :
                  sep_hours = (curtime[0]-starttime[0])*3600
                else:
                  sep_hours = (24 - starttime[0] + curtime[0])*3600
                # time offset from start in seconds
                hit_time = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
                hit_time = float(hittime)

            hit_times[count] = hit_time
            hit_ys[count] = hit_y
            count += 1
            hit_labels.append(hit[1] + ' ' + hit[2])


        i.SetData(u'hit_times', hit_times)
        i.SetData(u'hit_ys', hit_ys)
        i.SetDataText(u'hit_labels', hit_labels)
                
        


## 
# @brief bring up a file open dialog and load in the requestd data set
# 
# @return 
    def open_file(self):
        fileprefix = QtGui.QFileDialog.getOpenFileName(None, "Select *.TX0 or *.TW0 file.", 
                os.getcwd(), 
                ("DWL MultiDop L2 Files (*.TX? *.TW? *.tx? *.tw?)"))
        fileprefix = str(fileprefix)
        self.load_file(fileprefix)

