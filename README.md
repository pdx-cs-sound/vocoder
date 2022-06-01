# vocoder: Vocoder Demo
Bart Massey 2022

This is a demo
[vocoder](https://en.wikipedia.org/wiki/Vocoder) written in
Python. It applies the volume envelope of a modulator signal
to a carrier signal across a range of frequencies produced
by a filter bank. Typically the carrier signal is some kind
of music and the modulator signal is a voice: this "makes
the music sound like it is talking."

In this demo version, the filter bank uses A and E
frequencies across 7 octaves. The filter widths and the
envelope follower cutoff are specifiable.

Run as

    python3 vocoder.py sadday.wav torvalds.wav

to produce a pleasing effect.

This work is made available under the "MIT license". Please
see the file `LICENSE.txt` in this distribution for license
terms.

The file `sadday.wav` included with this distribution is a
clip from the song
[“A Sad Day”](https://freemusicarchive.org/genre/Electronic/)
by Maarten Schellekens, available under the
[Creative Commons Attribution-Noncommercial License](https://creativecommons.org/licenses/by-nc/1.0/). Thanks
to [Free Music Archive](http://freemusicarchive.org) for
providing this.

The file `torvalds.wav` is a re-encoding of a Sun-format
(8-bit µ-law) recording of Linus Torvalds. I have no
recollection of where I got it: it's more than 20 years old.
