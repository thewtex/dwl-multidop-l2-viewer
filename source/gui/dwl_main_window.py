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
from gui.plotwindow import DWLPlotWindow

class DWLMainWindow(QtGui.QMainWindow):

    def __init__(self, file_prefix):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

# set up status bar
        statusbar = self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(statusbar)
        self.statusBar().showMessage('Ready')
        self.current_subject_label = QtGui.QLabel(statusbar)
        self.statusBar().addPermanentWidget(self.current_subject_label)
        self.loading_label = QtGui.QLabel(statusbar)
        self.loading_progress_bar = QtGui.QProgressBar(statusbar)
        self.axis_values_label = QtGui.QLabel(statusbar)
        statusbar.addWidget(self.axis_values_label)
        self.axis_values_label.show()

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
        self.plot = DWLPlotWindow(self.document, self)
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

# plot channel 1
            i.Add('xy', name='chan1', autoadd=False)
            i.To('chan1')
            i.Set('xData', u'time')
            i.Set('yData', u'chan1_vel')
            i.Set('PlotLine/color', chan1color)
            i.Set('marker', u'none')
            i.To('..')

# plot channel 2
            i.Add('xy', name='chan2', autoadd=False)
            i.To('chan2')
            i.Set('xData', u'time')
            i.Set('yData', u'chan2_vel')
            i.Set('PlotLine/color', chan2color)
            i.Set('marker', u'none')

# plot hits
            i.To('..')
            i.Add('xy', name='hits', autoadd=False)
            i.To('hits')
            i.Set('xData', u'hit_times')
            i.Set('yData', u'hit_ys')
            i.Set('PlotLine/hide', True)
            i.Set('MarkerFill/color', u'grey')
            i.Set('Label/color', u'grey')
            i.Set('labels', u'hit_labels')
            i.Set('Label/posnHorz', u'centre')
            i.Set('Label/posnVert', u'top')

# plot marks
            mark_colors = {'MRK1': u'red',
                    'MRK2': u'blue',
                    'MRK3': u'cyan',
                    'MRK4': u'magenta',
                    'MRK5': u'darkcyan',
                    'MRK6': u'darkmagenta' }
            i.To('..')
            dataset_prefixes = set([dataset[:4] for dataset in i.GetDatasets()])
            for p in dataset_prefixes:
                if p[:3] == 'MRK':
                    i.Add('xy', name=p, autoadd=False)
                    i.To(p)
                    i.Set('xData', p + '_times')
                    i.Set('yData', p + '_ys')
                    i.Set('PlotLine/hide', True)
                    i.Set('MarkerFill/color', mark_colors[p])
                    i.Set('Label/color', mark_colors[p])
                    i.Set('labels', p + '_labels')
                    i.Set('Label/posnHorz', u'centre')
                    i.Set('Label/posnVert', u'top')
                    i.To('..')

        add_graph('top_graph', 0.0, 5.0)
        i.To('/page1/grid1/top_graph/x')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.75pt')
        i.To('../y')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.7pt')
        add_graph('middle_graph', 0.0, 20.0)
        i.To('/page1/grid1/middle_graph')
        i.Add('rect', name='window', autoadd=False)
        i.To('window')
        i.Set('xPos', [2.5/20.0])
        i.Set('yPos', [0.5])
        i.Set('width', [5.0/20.0])
        i.Set('height', [1.0])
        i.Set('Border/color', 'darkblue')
        i.Set('Border/width', '1.0pt')
        i.Set('Fill/transparency', 80)
        i.Set('Fill/hide', False)
        i.Set('Fill/color', 'blue')
        add_graph('bottom_graph', 0.0, -1)
        i.To('/page1/grid1/bottom_graph/x')
        i.Set('label', u'Time [\\emph{s}]')
        i.To('..')
        i.Add('rect', name='window', autoadd=False)
        i.To('window')
        i.Set('xPos', [10.0/self.max_time])
        i.Set('yPos', [0.5])
        i.Set('width', [20.0/self.max_time])
        i.Set('height', [1.0])
        i.Set('Border/color', 'darkblue')
        i.Set('Border/width', '1.0pt')
        i.Set('Fill/transparency', 80)
        i.Set('Fill/hide', False)
        i.Set('Fill/color', 'blue')

