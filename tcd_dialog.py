#!/usr/bin/env python
## tcd_dialog
#   gives you a file chooser dialog and passes the file to tcd_analyze.py
#   for processing the transcranial doppler data generated on a DWL Multidop L2
#
#   @author Matt McCormick (thewtex) <matt@mmmccormick.com>
#   @date created 2008 April 29

import wx
import os

from tcd_analyze import TCDAnalyze as tcd

app = wx.PySimpleApp()

dialog = wx.FileDialog(None, 'Choose a data file from the DWL trancranial doppler machine', wildcard='*TW?')

if dialog.ShowModal() == wx.ID_OK:
  filename = dialog.GetFilename()
  filenamesplit = os.path.splitext(filename)
  dirname = dialog.GetDirectory()
  full = os.path.join(dirname, filenamesplit[0])
  print 'Selected:', os.path.join(dirname, filename)

  t = tcd(full)
  t.plot_w_data(w_set=[filenamesplit[1][-1]], saveit=False, showit=True)
