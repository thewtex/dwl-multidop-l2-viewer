import os

import numpy

from dwl_multidop_exceptions import *
from fileparsing.dwl_multidop_tx import TX
from fileparsing.dwl_multidop_tw import TW

## 
# @brief load the .TW? and .TX? and place the data in the given CommandInterface
class DWLMultidopLoadFile():
    def __init__(self, interface, main_window):
        self.interface = interface
        self.main_window = main_window

## 
# @brief read in the data from the .tx and tw files
# 
# @param file_prefix prefix to the files
# 
# @return  maximum time in the dataset
    def load_file(self, file_prefix):
        self._find_filepath(file_prefix)
        self.main_window.statusBar().clearMessage()
        self.main_window.statusBar().insertWidget(0, self.main_window.loading_label)
        self.main_window.statusBar().insertWidget(1, self.main_window.loading_progress_bar)
        self.main_window.loading_label.show()
        self.main_window.loading_progress_bar.show()
        self._load_tx_file()
        self._load_tw_file()
        self.main_window.statusBar().removeWidget(self.main_window.loading_label)
        self.main_window.statusBar().removeWidget(self.main_window.loading_progress_bar)
        max_time = self._import_velocity()
        self._import_hits_marks()

        return max_time

    def _find_filepath(self, file_prefix):
        """find the filepath"""
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

        self.tx_file = tx_file
        self.tw_file = tw_file

        self.main_window.setWindowTitle('DWL Multidop L2 Viewer - ' + tx_file)

    def _load_tx_file(self):
        self.main_window.loading_label.setText('Loading metadata .TX file...')
        self.tx = TX(self.tx_file, self.main_window.loading_progress_bar)

    def _load_tw_file(self):
        self.main_window.loading_label.setText('Loading velocity data from .TW FILE...')
        self.tw = TW(self.tw_file, self.tx.metadata['prf'], self.tx.metadata['doppler_freq_1'],
                self.tx.metadata['doppler_freq_2'], self.main_window.loading_progress_bar)
        self.main_window.current_subject_label.setText('Current Patient: ' +
                self.tx.metadata['patient_name'])

## 
# @brief import velocity data into the plotting interface
# 
# @return maximum time in the dataset
    def _import_velocity(self):
        i = self.interface
        i.SetData('chan1_vel', self.tw.chan1)
        i.SetData('chan2_vel', self.tw.chan2)
        sample_freq = float(self.tx.metadata['sample_freq'])
        time = numpy.arange(len(self.tw.chan1)) / sample_freq
        i.SetData('time', time)
        return len(self.tw.chan1) / sample_freq

## 
# @brief import hits data and marks into plot
# 
# @return 
    def _import_hits_marks(self):
        i = self.interface
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
