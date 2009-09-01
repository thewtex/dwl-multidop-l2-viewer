class TX:
    """Process a DWL Multidop L2 *.TX? file

    Arguments:
        filepath:           path to the *.TX? file

    After initialization will have a 'metadata' member that is dictionary with
    imaging parameters.
      metadata has the following dictionary keys:
	patient_name:
	  
	prf:
	  pulse repetition frequency [Hz]
	  
	sample_freq:
	  velocity curve sampling frequency [Hz]
	  
	doppler_freq_1:
	  excitation frequency of channel 1 [kHz]
	  
	doppler_freq_2:
	  excitation frequency of channel 2 [kHz]

	start_time:
	  clock time of acquisition start

	hits:
	  list with the detected hits.  Each entry is a tuple with the sample point, hit dB, and hit time
        """

    def __parse_metadata(self):
        print 'Reading ', self._filepath

        f = open(self._filepath, 'r')
        metadata = {'patient_name':'unknown patient', 'exam_date':'00-00-00', 'prf':6000, 'sample_freq':1000, 'doppler_freq_1':2000, 'doppler_freq_2':2000, 'start_time':'00:00:00', 'hits':[], 'marks':[] }

        lines = f.readlines()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(len(lines))
        self._value = 0
        self._progress_bar.setValue(self._value)
        for i in xrange(len(lines)):
            self._value = self._value + 1
            self._progress_bar.setValue(self._value)
            lis = lines[i].split()
            if lis[1] == 'HIT':
                metadata['hits'].append( (int(lis[0]), lis[2], lis[3], 'Unchecked' ) ) 
            elif lis[1][:3] == 'MRK':
                metadata['marks'].append( (int(lis[0]), lis[1],  lis[2], lis[4] ) ) 
            elif ( lis[2] == 'NAME:' ):
                metadata['patient_name'] = lines[i][lines[i].rfind('NAME:')+6:-1]
            elif ( lis[2] == 'EXAM:' ):
                metadata['exam_date'] = lis[3]
            elif ( lis[2] == 'PRF' ):	
                metadata['prf'] = int(lis[3])
            elif ( lis[2] == 'SAMPLE_F' ):	
                metadata['sample_freq'] = int(lis[3])/10
            elif ( lis[2] == 'FDOP1' ):	
                metadata['doppler_freq_1'] = int(lis[3])
            elif ( lis[2] == 'FDOP2' ):	
                metadata['doppler_freq_2'] = int(lis[3])
            elif lis[1] == 'START' :
                metadata['start_time'] = lis[2] 

        f.close()

        self.metadata = metadata

    def __init__(self, filepath, progress_bar):
        self._filepath = filepath
        self._progress_bar = progress_bar
        self.__parse_metadata()

