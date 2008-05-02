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
  Linux users may just want to install the 'matplotlib' or 'python-matplotlib'
  Windows user may want the Enthought Python Distribution.
  and the 'wxpython' packages.


Installation:
  run:
    python setup.py install
    or the appropriate installer.


Running:
  You will need to get the *.TX* and *.TW files off the machine.  
  To copy files from the DOS prompt to a floppy, these commands may be
  helpful:
  
    A:
  Switch to floppy drive.

    D:
  Switch to data drive.

    cd DATA
  Change into the data directory.

    cd ..
  Go up one directory.

    dir \p
  List the contents of the current directory, by page.

    copy NLA169.* A:\
  Copy all files starting with NLA169., e.g., to the floppy drive.

    erase NLA169.*
  Erase all files starting with NLA169.



  Installs a graphical file picker
    tcd_dialog.py
  Run it to start the program.


Author:
  Matt McCormick <matt@mmmccormick.com>

Legal:
  See legal.txt
