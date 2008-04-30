tcd_analyze

Purpose:
  For processing the transcranial doppler data generated on a DWL Multidop  L2.


Dependencies:
  You will also need python, wxpython, numpy, and matplotlib.  
  See:
  http://python.org
  http://scipy.org
  http://wxpython.org

  They are all conveniently packages together in Enthought Python Distribution
  http://www.enthought.com/products/epd.php


Installation:
  run:
    python setup.py install


Running:
  You will need to get the *.TX* and *.TW files off the machine.  You may
  find BG-Rescue Linux helpful for this
  http://www.giannone.eu/rescue/current/


  installs a 'tcd_analyze.py' script.  
    process_directory.py -h
  for help.

  Also installs a graphical file picker
    tcd_dialog.py


Author:
  Matt McCormick <matt@mmmccormick.com>

Legal:
  See legal.txt
