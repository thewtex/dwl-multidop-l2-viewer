#!/usr/bin/env python
## @package tcd_analyze
#   for processing the transcranial doppler data generated on a DWL Multidop L2
#
#   @author Matt McCormick (thewtex) <matt@mmmccormick.com>
#   @date created 2008 March 15

from pylab import *

import os
import glob

import scipy.signal
import numpy as npy

from optparse import OptionParser



# adjusted from /usr/share/doc/matplotlib-0.91.2/examples/clippedline.py
class ClippedLine(Line2D):
    """
    Clip the xlimits to the axes view limits -- this example assumes x is sorted
    """

    def __init__(self, ax, *args, **kwargs):
        Line2D.__init__(self, *args, **kwargs)
	## axes the line is plotted in
        self.ax = ax


    def set_data(self, *args, **kwargs):
        Line2D.set_data(self, *args, **kwargs)
	## what is plotted pre-clipping
        self._xorig = npy.array(self._x)
	## what is plotted pre-clipping
        self._yorig = npy.array(self._y)

    def draw(self, renderer):
        xlim = self.ax.get_xlim()

        ind0 = npy.searchsorted(self._xorig, xlim[0], side='left')
        ind1 = npy.searchsorted(self._xorig, xlim[1], side='right')
        self._x = self._xorig[ind0:ind1]
        self._y = self._yorig[ind0:ind1]

        Line2D.draw(self, renderer)



