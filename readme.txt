======================
DWL Multidop L2 Viewer
======================



Purpose
=======

For processing the transcranial doppler data generated on a DWL Multidop  L2.


Dependencies
============

You will also need 

  - python_  
  - numpy_ 
  - PyQt4_ 
  - veusz_  

.. _python: http://python.org
.. _numpy:  http://numpy.org
.. _PyQt4:  http://www.riverbankcomputing.co.uk/software/pyqt/intro
.. _veusz:  http://gna.org/projects/veusz/


Installation
============

Run::

  python setup.py install

or the appropriate installer.


Running
=======

You will need to get the ``*.TX?`` and ``*.TW?`` files off the machine.  
To copy files from the DOS prompt to a floppy, these commands may be
helpful:

  ``A:``
    Switch to floppy drive.

  ``D:``
    Switch to data drive.

  ``cd DATA``
    Change into the data directory.

  ``cd ..``
    Go up one directory.

  ``dir \p``
    List the contents of the current directory, by page.

  ``copy NLA169.* A:\``
    Copy all files starting with NLA169., e.g., to the floppy drive.

  ``erase NLA169.*``
    Erase all files starting with NLA169.

Run ``dwl_multidop.py`` to start the program.


:Author: Matt McCormick <matt@mmmccormick.com>
:Legal: See legal.txt

.. vim ft=rst
