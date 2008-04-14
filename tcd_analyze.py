#!/usr/bin/env python

# tcd_analyze.py
# for processing the transcranial doppler data
# Matt McCormick (thewtex) <matt@mmmccormick.com>
# 2008 March 15

from pylab import *

import os
import glob



# adjusted from /usr/share/doc/matplotlib-0.91.2/examples/clippedline.py
class ClippedLine(Line2D):
    """
    Clip the xlimits to the axes view limits -- this example assumes x is sorted
    """

    def __init__(self, ax, *args, **kwargs):
        Line2D.__init__(self, *args, **kwargs)
        self.ax = ax


    def set_data(self, *args, **kwargs):
        Line2D.set_data(self, *args, **kwargs)
        self.xorig = npy.array(self._x)
        self.yorig = npy.array(self._y)

    def draw(self, renderer):
        xlim = self.ax.get_xlim()

        ind0, ind1 = npy.searchsorted(self.xorig, xlim)
        self._x = self.xorig[ind0:ind1]
        self._y = self.yorig[ind0:ind1]

        Line2D.draw(self, renderer)



class ExtensionError(Exception):
  """Exception raised if a file does not have the expected extension."""

  def __init__(self, filename, extension):
    self.filename = filename
    self.extension = extension

  def __str__(self):
    return 'the filename, %s, does not have the anticipated extension, %s' % (self.filename, self.extension)





