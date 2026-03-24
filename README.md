This project is a digital guitar tuner built using python 

It takes a direct raw guitar input from an audio interface, finds the fundamental frequency of the input, maps said frequency to its closest musical note, and tells the user how far out of tune their guitar is and which way they need to tune (up or down)


The project contains 4 files (listed in order of creation):

(1) Audio_Input_Test.py : a test script i wrote to see if i was getting a signal from my guitar and if the configuration for audio interface was set up correctly

(2) Fourier_Transform_Pitch_Detection.py : my first itteration / attempt at making a pitch detection algorithm, using a fourier transform. this script did not work as desired.

(3) Autocorrelation_Pitch_Detection.py : my second itteration / attempt at a pitch detection algorithm, this time using autocorrelation. The pitch detection in this script was much more accurate than in my first itteration.

(4) Autocorrelation_Pitch_Detection+Tuner.py : This script itterates upon my Autocorrelation pitch detection algorithm, taking the detected frequency form the guitar and mapping it to a guitar note like a traditional tuner.
    This is curerntly the final itteration of the project



(note: all of the above files are independent i.e. no files are imported in another file.)

