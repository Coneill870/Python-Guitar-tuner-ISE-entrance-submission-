import sounddevice as sd
import numpy as np

#each audio device connected to this computer has an index
#This query prints a list of all sound devices and their index, which can be used to identify my audio interface
print(sd.query_devices())

# all arguments of the function must be present even if unused
def callback(indata, frames, time, status):
    print(np.max(np.abs(indata)))



# as the device is recognised by its index,
# unplugging or plugging in extra audio devices my change the index of the audio interface
sd.InputStream(
    device=25,  #audio interface
    channels=2, #left or right
    samplerate=44100,
    callback=callback
).start()

input("Play something on the guitar. press enter to stop.")
#the script essentially prints a load of junk data if any input is detected from the audio interface