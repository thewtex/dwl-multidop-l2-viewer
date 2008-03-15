#!/usr/bin/env python

# tcd_analyze.py
# for processing the transcranial doppler data
# Matt McCormick (thewtex) <matt@mmmccormick.com>
# 2008 March 15

from pylab import *
import os
import re



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

  Create figures and save them."""

  def __init__(self, data_file, metadata_file=''):
    # argument checking
    os.stat(data_file)
    if re.match( r'.+\.tw\d', data_file) == None :
      e = ExtensionError(data_file, '.twX')
      raise e

    self.data_file = data_file

    
    def __parse_metadata(metadata_file):
      f = open(metadata_file, 'r')
      
      lines = f.readlines()
      patient_name = lines[1].split()[3]
      prf = lines[3].split()[3]
      sample_freq = lines[4].split()[3]
      doppler_freq_1 = lines[7].split()[3]
      doppler_freq_2 = lines[8].split()[3]

      f.close()

      return (patient_name, prf, sample_freq, doppler_freq_1, doppler_freq_1)

    # default metadata

    if metadata_file == '':
      metadata_file = data_file[:data_file.rfind('.tw')] + 'tx' + p[-1]
      if os.path.exists(metadata_file):
	(self._patient_name, self._prf, self._sample_freq, self._doppler_freq_1, self._doppler_freq_1) = __parse_metadata(metadata_file)
      else:
	# default metadata
	self._patient_name = 'unknown patient'
	self._prf = 6000
	self._sample_freq = 1000
	self._doppler_freq_1 = 2000
	self._doppler_freq_2 = 2000
    else:
      os.stat(metadata_file)
      if re.match( r'.+\.tx\d', data_file) == None :
        e = ExtensionError(data_file, '.txX')
        raise e
      (self._patient_name, self._prf, self._sample_freq, self._doppler_freq_1, self._doppler_freq_1) = __parse_metadata(metadata_file)

	


    self.metadata_file = metadata_file
