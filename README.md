# rgToSc
Add iTunes Sound Check meta-data from ReplayGain meta-data.

I like to listen to large playlists in shuffle mode on my Sonos speakers.  Some songs in my collection are a lot louder than others.  By adjusting the gain on each song, the volume can be normalized so that the volume of all songs are about the same.  ReplayGain (http://wiki.hydrogenaud.io/index.php?title=ReplayGain_specification) is a widely supported standard for volume normalization.  It specifies storing the song specific gain in meta-data in each MP3 file. It does not modify the music itself.  That means that the software playing the music needs to understand and use the meta-data.

Unfortunately, Sonos does not support the ReplayGain standard for MP3 files, but it does support the proprietary Apple iTunes volume normalization called Sound Check (https://sonos.custhelp.com/app/answers/detail/a_id/330).  The rgToSc.py Python script reads the ReplayGain meta-data in an MP3 file, calculates the Sound Check meta-data, and stores the Sound Check meta-data in the MP3 file.

The script can update individual files or directory structures.  If the file already contains the Sound Check meta-data, then it will not modify the file unless the -f option is used.  That way you can periodically run the script on your entire collection and only the new MP3 files will be updated, saving a lot of space during incremental backups.  

In order to generate the ReplayGain meta-data that this script depends on, I use the excellent rgain Python package (https://bitbucket.org/fk/rgain/).  Here are the commands I use:
```
collectiongain --mp3-format=replaygain.org music_dir
python rgToSc.py music_dir
```
There are a number of different possible formats to the ReplayGain meta-data for MP3 files.  The standard recommends that ID3v2 TXXX frames be used and that is what rgToSc.py uses.

This script has been tested and works on GNU/Linux and Windows7.

##### Dependencies

rgToSc.py depends on mutagen Python package (https://bitbucket.org/lazka/mutagen/overview).  The rgain package also depends on mutagen package, so installing the rgain package will take care of the rgToSc.py dependencies.  In Debian-based GNU/Linux distributions, the rgain APT package is python-rgain.
