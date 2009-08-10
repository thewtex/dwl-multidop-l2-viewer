import numpy
import os 

class TW:
    """Process a DWL Multidop L2 *.TW? file

    Arguments:
        filepath:           path to the *.TW? file
        prf:                Pulse repetition frequency
        doppler_freq_1      Doppler Frequency of Channel 1
        doppler_freq_2      Doppler Frequency of Channel 2

    After initialization, will have 'chan1' and 'chan2' which are numpy 1D arrays
    with the peak velocity for each channel
        """
    def __parse_data(self):
        print 'Reading ', self._filepath
        f = open(self._filepath, 'rb')

        samp_per_segment = 64
        bytes_per_sample = 2
        channels = 2
        tcd_dtype= 'int16'
        f_size = os.path.getsize(self._filepath)
        segments = f_size / ( samp_per_segment * bytes_per_sample * channels )
        chan1 = numpy.array([], dtype=tcd_dtype)
        chan2 = numpy.array([], dtype=tcd_dtype)
        data  = numpy.zeros((samp_per_segment), dtype=tcd_dtype)
        for seg in xrange(segments):
            data = numpy.fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
            chan1 = numpy.concatenate((chan1, data.copy()) )
            data = numpy.fromfile(f, dtype=tcd_dtype, count=samp_per_segment)
            chan2 = numpy.concatenate((chan2, data.copy()) )

        f.close()

        chan1 = chan1.astype(float) / 2.0**11 * self._prf/2.0 *154000.0 / self._doppler_freq_1/10**3
        chan2 = chan2.astype(float) / 2.0**11 * self._prf/2.0 *154000.0 / self._doppler_freq_2/ 10**3

        self.chan1 = chan1
        self.chan2 = chan2

        

    def __init__(self, filepath, prf, doppler_freq_1, doppler_freq_2):
        self._filepath = filepath
        self._prf = float(prf)
        self._doppler_freq_1 = float(doppler_freq_1)
        self._doppler_freq_2 = float(doppler_freq_2)
        self.__parse_data()