class TCDAnalyze:
  """Process a trancranial doppler file.

  Create figures and save them.
  
  *Parameters*:
    
      * filename_prefix: [qualified] filename prefix, e.g. 'nla168'
      
    """

  def __init__(self, filename_prefix):
    # argument checking
    if (glob.glob(filename_prefix + '.tw*') == []) and (glob.glob(filename_prefix + '.td*') == []) :
	e = ExtensionError( filename_prefix, '.tw* or .td*')
	raise e

    ## [qualified] filename prefix, e.g. 'nla168'
    self._filename_prefix = filename_prefix

    ## set containing #'s in filename_prefix + .tx#
    self._x_set = set()
    ## set containing #'s in filename_prefix + .tw#
    self._w_set = set()
    ## set containing #'s in filename_prefix + .td#
    self._d_set = set()

    prefixes = ['.tx', '.tw', '.td']
    for prefix in prefixes:
      for file in glob.glob(filename_prefix + prefix + '*'):
	if prefix == '.tx':
          self._x_set.add( file[ file.rindex( prefix )+3: ] )
	elif prefix == '.tw':
          self._w_set.add( file[ file.rindex( prefix )+3: ] )
	elif prefix == '.td':
          self._d_set.add( file[ file.rindex( prefix )+3: ] )
	else:
	  e = ExtensionError( 'unexpected, unknown extension, ' + prefix )
	  raise e
	  


    def __parse_metadata(metadata_file):
      f = open(metadata_file, 'r')

      metadata = {'patient_name':'unknown patient', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000, 'start_time':'00:00:00', 'hits':[]}
      
      lines = f.readlines()
      for i in xrange(len(lines)):
	lis = lines[i].split()
	if lis[1] == 'HIT':
	  ts = lis[3].split(':')
	  metadata['hits'].append( (int(lis[0]), lis[2], lis[3] ) ) 
        elif ( lis[2] == 'NAME:' ):
	  metadata['patient_name'] = lis[3]
	elif ( lis[2] == 'PRF' ):	
	  metadata['prf'] = int(lis[3])
	elif ( lis[2] == 'SAMPLE_F' ):	
	  metadata['sample_freq'] = int(lis[3])/10
	elif ( lis[2] == 'FDOP1' ):	
	  metadata['doppler_freq_1'] = int(lis[3])
	elif ( lis[2] == 'FDOP2' ):	
	  metadata['doppler_freq_2'] = int(lis[3])
	elif lis[1] == 'START' :
	  metadata['start_time'] = lis[2] 

      f.close()

      return metadata

    ## default metadata -- used if a '.tx#' file does not exist
    self._default_metadata = {'patient_name':'unknown patient', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000, 'start_time':'00:00:00', 'hits':[]}

    ## metadata extracted from the '.tx*' files
    self._metadata = dict()
    for file in self._x_set:
      self._metadata[file] = __parse_metadata(self._filename_prefix + '.tx' + file)
  



  
  def _read_w(self, w_set=[]):
    """Read the 'filename_prefix.tw*' (doppler max velocity envelope) files.

    *Parameters*:
      w_set:
	subset of the self._w_set to read, defaults to the entire set

	"""

    if w_set == []:
      w_set = self._w_set

    ## doppler data
    self._w_data = dict()

    samp_per_segment = 64
    bytes_per_sample = 2
    channels = 2
    tcd_dtype= 'int16'


    for file in w_set:
      filename = self._filename_prefix + '.tw' + file 
      f = open(filename, 'rb')
      f_size = os.path.getsize(filename)
      print 'Reading ', filename
  
      segments = f_size / ( samp_per_segment * bytes_per_sample * channels )
  
      chan1 = array([], dtype=tcd_dtype)
      chan2 = array([], dtype=tcd_dtype)
      data  = zeros((samp_per_segment), dtype=tcd_dtype)
      for seg in xrange(segments):
        data = fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
        chan1 = concatenate((chan1, data.copy()) )
        data = fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
        chan2 = concatenate((chan2, data.copy()) )


      chan1 = chan1.astype(float) / 2.0**11 * self._default_metadata['prf']/2.0 *154000.0 / self._default_metadata['doppler_freq_1']/10**3
      chan2 = chan2.astype(float) / 2.0**11 * self._default_metadata['prf']/2.0 *154000.0 / self._default_metadata['doppler_freq_1']/10**3
      self._w_data[file] = (chan1, chan2)

      f.close()
  
  


  def plot_w_data(self, w_set=[], saveit=True, showit=False):
    """Plot the 'w' file max velocity envelope data.
    
    *Parameters*:
      w_set:
	subset of the self._w_set to read, defaults to the entire set

      saveit:
	whether or not to save the plot to a file in the _file_prefix location

      showit:
	whether or not to show the plot in a GUI on screen

    """
    if w_set == []:
      w_set = self._w_set

    def onpick_adjust_xaxis( event ):
      """Adjust the view of the top subplot"""
      fig = gcf()
      ax = fig.get_axes()
      a = ax[0]
      a.set_xlim( event.mouseevent.xdata - 2.5, event.mouseevent.xdata + 2.5 )
      draw()
      
    self._read_w(w_set)


    for file in w_set:
      print 'Plotting ', self._filename_prefix + '.tw' + file
      if self._metadata.has_key(file):
	metadata = self._metadata[file]
      else:
	metadata = self._default_metadata

      (chan1, chan2) = self._w_data[file]
      sample_freq = float( metadata['sample_freq'])
      time = arange( len(chan1) ) / sample_freq


      fig = figure(int(file))

      chansmax = max([chan1.max(), chan2.max()]) 
      chansmin = min([chan1.min(), chan2.min()])
      hity = chansmax / 3.0
      hityinc = chansmax/11.0

      ax1 = fig.add_subplot(211)
      ax1.set_ylim(chansmin, chansmax)
      chan1_line1 = ClippedLine(ax1, time, chan1, color='r', ls='-',  label='Channel 1', markersize=0 )
      chan2_line1 = ClippedLine(ax1, time, chan2, color=(0.3, 1.0, 0.3), markersize=0, label='Channel 2', antialiased=True )
      ax1.add_line(chan1_line1)
      ax1.add_line(chan2_line1)
      for i in metadata['hits']:
	if hity > chansmax* 2.0/3.0:
	  hity = chansmax/ 3.0
	else:
	  hity = hity + hityinc
        line = ClippedLine(ax1, [float(i[0]) / sample_freq], [hity], color=(0.9, 0.9, 1.0), marker='o', markeredgewidth=2, markeredgecolor='blue')
	ax1.add_line(line)
        text( float(i[0]) / sample_freq, hity+hityinc/2.0, i[1] + ' ' + i[2], color=(0.9, 0.9, 1.0),  horizontalalignment='center', fontsize=12 )
      xlim( (0.0, 5.0) )
      l = legend( )
      lf = l.get_frame()
      lf.set_facecolor( (0.5, 0.5, 0.5) )

      title( metadata['patient_name'] )
      ylabel('Velocity [cm/s]')
      grid(b=True, color=(0.3, 0.3, 0.3))

      ax2 = fig.add_subplot(212)
      ax2.set_picker(True)
      plot( time, chan1, 'r-',  label='Channel 1', antialiased=False )
      plot( time, chan2, color=(0.3, 1.0, 0.3), markersize=0, label='Channel 2', antialiased=False )
      chansmax = max([max(chan1), max(chan2)]) 
      hity = chansmax / 3.0
      for i in metadata['hits']:
	if hity > chansmax* 2.0/3.0:
	  hity = chansmax/ 3.0
	else:
	  hity = hity + hityinc
	plot( [float(i[0]) / sample_freq], [hity], color=(0.9, 0.9, 1.0), marker='o', markeredgewidth=2, markeredgecolor='blue')
      ylabel('Velocity [cm/s]')
      xlabel('Time [sec] + ' + metadata['start_time'])

      if saveit:
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.png' )
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.eps' )
      if showit:
	fig.canvas.mpl_connect('pick_event', onpick_adjust_xaxis)
	show()
  



  ## @warning this is incomplete, and possibly incorrect
  def _read_d(self,  d_set=[]):
    """Read the 'filename_prefix.td*' (doppler spectrum) files.

    *Parameters*:
      d_set:
	subset of the self._d_set to read, defaults to the entire set

    """
    if d_set == []:
      d_set = self._d_set

    ## doppler data
    self._d_data = dict()

    samp_per_segment = 9216
    bytes_per_sample = 2
    channels = 2
    # samples between data subsegments (see 'while' loop below)
    subsegment_separator = 41472
    # samples between data supersegments (see 'while' loop below)
    supersegment_separator = 128
    start_sample = 22016
    spectrum_points = 32

    tcd_dtype= 'int16'


    for file in d_set:
      filename = self._filename_prefix + '.td' + file 
      f = open( filename, 'rb' )
      f_size = os.path.getsize(filename)
      print 'Reading ', filename
  
  
      chan1 = array([], dtype=tcd_dtype)
      chan2 = array([], dtype=tcd_dtype)
      data  = zeros((samp_per_segment), dtype=tcd_dtype)
      index = start_sample
      segment = 0
      while( (index + samp_per_segment*2)*bytes_per_sample < f_size ):
	f.seek(index*bytes_per_sample)
        data = fromfile(f, dtype=tcd_dtype, count=samp_per_segment)

	segment = segment + 1
	if segment % 2 == 1:
	  index = index + subsegment_separator
	  chan1 = concatenate((chan1, data.copy()) )
	else:
	  index = index + subsegment_separator + supersegment_separator
	  chan2 = concatenate((chan2, data.copy()) )

      chan1.resize( (chan1.shape[0] / spectrum_points, spectrum_points) )
      chan2.resize( (chan2.shape[0] / spectrum_points, spectrum_points) )

      chan1 = chan1.transpose()
      chan2 = chan2.transpose()

      self._d_data[file] = (chan1, chan2)

      f.close()



  ## @warning this is incomplete, and possibly incorrect
  def plot_d_data(self, d_set=[], saveit=True, showit=False):
    """Plot the 'd' file doppler data.
    
    *Parameters*:
      d_set:
	subset of the self._d_set to read, defaults to the entire set

      saveit:
	whether or not to save the plot to a file in the _file_prefix location

      showit:
	whether or not to show the plot in a GUI on screen

    """
    if d_set == []:
      d_set = self._d_set

    self._read_d(d_set)

    for file in d_set:
      if self._metadata.has_key(file):
	metadata = self._metadata[file]
      else:
	metadata = self._default_metadata

      (chan1, chan2) = self._d_data[file]
      chan1 = array(chan1, dtype='float')
      chan2 = array(chan2, dtype='float')

      figure(int(file))
      subplot(211)
      #imshow( chan1, aspect='auto', origin='lower', extent=(0.0, float(len(chan1))/metadata['sample_freq'], -1, 1) )
      imshow( chan1, aspect='auto' )
      title( metadata['patient_name'] )
      subplot(212)
      imshow( chan2, aspect='auto' )

      if saveit:
	savefig( self._filename_prefix + '_doppler_' + file + '.png' )
      if showit:
	show()


  def get_d_set(self):
    """Return the set containing #'s in filename_prefix + .td#."""
    return self._d_set
  
  def get_w_set(self):
    """Return the set containing #'s in filename_prefix + .tw#."""
    return self._w_set

  def get_metadata(self):
    """Return metadata extracted from the '.tx*' files.
      
      metadata has the following dictionary keys:
	patient_name:
	  
	prf:
	  pulse repetition frequency [Hz]
	  
	sample_freq:
	  velocity curve sampling frequency [Hz]
	  
	doppler_freq_1:
	  excitation frequency of channel 1 [kHz]
	  
	doppler_freq_2:
	  excitation frequency of channel 2 [kHz]

	start_time:
	  clock time of acquisition start

	hits:
	  list with the detected hits.  Each entry is a tuple with the sample point, hit dB, and hit time
	  """
    return self._metadata

  def get_d_data(self, d_set=[]):
    """Return the 'd' file doppler data.
    *Parameters*:
      d_set:
	subset of the self._d_set to read, defaults to the entire set
	"""
    if d_set == []:
      d_set = self._d_set
    self._read_d(d_set)
    return self._d_data

  def get_w_data(self, w_set=[]):
    """Return the 'w' file average velocity data.
    *Parameters*:
      w_set:
	subset of the self._w_set to read, defaults to the entire set
	"""
    if w_set == []:
      w_set = self._w_set
    self._read_w(w_set)
    return self._w_data





    
	

# if running as script
if __name__ == "__main__":
      import sys
      for arg in sys.argv[1:] :
	 t = TCDAnalyze(arg)
	 t.plot_w_data(showit=True)