# print current x,y mouse position in lower left hand corner
        self.connect(self.plot, QtCore.SIGNAL("sigAxisValuesFromMouse"),
                self.slotUpdateAxisValues)

# adjust the x location in graphs above the one clicked
        self.connect(self.plot, QtCore.SIGNAL('sigAdjustGraphXLoc'),
                self.slotAdjustGraphXLoc)




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
        self.max_time = len(self.tw.chan1) / sample_freq
        i.SetData('time', time)

        chandel = max([self.tw.chan1.max(), self.tw.chan2.max()]) - min([self.tw.chan1.min(), self.tw.chan2.min()])

# import hits data and marks into plot
        hit_times, hit_ys, hit_labels = self._place_events(self.tx.metadata['hits'], chandel*0.1, chandel*0.8)
        i.SetData(u'hit_times', hit_times)
        i.SetData(u'hit_ys', hit_ys)
        i.SetDataText(u'hit_labels', hit_labels)

        marks = dict()
        for mark in self.tx.metadata['marks']:
            if mark[1] not in marks:
                marks[mark[1]] = [mark]
            else:
                marks[mark[1]].append(mark)
        for markkey, markval in marks.iteritems():
            mark_times, mark_ys, mark_labels = self._place_events(markval,
                    chandel*0.1+0.05*chandel, chandel*0.8)
            i.SetData(markkey + '_times', mark_times)
            i.SetData(markkey + '_ys', mark_ys)
            i.SetDataText(markkey + '_labels', mark_labels)
        

    def _place_events(self, events, event_y_min, event_y_max):
        """take mark and hit events and determine their location on the
        plot"""
#           use_centisec_clock: whether to use the 1/100 sec clock recordings from the hits data file, or the hr:min:sec, values instead.  On our machine, we found that the there was a large discrepency as for long time period recordings
        use_centisec_clock = True

# we stagger the Y location of the hits so that they do not overlap
        event_y_inc = (event_y_max - event_y_min) / 6.0
        event_y = event_y_min
        event_time = 0.0
        event_ys = numpy.zeros(len(events))
        event_times = numpy.zeros(len(events))
        event_labels = []
        count = 0
        for event in events:
            if event_y > event_y_max:
                event_y = event_y_min
            else:
                event_y += event_y_inc
            if use_centisec_clock:
                event_time = float(event[0]) / 100.0
            else:
            #### use the hr:min:sec recording
                #startime[0] = hour
                #starttime[1] = minute
                #starttime[2] = second
                starttime = [ int(x) for x in metadata['start_time'].split(':') ]
                curtime = [ int(x) for x in event[2].split(':') ]
                # deal with clock wrap around, assuming 
                # the examine takes less than 24 hrs :P
                if curtime[0] >=  starttime[0] :
                  sep_hours = (curtime[0]-starttime[0])*3600
                else:
                  sep_hours = (24 - starttime[0] + curtime[0])*3600
                # time offset from start in seconds
                event_time = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
                event_time = float(eventtime)

            event_times[count] = event_time
            event_ys[count] = event_y
            count += 1
            event_labels.append(event[1] + ' ' + event[2])
        return (event_times, event_ys, event_labels)

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


    def slotUpdateAxisValues(self, values):
        """Update the position where the mouse is relative to the axes."""

        if values:
            # construct comma separated text representing axis values
            valitems = []
            for name, val in values.iteritems():
                valitems.append('%s=%#.4g' % (name, val))
            valitems.sort()
            self.axis_values_label.setText(', '.join(valitems))
        else:
            self.axis_values_label.setText('No position')

    def slotAdjustGraphXLoc(self, values):
        i = self.interface
        print values
