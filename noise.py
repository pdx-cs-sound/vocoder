import sys
import numpy as np
import scipy.io.wavfile as wavfile

rate = 48000

nnoise = int(sys.argv[1])
noise = np.random.rand(int(nnoise * rate))

wavfile.write(sys.argv[2], rate, noise)
