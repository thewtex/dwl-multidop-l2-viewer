#!/usr/bin/env python

# tcd_analyze.py
# for processing the transcranial doppler data
# Matt McCormick (thewtex) <matt@mmmccormick.com>
# 2008 March 15

from pylab import *
import os
import glob



def read_tcd(filename):
  """Read the contents of transcranial doppler nlaXXX.twX file.

  Returns a two element tuple of numpy arrays; one for each channel."""

  f = open(filename, 'rb')


  f_size = os.path.getsize(filename)

  samp_per_segment = 64
  bytes_per_sample = 2
  channels = 2

  segments = f_size / ( samp_per_segment * bytes_per_sample * channels )

  tcd_dtype= 'int16'


  chan1 = array([], dtype=tcd_dtype)
  chan2 = array([], dtype=tcd_dtype)
  data  = zeros((samp_per_segment), dtype=tcd_dtype)
  for seg in xrange(segments):
    data = fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
    chan1 = concatenate((chan1, data.copy()) )
    data = fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
    chan2 = concatenate((chan2, data.copy()) )
  f.close()


  return (chan1, chan2)



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
    if glob.glob(filename_prefix + '.tw*') == [] || glob.glob(filename_prefix + '.td*' == [] :
	e = ExtensionError( filename_prefix, '.tw* or .td*')
	raise e

    self._filename_prefix = filename_prefix

    # set containing #'s in filename_prefix + .tx#
    self._x_set = set()
    # set containing #'s in filename_prefix + .tw#
    self._w_set = set()
    # set containing #'s in filename_prefix + .td#
    self._d_set = set()

    self._data_file = data_file

    
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

    # default metadata
    self._metadata = {'patient_name':'unknown patient', 'prf':6000, 'sample_freq':100, 'doppler_freq_1':2000, 'doppler_freq_2':2000}

    if metadata_file == '':
      metadata_file = self._data_file[:self._data_file.rfind('.tw')] + '.tx' + self._data_file[-1]
      if os.path.exists(metadata_file):
        self._metadata = __parse_metadata(metadata_file)
    else:
      os.stat(metadata_file)
      if re.match( r'.+\.tx\d', data_file) == None :
        e = ExtensionError(data_file, '.txX')
        raise e
      self._metadata = __parse_metadata(metadata_file)

    self._channel_1_data, self._channel_2_data = read_tcd(self._data_file)
    #self._channel_1_data = self._channel_1_data.astype(float) / 2.0**15 * self._metadata['prf']/2.0 *154 / self._metadata['doppler_freq_1']
    #self._channel_2_data = self._channel_2_data.astype(float) / 2.0**15 * self._metadata['prf']/2.0 *154 / self._metadata['doppler_freq_2']


  #def plot():
    figure
    time = arange(len(self._channel_1_data), dtype=float) / float(self._metadata['sample_freq'])
    max_ind = self._metadata['sample_freq'] * 5
    plot(time[:max_ind], self._channel_1_data[:max_ind], 'r-', time[:max_ind], self._channel_2_data[:max_ind], 'g-')
    xlabel('Time [sec]')
    ylabel('Velocity')
    title('Patient: ' + self._metadata['patient_name'])
    savefig(self._data_file + '.png')

  #def show_fig():
    #self.__plot()
    show()

  #def print_fig(format):
    #self.__plot()

    
	

# if running as script
if __name__ == "__main__":
      import sys
      for arg in sys.argv[1:] :
	 t = TCDAnalyze(arg)

