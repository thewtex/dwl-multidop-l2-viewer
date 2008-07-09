from distutils.core import setup
setup(name='tcd_analyze',
      version='0.4.1',
      description='For processing the transcranial doppler data generated on a DWL Multidop  L2.',
      long_description='See readme.txt',
      author='Matt McCormick',
      author_email='matt@mmmccormick.com',
      url='http://mmmccormick.com/#tcd_analyze',
      license='See legal.txt',
      py_modules=['tcd_analyze'],
      requires=['pylab', 'numpy'],
      scripts=['tcd_analyze.py'],
      )
