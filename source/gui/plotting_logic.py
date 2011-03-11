from  PyQt4 import QtCore 

from veusz.document.commandinterface import CommandInterface
import veusz.setting

from fileparsing.dwl_multidop_load_file import DWLMultidopLoadFile

import numpy as np

## 
# @brief implement logic of how plots look and behave
class PlottingLogic(QtCore.QObject):
    def __init__(self, main_window, document, file_prefix):
        veusz.setting.settingdb['plot_antialias'] = False

        self.document = document
        self.interface = CommandInterface(self.document)
        self.file_loader = DWLMultidopLoadFile(self.interface, main_window)
        self.load_file(file_prefix)
        self._set_up_page()
        self._set_up_top_graph()
        self._set_up_middle_graph()
        self._set_up_bottom_graph()

# adjust the x location in graphs above the one clicked
        self.connect(main_window.plot, QtCore.SIGNAL('sigAdjustGraphXLoc'),
                self.slotAdjustGraphXLoc)

    def load_file(self, file_prefix):
        self.max_time = self.file_loader.load_file(file_prefix)

    def _set_up_page(self):
        i = self.interface
        i.Set('width', u'20cm')
        i.Set('height', u'27cm')
        i.To(i.Add('page', name='page1'))
        i.To(i.Add('grid', name='grid1'))
        i.Set('rows', 3)
        i.Set('columns', 1)
        i.Set('leftMargin', u'0.2cm')
        i.Set('bottomMargin', u'0.2cm')

## 
# @brief add one of the three graphs
# 
# @param graphname
# @param xmin
# @param xmax
# 
# @return 
    def _add_graph(self, graphname, xmin, xmax):
        i = self.interface
# @todo find out if this color scheme mimic the machine
        chan1color = u'green'
        chan2color = u'orange'
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

    def _set_up_top_graph(self):
        i = self.interface
        self._add_graph('top_graph', 0.0, 5.0)
        i.To('/page1/grid1/top_graph/x')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.75pt')
        i.To('../y')
        i.Set('GridLines/style', u'dotted-fine')
        i.Set('GridLines/hide', False)
        i.Set('GridLines/width', '0.7pt')
        i.To('../chan1')
        i.Set('key', u'Channel 1 TAP =')
        i.To('../chan2')
        i.Set('key', u'Channel 2 TAP =')
        i.To('..')
        i.Add('key', name='tap')
        i.To('tap')
        i.Set('horzPosn', u'right')
        i.Set('vertPosn', u'top')

    def _set_up_middle_graph(self):
        i = self.interface
        self._add_graph('middle_graph', 0.0, 20.0)
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

    def _set_up_bottom_graph(self):
        i = self.interface
        self._add_graph('bottom_graph', 0.0, -1)
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

    def slotAdjustGraphXLoc(self, values):
        i = self.interface
        graph_to_adjust = values[1]
        target_time = values[0]['x']
        if graph_to_adjust == 'top_graph':
            i.To('/page1/grid1/top_graph/x')
            min_time = float(target_time - 2.5)
            max_time = float(target_time + 2.5)
            i.Set('min', min_time)
            i.Set('max', max_time)
            time = i.GetData('time')[0]
            chan1 = i.GetData('chan1_vel')[0]
            chan2 = i.GetData('chan2_vel')[0]
            print( min_time )
            print( max_time )
            print( time )
            target_time_idxs = np.logical_and(time > min_time, time < max_time)
            tap1 = np.sum(chan1[target_time_idxs]) / np.sum(target_time_idxs)
            tap2 = np.sum(chan2[target_time_idxs]) / np.sum(target_time_idxs)
            i.To('../chan1')
            i.Set('key', u'Channel 1 TAP = ' + '{0:.1f}'.format(tap1))
            i.To('../chan2')
            i.Set('key', u'Channel 2 TAP = ' + '{0:.1f}'.format(tap2))
            i.To('../../middle_graph/x')
            cur_min = i.Get('min')
            i.To('../window')
            i.Set('xPos', (target_time-cur_min)/20.0)
        elif graph_to_adjust == 'middle_graph':
            i.To('/page1/grid1/middle_graph/x')
            i.Set('min', float(target_time - 10.0))
            i.Set('max', float(target_time + 10.0))
            i.To('../../bottom_graph/window')
            i.Set('xPos', target_time/self.max_time)
