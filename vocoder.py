# Vocoder
# Bart Massey 2022

import argparse, math, os, sounddevice
import numpy as np
import scipy.signal as ss
import scipy.io.wavfile as wavfile

ap = argparse.ArgumentParser(description="Vocoder demo.")
ap.add_argument(
    "-w", "--width",
    help="Filter width (0..1).",
    type=float,
    default=0.3
)
ap.add_argument(
    "-e", "--envelope-tc",
    help="Time constant for envelope filter in Hz.",
    type=float,
    default=20
)
ap.add_argument(
    "--output-intermediates",
    help="Save intermediates as WAV files for debugging.",
    action="store_true",
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
    nargs='?',
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
    return wav.reshape(-1).astype(np.float32)

# Obtain the carrier and modulator. Truncate to the shorter
# of the two for equal length.
carrier = read_wav(args.carrier)
modulator = read_wav(args.modulator)
nsamples = min(len(carrier), len(modulator))
carrier = carrier[:nsamples]
modulator = modulator[:nsamples]

# Frequency locations of filter centers. Hardwired to
# octaves and fifths starting at A[2] and proceeding through
# E[8].
filter_centers = []
for i in range(7):
    f1 = 2 ** i * 110
    f2 = 1.5 * f1
    filter_centers += [f1, f2]

# Build a bandpass filter for each filter center. The filter
# width is a command-line argument.
filter_bank = [
    ss.iirfilter(
        4,
        (
            max(1, center * (1 - args.width / 2)),
            min(rate // 2 - 1, center * (1 + args.width / 2)),
        ),
        btype = 'bandpass',
        output = 'sos',
        fs = rate,
    )
    for center in filter_centers
]

# Return the list of samples produced by filtering the
# provided samples with each filter in the filter bank.
def filtered(samples):
    return [ss.sosfilt(f, samples) for f in filter_bank]

# Get the filter bank output for both the carrier and the
# modulator.
carrier_filtered = filtered(carrier)
modulator_filtered = filtered(modulator)

# Apply an "envelope follower" (also known as an AM
# demodulator) to the filtered modulator signals.  The idea
# is to track the peaks of a signal at low frequency to get
# the "shape" of the signal for each filtered signal.
follower_filter = ss.iirfilter(
    8,
    args.envelope_tc,
    btype = 'lowpass',
    output = 'sos',
    fs = rate,
)
envelope = [
    ss.sosfilt(follower_filter, np.abs(c)) for c in modulator_filtered
]

# Normalize the envelope gain ("AGC").
peak_envelope = max(max(e) for e in envelope)
for i in range(len(envelope)):
    envelope[i] = envelope[i] * 0.5 / peak_envelope

# Sum up the envelope times the carrier signal across all
# filtered frequencies to get the output signal.
vocoded = np.zeros(nsamples, dtype=np.float32)
for i in range(len(filter_bank)):
    vocoded += carrier_filtered[i] * envelope[i]

# Normalize the output gain ("AGC").
peak = np.max(np.abs(vocoded))
vocoded *= 0.5 / peak

def wav_write(filename, samples):
    samples = (32767 * samples).reshape(-1, 1).astype(np.int16)
    wavfile.write(filename, rate, samples)

# Either play the output or write it to a WAV file.
if args.output:
    wav_write(args.output, vocoded)
else:
    nchunk = 4096
    nvocoded = len(vocoded)
    stream = sounddevice.OutputStream(
        blocksize = nchunk,
        channels = 1,
        samplerate = rate,
    )
    stream.start()
    for i in range(0, nvocoded, nchunk):
        stream.write(vocoded[i : i + nchunk])
    stream.stop()
    stream.close()

# Useful for debugging and display.
if args.output_intermediates:
    try:
        os.mkdir("products")
    except FileExistsError:
        pass
    for i, c in enumerate(filter_centers):
        filename = f"products/env{int(c)}.wav"
        wav_write(filename, envelope[i])
        filename = f"products/car{int(c)}.wav"
        wav_write(filename, carrier_filtered[i])
        filename = f"products/mod{int(c)}.wav"
        wav_write(filename, modulator_filtered[i])
