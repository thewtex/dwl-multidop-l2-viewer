#!/usr/bin/env python

from pylab import *
import os

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