class DecimatedClippedLine(Line2D):
  """
  Decimate and clip the data so it does not take as long to plot.  Assumes data is sorted and equally spaced.
  """

  def __init__(self, ax, *args, **kwargs):
    """
    *Parameters*:
      ax:
	axes the line is plotted on

      *args, **kwargs:
	Line2D args

    """
    Line2D.__init__(self, *args, **kwargs)
    ## axes the line is plotted in
    self.ax = ax


  def set_data(self, *args, **kwargs):
    Line2D.set_data(self, *args, **kwargs)
    ## data preclipping and decimation
    self._xorig = npy.array(self._x)
    ## data pre clipping and decimation
    self._yorig = npy.array(self._y)


  def draw(self, renderer):
    bb = self.ax.get_window_extent()
    width = bb.width()

    xlim = self.ax.get_xlim()
    ind0 = npy.searchsorted(self._xorig, xlim[0], side='left')
    ind1 = npy.searchsorted(self._xorig, xlim[1], side='right')

    self._x = self._xorig[ind0:ind1]
    self._y = self._yorig[ind0:ind1]

    if self.ax.get_autoscale_on():
      ylim = self.ax.get_ylim()
      self.ax.set_ylim( min([ylim[0], self._y.min()]), max([ylim[1], self._y.max()]) )

    if width / float( ind1 - ind0 ) < 0.4: # if number of points to plot is much greater than the pixels in the plot
      b, a = scipy.signal.butter(5, width / float( ind1 - ind0 ))
      filty = scipy.signal.lfilter( b, a, self._y )

      step = int( float( ind1 - ind0 ) / width )
      self._x = self._x[::step]
      self._y = filty[::step]

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
      
      * use_centisec_clock:
	whether to use the 1/100 sec clock recordings from the hits data file, or the hr:min:sec, values instead.  On our machine, we found that the there was a large discrepency as for long time period recordings
      
    """

  def __init__(self, filename_prefix, use_centisec_clock=False):
    # argument checking
    if (glob.glob(filename_prefix + '.TW[0-9]') == []) and (glob.glob(filename_prefix + '.TD[0-9]') == []) :
	e = ExtensionError( filename_prefix, '.TW* or .TD*')
	raise e


    self.use_centisec_clock = use_centisec_clock


    ## [qualified] filename prefix, e.g. 'nla168'
    self._filename_prefix = filename_prefix

    ## set containing #'s in filename_prefix + .TX#
    self._x_set = set()
    ## set containing #'s in filename_prefix + .TW#
    self._w_set = set()
    ## set containing #'s in filename_prefix + .TD#
    self._d_set = set()

    prefixes = ['.TX', '.TW', '.TD']
    for prefix in prefixes:
      for file in glob.glob(filename_prefix + prefix + '[0-9]'):
	if prefix == '.TX':
          self._x_set.add( file[ file.rindex( prefix )+3: ] )
	elif prefix == '.TW':
          self._w_set.add( file[ file.rindex( prefix )+3: ] )
	elif prefix == '.TD':
          self._d_set.add( file[ file.rindex( prefix )+3: ] )
	else:
	  e = ExtensionError( 'unexpected, unknown extension, ' + prefix )
	  raise e
	  


    def __parse_metadata(metadata_file):
      f = open(metadata_file, 'r')

      metadata = {'patient_name':'unknown patient', 'exam_date':'00-00-00', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000, 'start_time':'00:00:00', 'hits':[], 'marks':[] }
      
      lines = f.readlines()
      for i in xrange(len(lines)):
	lis = lines[i].split()
	if lis[1] == 'HIT':
	  metadata['hits'].append( (int(lis[0]), lis[2], lis[3], 'Unchecked' ) ) 
	if lis[1][:3] == 'MRK':
	  metadata['marks'].append( (int(lis[0]), lis[1],  lis[2], lis[4] ) ) 
        elif ( lis[2] == 'NAME:' ):
	  metadata['patient_name'] = lines[i][lines[i].rfind('NAME:')+6:-1]
        elif ( lis[2] == 'EXAM:' ):
	  metadata['exam_date'] = lis[3]
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

    ## default metadata -- used if a '.TX#' file does not exist
    self._default_metadata = {'patient_name':'unknown patient', 'exam_date':'00-00-00', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000, 'start_time':'00:00:00', 'hits':[], 'marks':[]}

    ## metadata extracted from the '.TX*' files
    self._metadata = dict()
    for file in self._x_set:
      self._metadata[file] = __parse_metadata(self._filename_prefix + '.TX' + file)

    ## default figure size
    self._default_fig_size = (9,10)

    ## current trial being processed
    self._current_trial = '0'

  


  
  def _read_w(self, w_set=[]):
    """Read the 'filename_prefix.TW*' (doppler max velocity envelope) files.

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
      filename = self._filename_prefix + '.TW' + file 
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
  
  def _write_hits(self):
      file = self._current_trial
      if self._metadata.has_key(file):
	metadata = self._metadata[file]
      else:
	metadata = self._default_metadata
      outfile = self._filename_prefix + '_' + file + '_' + metadata['patient_name'].replace(' ','_') + '_' + 'hits.csv' 
      
      print 'Saving ', outfile

      f = open(outfile, 'w')
      f.write(metadata['patient_name'] + ', trial ' + file + '\n')
      f.write('Examined on ' + metadata['exam_date'] + '\n')
      from datetime import date
      today = date.today()
      f.write('Analyzed on ' + today.isoformat() + '\n')
      asses_l = []
      for hit in metadata['hits']:
	asses_l.append(hit[3])
      f.write( 'Total hits: ' + str(len(metadata['hits'])) + '\n')
      f.write( 'Affirmed: ' + str(asses_l.count('Affirmed')) + '\n' )
      f.write( 'Denied: ' + str(asses_l.count('Denied')) + '\n' )
      f.write( 'Unchecked: ' + str(asses_l.count('Unchecked')) + '\n')


      f.write('Hit time, Hit level above background, Assessment\n')
      for hit in metadata['hits']:
	f.write( str(hit[2]) + ',' + str(hit[1]) + ',' + hit[3] + '\n' )

      f.close()

    
  


  def _onpick_adjust_w_xaxis(self, event ):
    """Adjust the view of the top subplot"""
    if not isinstance(event.artist, matplotlib.axes.Subplot):
      return
    fig = gcf()
    
    ax = fig.get_axes()

    ax_top = ax[0]
    ax_mid = ax[1]

    ax_picked = event.artist
    
    for i in xrange( len(self._w_ax2s) ):
      if ax_picked == self._w_ax2s[i]:
	ax_top.set_xlim( event.mouseevent.xdata - 2.5, event.mouseevent.xdata + 2.5 )
	rect = self._w_ax2rects[i]
	rect.set_x( event.mouseevent.xdata - 2.5 )
      elif ax_picked == self._w_ax3s[i]:
	ax_mid.set_xlim( event.mouseevent.xdata - 50.0, event.mouseevent.xdata + 50.0 )
	rect = self._w_ax3rects[i]
	rect.set_x( event.mouseevent.xdata - 50.0 )

    draw()



  def _onpick_select_hit(self, event ):
    """Change the color and the label of the hit"""
    if not isinstance(event.artist, ClippedLine):
      return

    fig = gcf()
    file = fig.get_label()
    if self._metadata.has_key(file):
	metadata = self._metadata[file]
    else:
	metadata = self._default_metadata
    sample_freq = float( metadata['sample_freq'])

    chosen_x =  event.artist.get_xdata()
    chosen_x = chosen_x[0]
    # colors
    affirmed_c='#FFAA18'
    affirmed_mec='#86590D'
    denied_c='#CC19DC'
    denied_mec='#550A5C'

    num_hits = len(metadata['hits'])
    i = 0
    located = False
    while ( i < num_hits ) and (not located):
      if self.use_centisec_clock:
	  hittime= float(metadata['hits'][i][0]) / sample_freq
      else:
	  #startime[0] = hour
	  #starttime[1] = minute
	  #starttime[2] = second
          starttime = [ int(x) for x in metadata['start_time'].split(':') ]
	  curtime = [ int(x) for x in metadata['hits'][i][2].split(':') ]
  	  # deal with clock wrap around, assuming 
  	  # the examine takes less than 24 hrs :P
	  if curtime[0] >=  starttime[0] :
  	    sep_hours = (curtime[0]-starttime[0])*3600
	  else:
	    sep_hours = (24 - starttime[0] + curtime[0])*3600
	  # time offset from start in seconds
	  hittime = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
	  hittime = float( hittime )
      if hittime == chosen_x:
	located = True
	if event.mouseevent.button == 1:
	  self._metadata[file]['hits'][i] = metadata['hits'][i][:3] + ('Affirmed',)
	  event.artist.set_color(affirmed_c)
	  event.artist.set_markeredgecolor(affirmed_mec)
	else:
	  self._metadata[file]['hits'][i] = metadata['hits'][i][:3] + ('Denied',)
	  event.artist.set_color(denied_c)
	  event.artist.set_markeredgecolor(denied_mec)
      i = i+1
    if not located:
      raise ValueError
    draw()



  def _save_or_close(self, event):
    """write to the output file and close the application"""
    fig = gcf()
    self._current_trial = fig.get_label()
    if event.artist.get_label() ==  'save':
      self._write_hits()
    else:
      close('all')


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

      
    self._read_w(w_set)


    # informational window
    fig_info = figure(10, figsize=(4.3,5.4), facecolor=(0.2,0.2,0.2))

    instructions='Instructions:\n--------------------\nData Navigation:\nbottom plot: all data\nmiddle plot: 100 sec selected from bottom\ntop plot: 5 sec selected from middle\nbuttons on bottom: saving and additional zooming\n----------\nHits Selection:\n left click to mark Affirm\n right click to mark Deny\n----------'

    figtext( 0.5, 0.3, instructions, figure=fig_info, va='bottom', ha='center', backgroundcolor='k', color='w', visible='True', fontsize=12.0, linespacing=1.8)
    figtext( 0.5, 0.15, 'Click here to save\n current plot\'s picks', label='save', linespacing=1.6, figure=fig_info, va='center', ha='center', backgroundcolor=(0.1,0.1,0.2), color='w', alpha=0.8, visible='True', picker=True, fontsize=14.0)
    figtext( 0.5, 0.05, 'Click here when finished', figure=fig_info, label='finish', va='top', ha='center', backgroundcolor=(0.1,0.1,0.2), color='w', alpha=0.8, visible='True', picker=True, fontsize=14.0)

    fig_info.canvas.mpl_connect('pick_event',self._save_or_close)





    ## bottom subplot (scout plot) for velocity envelope figure
    #  views the entire signal
    self._w_ax3s = []
    ## middle subplot (scout plot) for velocity envelope figure
    #  views a shorter duration segment
    self._w_ax2s = []
    ## indicator rectangles in self._w_ax3s
    self._w_ax3rects = []
    ## indicator rectangles in self._w_ax2s
    self._w_ax2rects = []
    for file in w_set:
      print 'Plotting ', self._filename_prefix + '.TW' + file
      self._current_trial = file
      if self._metadata.has_key(file):
	metadata = self._metadata[file]
      else:
	metadata = self._default_metadata

      (chan1, chan2) = self._w_data[file]
      sample_freq = float( metadata['sample_freq'])
      time = arange( len(chan1) ) / sample_freq

      fig = figure(int(file), figsize=self._default_fig_size)
      fig.set_label(file)

      chansmax = max([chan1.max(), chan2.max()]) 
      chansmin = min([chan1.min(), chan2.min()])
      hity = chansmax / 3.0
      hityinc = chansmax/11.0

      # colors
      hit_c=(0.6,0.6,1.0)
      hit_mec='blue'
      mark1_c = (0.4, 0.4, 0.8)
      mark2_c = (0.2, 0.8, 0.2)
      markelse_c = (0.8,0.2,0.2)
      def plot_hits(ax, hity, chansmax):
        """Plot hits as points on the given axis."""
  
        for i in metadata['hits']:
	  if hity > chansmax* 2.0/3.0:
	   hity = chansmax/ 3.0
	  else:
	   hity = hity + hityinc
	  
	  if self.use_centisec_clock:
	    hittime = float(i[0]) / sample_freq
	  else:
      	  #### use the hr:min:sec recording
	    #startime[0] = hour
	    #starttime[1] = minute
	    #starttime[2] = second
            starttime = [ int(x) for x in metadata['start_time'].split(':') ]
	    curtime = [ int(x) for x in i[2].split(':') ]
      	    # deal with clock wrap around, assuming 
      	    # the examine takes less than 24 hrs :P
            if curtime[0] >=  starttime[0] :
      	      sep_hours = (curtime[0]-starttime[0])*3600
      	    else:
      	      sep_hours = (24 - starttime[0] + curtime[0])*3600
      	    # time offset from start in seconds
      	    hittime = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
      	    hittime = float( hittime )

          line = ClippedLine(ax, [ hittime ], [hity], color=hit_c , marker='o', markeredgewidth=2, markeredgecolor=hit_mec, picker=7.0)
  	  ax.add_line(line)

	for i in metadata['marks']:
	  if hity > chansmax* 2.0/3.0:
	   hity = chansmax/ 3.0
	  else:
	   hity = hity + hityinc
	  
	  if self.use_centisec_clock:
	    hittime = float(i[0]) / sample_freq
	  else:
      	  #### use the hr:min:sec recording
	    #startime[0] = hour
	    #starttime[1] = minute
	    #starttime[2] = second
            starttime = [ int(x) for x in metadata['start_time'].split(':') ]
	    curtime = [ int(x) for x in i[2].split(':') ]
      	    # deal with clock wrap around, assuming 
      	    # the examine takes less than 24 hrs :P
            if curtime[0] >=  starttime[0] :
      	      sep_hours = (curtime[0]-starttime[0])*3600
      	    else:
      	      sep_hours = (24 - starttime[0] + curtime[0])*3600
      	    # time offset from start in seconds
      	    hittime = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
      	    hittime = float( hittime )

	  if i[3] == 'MARK1':
	    mark_c = mark1_c
	  elif i[3] == 'MARK2':
	    mark_c = mark2_c
	  else:
	    mark_c = markelse_c
	  text( hittime, hity, i[1] + ' ' + i[2], color=mark_c, axes=ax,  horizontalalignment='center', fontsize=12 )
  	  ax.add_line(line)



      
      # plot top, close examination subplot
      ax1 = fig.add_subplot(311)
      ax1.set_ylim(chansmin, chansmax)
      chan1_line1 = ClippedLine(ax1, time, chan1, color='r', ls='-',  label='Channel 1', markersize=0 )
      chan2_line1 = ClippedLine(ax1, time, chan2, color=(0.3, 1.0, 0.3), markersize=0, label='Channel 2', antialiased=True )
      ax1.add_line(chan1_line1)
      ax1.add_line(chan2_line1)
      plot_hits(ax1, hity, chansmax)
      for i in metadata['hits']:
	if hity > chansmax* 2.0/3.0:
	  hity = chansmax/ 3.0
	else:
	  hity = hity + hityinc
	#if self.use_centisec_clock:
	  hittime2= float(i[0]) / sample_freq
	#else:
	  #startime[0] = hour
	  #starttime[1] = minute
	  #starttime[2] = second
          starttime = [ int(x) for x in metadata['start_time'].split(':') ]
	  curtime = [ int(x) for x in i[2].split(':') ]
    	  # deal with clock wrap around, assuming 
    	  # the examine takes less than 24 hrs :P
          if curtime[0] >=  starttime[0] :
    	      sep_hours = (curtime[0]-starttime[0])*3600
    	  else:
    	    sep_hours = (24 - starttime[0] + curtime[0])*3600
    	  # time offset from start in seconds
    	  hittime = sep_hours + (curtime[1] - starttime[1])*60 + (curtime[2] - starttime[2])
    	  hittime1 = float( hittime )
	  # these don't work properly -- and extra arrows apparently randomly
	  #arrow( hittime, hity, 1.0, 0.0, alpha=0.6, facecolor=hit_c, edgecolor=hit_mec, width=1.0,  head_starts_at_zero=True, head_width=4.0, head_length=0.1 )
	  #arrow( hittime, hity, -1.0, 0.0, alpha=0.6, facecolor=hit_c, edgecolor=hit_mec, width=1.0,  head_starts_at_zero=False, head_width=4.0, head_length=0.1 )
	print hittime2-hittime1

	text( hittime, hity+hityinc/2.0, i[1] + ' ' + i[2], color=hit_c,  horizontalalignment='center', fontsize=12 )
      xlim( (0.0, 5.0) )
      l = legend( )
      lf = l.get_frame()
      lf.set_facecolor( (0.5, 0.5, 0.5) )

      title( metadata['patient_name'] )
      ylabel('Velocity [cm/s]')
      grid(b=True, color=(0.3, 0.3, 0.3))

      # plot middle, medium zoom
      ax2 = fig.add_subplot(312)
      self._w_ax2s.append(ax2)
      ax2.set_picker(True)
      chan1_line2 = ClippedLine(ax2, time, chan1, color='r', ls='-',  markersize=0, label='Channel 1', antialiased=True )
      chan2_line2 = ClippedLine(ax2, time, chan2, color=(0.3, 1.0, 0.3), markersize=0, label='Channel 2', antialiased=True )
      ax2.add_line(chan1_line2)
      ax2.add_line(chan2_line2)
      ax2.set_xlim( 0.0, 20.0 )
      ax2.set_ylim( min([chan1.min(), chan2.min()]), max([chan1.max(), chan2.max()]) )
      # draw the hits
      plot_hits(ax2, hity, chansmax)
      # draw indicator rectangle
      ax2ylim = ax2.get_ylim()
      rect = Rectangle( (0.0, ax2ylim[0]), 5.0, ax2ylim[1] - ax2ylim[0], edgecolor=(0.9,0.9,1.0), lw=1, alpha=0.5)
      ax2.add_artist(rect)
      self._w_ax2rects.append( rect )
      ylabel('Velocity [cm/s]')



      # plot bottom, general overview subplot
      ax3 = fig.add_subplot(313)
      self._w_ax3s.append(ax3)
      ax3.set_picker(True)
      chan1_line2 = DecimatedClippedLine(ax3, time, chan1, color='r', ls='-',  markersize=0, label='Channel 1', antialiased=True )
      chan2_line2 = DecimatedClippedLine(ax3, time, chan2, color=(0.3, 1.0, 0.3), markersize=0, label='Channel 2', antialiased=True )
      ax3.add_line(chan1_line2)
      ax3.add_line(chan2_line2)
      ax3.set_xlim( time.min(), time.max() )
      ax3.set_ylim( min([chan1.min(), chan2.min()]), max([chan1.max(), chan2.max()]) )
      # draw the hits
      plot_hits(ax3, hity, chansmax)
      # draw indicator rectangle
      ax3ylim = ax3.get_ylim()
      rect = Rectangle( (0.0, ax3ylim[0]), 100.0, ax3ylim[1] - ax3ylim[0], edgecolor=(0.9,0.9,1.0), lw=1, alpha=0.5)
      ax3.add_artist(rect)
      self._w_ax3rects.append( rect )
      ylabel('Velocity [cm/s]')
      xlabel('Time [sec] + ' + metadata['start_time'])

      if saveit:
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.png' )
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.eps' )
    if showit:
	fig.canvas.mpl_connect('pick_event', self._onpick_adjust_w_xaxis)
	fig.canvas.mpl_connect('pick_event', self._onpick_select_hit)
	show()
  



  ## @warning this is incomplete, and possibly incorrect
  def _read_d(self,  d_set=[]):
    """Read the 'filename_prefix.TD*' (doppler spectrum) files.

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
      filename = self._filename_prefix + '.TD' + file 
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


  ## @warning this is incomplete, and may be incorrect
  def get_d_set(self):
    """Return the set containing #'s in filename_prefix + .TD#."""
    return self._d_set
  
  def get_w_set(self):
    """Return the set containing #'s in filename_prefix + .TW#."""
    return self._w_set

  def get_metadata(self):
    """Return metadata extracted from the '.TX*' files.
      
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

      usage = """usage: %prog [options] <fileprefix>

<fileprefix> is the filename prefix of the DWL Multidop L2 files.

E.g., if you have 'nla168.TX0' and 'nla168.TW0'
in the current directory <fileprefix> = 'nla168'"""
      parser = OptionParser(usage=usage)

      parser.add_option("-n", "--no-show", help="Do not display the generated plots on screen", dest="showit", action="store_false", default=True)
      parser.add_option("-s", "--save", help="Save the generated plots", dest="saveit", action="store_true", default=False)
      parser.add_option("-t", "--trials", dest="trials", help="Comma separated list of the trials to process, e.g. if you had 'nla168.TX0', 'nla168.TX1', and 'nla168.TX2' and the corresponding '*.TW*' files in the current directory, you issue --trials=1,2 to process only the second and third trials.  Defaults to all trials.", default='[]' )

      options, args = parser.parse_args()

      t = TCDAnalyze(args[0])
      trials = []
      if options.trials != '[]':
	for i in options.trials.split(','):
	  trials.append(i)

      t.plot_w_data(w_set=trials, showit=options.showit, saveit=options.saveit)


