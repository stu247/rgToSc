# -*- coding: utf-8 -*-
#
# rgToSc.py
#
# Add iTunes SoundCheck meta-data from Replay Gain meta-data.
#
# Adapted from rg2sc.py by:
# Copyright © 2010 Rogério Theodoro de Brito
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation (or at your option, any
# latter version)
#
# References:
#
# * http://www.hydrogenaudio.org/forums/index.php?showtopic=24620
# * http://www.id3.org/iTunes_Normalization_settings
#
# Summary (oversimplified):
#
# The tag is composed of 5 pairs of integers, written in base 16:
#
# * 1st pair: the value 1000 * 10^{-gain/10} (twice)
# * 2nd pair: the value 2500 * 10^{-gain/10} (twice)
# * 3rd pair: unknown data, probably for statistical purposes
# * 4th pair: the absolute value of the peak sample (twice)
# * 5th pair: unknown data, as the 3rd pair

import sys, os
import argparse
from mutagen.id3 import ID3, COMM, RVA2
import mutagen

global args

def gain_to_watts(gain):
    return pow(10, -gain*.1)

def to_hexstring(x):
    # leading space required; blame Apple
    return " %08X" % int(x)

def write_soundcheck(file):
    try:
        audio = ID3(file)
    except mutagen.id3.error:
        print('Not an ID3 file (%s)' % file)
        return

    # The format of the key is different between GNU/Linux and Windows!
    if not args.force and (audio.get(u"COMM:iTunNORM:'eng'") or
                           audio.get(u"COMM:iTunNORM:eng")):
        # the file already has iTunNORM, by default, do not touch the file
        return

    # get the values

    print(file)
    rggain = audio.get(u"TXXX:replaygain_track_gain")
    if rggain is None:
        print('Error: could not find ReplayGain gain')
        return
    else:
        try:
            gain = float(str(rggain).translate(None, ' dB'))
        except:
            print('Error: ReplayGain gain not valid (%s)' % rggain)
            return

    rgpeak = audio.get(u"TXXX:replaygain_track_peak")
    if rgpeak is None:
        print('Error: could not find ReplayGain peak')
        return
    else:
        try:
            peak = float(str(rgpeak))
        except:
            print('Error: ReplayGain peak not valid (%s)' % rgpeak)
            return

    # write the values

    values = [
        to_hexstring(1000 * gain_to_watts(gain)),
        to_hexstring(1000 * gain_to_watts(gain)),
        to_hexstring(2500 * gain_to_watts(gain)),
        to_hexstring(2500 * gain_to_watts(gain)),
        " 00000000", # bogus
        " 00000000", # bogus
        to_hexstring(peak * (32*1024 - 1)),
        to_hexstring(peak * (32*1024 - 1)),
        " 00000000", # bogus
        " 00000000", # bogus
        ]
             
    audio.add(COMM(desc="iTunNORM", lang="eng", text="".join(values), encoding=3))
    audio.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''
Add iTunes SoundCheck meta-data from Replay Gain meta-data.
Replay Gain data is read from ID3v2 TXXX frames and SoundCheck data is stored
in iTunNORM COMM frame.  By default, the script does not update SoundCheck data
if it already exists in the file.
''')
    parser.add_argument('music_file_or_dir', nargs='+',
                        help='Music file or directory tree containing music files.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Update SoundCheck meta-data even if it already exists.')
    args = parser.parse_args();

    # process the list of directories and files
    for arg in args.music_file_or_dir:
        if os.path.isdir(arg):
            for dirpath, dirnames, filenames in os.walk(arg):
                for filename in filenames:
                    write_soundcheck(os.path.join(dirpath, filename))
        elif os.path.isfile(arg):
            write_soundcheck(arg)
        else:
            print("Error: %s is not a file or directory." % arg)

