# Vocoder
# Bart Massey 2022

import argparse, math
import numpy as np
import scipy.signal as ss
import scipy.io.wavfile as wavfile

ap = argparse.ArgumentParser()
ap.add_argument(
    "-w", "--width",
    help="Filter width (0..1)",
    type=float,
    default=0.1
)
ap.add_argument(
    "carrier",
    help="Input carrier audio file.",
)
ap.add_argument(
    "modulator",
    help="Input modulator audio file.",
)
ap.add_argument(
    "output",
    help="Output audio file.",
)
args = ap.parse_args()

# Sample rate in samples / second.
rate = 48000
# Chunk size in samples.
nchunk = 8192

def read_wav(filename):
    wrate, wav = wavfile.read(filename)
    assert rate == wrate, "need 48000 sps wave"
    assert len(np.shape(wav)) == 1, "need 1 channel wave"
    return wav.astype(np.float32)


carrier = read_wav(args.carrier)
modulator = read_wav(args.modulator)
nsamples = min(len(carrier), len(modulator))
carrier = carrier[:nsamples]
modulator = modulator[:nsamples]

filter_centers = []
for i in range(7):
    f1 = 2 ** i * 110
    f2 = 1.5 * f1
    filter_centers += [f1, f2]

filter_bank = [
    ss.iirfilter(
        4,
        (
            center * (1 - args.width / 2),
            center * (1 + args.width / 2),
        ),
        btype = 'bandpass',
        output = 'sos',
        fs = rate,
    )
    for center in filter_centers
]

def filtered(samples):
    return [ss.sosfilt(f, samples) for f in filter_bank]

carrier_filtered = filtered(carrier)
modulator_filtered = filtered(modulator)

follower_filter = ss.iirfilter(
    4,
    50,
    btype = 'lowpass',
    output = 'sos',
    fs = rate,
)
envelope = [
    ss.sosfilt(follower_filter, np.abs(c)) for c in carrier_filtered
]

result = np.zeros(nsamples)
for i in range(len(filter_bank)):
    result += modulator_filtered[i] * envelope[i]

peak = np.max(np.abs(result))
result *= 0.5 / peak

wavfile.write(args.output, rate, result)
