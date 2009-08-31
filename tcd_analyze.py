#!/usr/bin/env python
## @package tcd_analyze
#   for processing the transcranial doppler data generated on a DWL Multidop L2
#
#   @author Matt McCormick (thewtex) <matt@mmmccormick.com>
#   @date created 2008 March 15

import os
import glob

import scipy.signal
import numpy as npy

from optparse import OptionParser


class TCDAnalyze:
  """Process a trancranial doppler file.

  Create figures and save them.
  
  *Parameters*:
    
      * filename_prefix: [qualified] filename prefix, e.g. 'nla168'
      
      * use_centisec_clock:
	whether to use the 1/100 sec clock recordings from the hits data file, or the hr:min:sec, values instead.  On our machine, we found that the there was a large discrepency as for long time period recordings
      
    """


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
    figtext( 0.5, 0.25, 'Click here to save\n the TAP (Time-Averaged Peak Velocity)\n from the top plot in the file', label='tap_save', linespacing=1.6, figure=fig_info, va='center', ha='center', backgroundcolor=(0.1,0.1,0.2), color='w', alpha=0.8, visible='True', picker=True, fontsize=14.0)
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
	if self.use_centisec_clock:
	  hittime= float(i[0]) / sample_freq
	else:
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
	  # these don't work properly -- and extra arrows apparently randomly
	  #arrow( hittime, hity, 1.0, 0.0, alpha=0.6, facecolor=hit_c, edgecolor=hit_mec, width=1.0,  head_starts_at_zero=True, head_width=4.0, head_length=0.1 )
	  #arrow( hittime, hity, -1.0, 0.0, alpha=0.6, facecolor=hit_c, edgecolor=hit_mec, width=1.0,  head_starts_at_zero=False, head_width=4.0, head_length=0.1 )

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





    
	

