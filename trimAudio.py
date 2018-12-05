from pathlib import Path
import os
import numpy as np
from essentia.standard import MonoLoader, MonoWriter


def ls(ruta = Path.cwd()):
    '''
    Read all the paths inside a given path
    :param ruta: path where you wanna read childs path
    :return: dirPath: child path from given path
    '''
    dirPath = [str(ruta + arch.name + '/') for arch in Path(ruta).iterdir()
               if os.path.isdir(os.path.join(ruta,arch.name))]
    return dirPath


def thresholdAudio(audioPath='testDownload/', t=-30, fs=44100):
    '''
    Run thresholdAudio for trim all de mp3 audio files in a audioPath/../.. where the first .. is related
    with the queryText and the second .. is related with the location of freesound track.
    It was thougt to use after soundDownload.py from sms-tool package at freesound source.

    :param audioPath: path where sounds where download (possible path used for soundDownload.py). Default: testDownload/
    :param t: threshold (in dB) to trim audiofiles related to max value of file. Default: -30
    :param fs: fs for the output sound. Default: 44100
    :return: print(Done!!)
    '''

    thTimes = 10 ** (t/20)                                          #threshold: dB to times
    instrument = ls(audioPath)                                      #read the queryText path inside the given path
    audioTrack = [ls(str(key)) for key in instrument]               #read the different folder inside each queryText path
    a, b = np.shape(audioTrack)                                     #size of the matrix
    finalArray = [os.path.join(str(audioTrack[i][j]), arch.name)
                  for i in np.arange(a) for j in np.arange(b) for arch in
                  Path(str(audioTrack[i][j])).iterdir()
                  if arch.name.endswith('.mp3')]                    #array for each track

    for key in finalArray:
        track = MonoLoader(filename=key, sampleRate=fs)()           #read audio and transform into mono
        maximo = np.max(abs(track))                                 #set the abs maximum
        i = 0
        j = -1
        while abs(track[i]) < maximo * thTimes:                     #find the first significant value
            i += 1
        while abs(track[j]) < maximo * thTimes:                     #find the last significant value
            j -= 1
        shortTrack = track[i:j]                                     #build the trimed track
        MonoWriter(filename=key + 'computed.wav')(shortTrack)       #write the file at same location of given
    print('Done!!')

