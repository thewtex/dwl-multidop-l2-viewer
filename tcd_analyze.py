#!/usr/bin/env python

# tcd_analyze.py
# for processing the transcranial doppler data
# Matt McCormick (thewtex) <matt@mmmccormick.com>
# 2008 March 15

from pylab import *
import os
import glob






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
    if (glob.glob(filename_prefix + '.tw*') == []) & (glob.glob(filename_prefix + '.td*') == []) :
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

      metadata = {'patient_name':'unknown patient', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000}
      
      lines = f.readlines()
      for i in xrange(len(lines)):
	if ( lines[i].split()[2] == 'NAME:' ):
	  metadata['patient_name'] = lines[i].split()[3]
	elif ( lines[i].split()[2] == 'PRF' ):	
	  metadata['prf'] = int(lines[i].split()[3])
	elif ( lines[i].split()[2] == 'SAMPLE_F' ):	
	  metadata['sample_freq'] = int(lines[i].split()[3])/10
	elif ( lines[i].split()[2] == 'FDOP1' ):	
	  metadata['doppler_freq_1'] = int(lines[i].split()[3])
	elif ( lines[i].split()[2] == 'FDOP2' ):	
	  metadata['doppler_freq_2'] = int(lines[i].split()[3])

      f.close()

      return metadata

    ## default metadata -- used if a '.tx#' file does not exist
    self._default_metadata = {'patient_name':'unknown patient', 'prf':6000, 'sample_freq':100, 'doppler_freq_1':2000, 'doppler_freq_2':2000}

    ## metadata extracted from the '.tx*' files
    self._metadata = dict()
    for file in self._x_set:
      self._metadata[file] = __parse_metadata(self._filename_prefix + '.tx' + file)
  



  
  def _read_w(self, w_set=[]):
    """Read the 'filename_prefix.tw*' (doppler average velocity waveform) files.

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


      chan1 = chan1.astype(float) / 2.0**11 * self._default_metadata['prf']/2.0 *154000.0 / self._default_metadata['doppler_freq_1']/2.0/10**3
      chan2 = chan2.astype(float) / 2.0**11 * self._default_metadata['prf']/2.0 *154000.0 / self._default_metadata['doppler_freq_1']/2.0/10**3
      self._w_data[file] = (chan1, chan2)

      f.close()
  
  


  def plot_w_data(self, w_set=[], saveit=True, showit=False):
    """Plot the 'd' file doppler data.
    
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

    for file in w_set:
      print 'Plotting ', self._filename_prefix + '.tw' + file
      if self._metadata.has_key(file):
	metadata = self._metadata[file]
      else:
	metadata = self._default_metadata

      (chan1, chan2) = self._w_data[file]
      time = arange( len(chan1) ) / float( metadata['sample_freq'] )

      figure(int(file))
      if time[-1] > 5.0:
	subplot(211)
        maxind = where( time < 5.0 )[0][-1]
        plot( time[:maxind], chan1[:maxind], 'r-',  label='Channel 1' )
        plot( time[:maxind], chan2[:maxind], 'g-', label='Channel 2' )
	title( metadata['patient_name'] + ' first five seconds' )
        ylabel('Velocity [cm/s]')
	subplot(212)
      plot( time, chan1, 'r-',  label='Channel 1' )
      plot( time, chan2, 'g-', label='Channel 2' )
      legend( )
      ylabel('Velocity [cm/s]')
      xlabel('Time [sec]')
      title( metadata['patient_name'] )

      if saveit:
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.png' )
	savefig( self._filename_prefix + '_velocity_curve_' + file + '.eps' )
      if showit:
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
	  velocity curve sampleing frequency [Hz]
	  
	doppler_freq_1:
	  excitation frequency of channel 1 [kHz]
	  
	doppler_freq_2:
	  excitation frequency of channel 2 [kHz]"""
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
	 t.plot_w_data()


