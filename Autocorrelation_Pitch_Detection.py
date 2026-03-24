import numpy as np
import sounddevice as sd

# audio interface / general settings for variables used in calculations / sounddevice functions
device_index = 25  # PreSonus Studio 24c
channel = 0  # 0 = left, 1 = right, Guitar is plugged into left
sample_rate = 44100 # how many samples of the audio input are taken per second
block_size = 2048  # bigger = more stable, slower response

min_freq = 60  # roughly B1, The lowest note on a guitar tuned to B standard / Baritone tuning
max_freq = 1200  # about 3 octaves up from this


def detect_pitch(signal): #using Autocorrelation
    # DC offset: an imposed voltage shifting the average value, and subsequently the whole signal up or down.
    # magnitude of the offset = mean value of the signal
    # (think midline of a basic sin function). this is removed for accurate pitch detection
    signal = signal - np.mean(signal)

    # Very quiet signal > probably no note being played
    if np.max(np.abs(signal)) < 0.003:
        return None

    # Autocorrelation:
    # This detects the fundamental frequency of a guitar note by comparing its waveform with itself.
    # The signal is passed through the function twice, as I want to compare the signal to itself at different points.
    corr = np.correlate(signal, signal, mode='full')
    # The bellow value corresponds to zero lag.
    # Any negative lag before this value is discarded as it is redundant for pitch detection
    corr = corr[len(corr) // 2:]

    # Defines max / min plausible guitar frequencies.
    # used in line 43 to limit the correlation search to physically possible guitar pitches.
    # dividing the sample rate by frequency gives a value in number of lags.
    min_lag = int(sample_rate / max_freq)
    max_lag = int(sample_rate / min_freq)

    # Masks out 0 Lag. When there is no lag (i.e when the lag approaches the minimum value assigned),
    # the waveform of the guitar note is simply laid on itself, providing no relevant pitch detection information
    corr[:min_lag] = 0

    # Find strongest correlation peak between the plausible range of guitar frequencies
    peak = np.argmax(corr[min_lag:max_lag])
    lag = peak + min_lag #as any frequencies <= the minimum lag are not included in the search,
    #the min_lag which we ignored must be added to the peak value we found within the interval
    # to give a correct index for the lag at which the fundamental frequency is found

    if lag == 0:  # precautionary step; shouldn't happen after the masking step at line 40
        return None

    frequency = sample_rate / lag #derived in notebook
    return frequency


print("Guitar tuner frequencies:")
print("Ctrl+C to stop\n")


# Sound device repeatedly calls this function with new audio data from the audio interface
#sounddevice input steam (line 64) requires middle 2 arguments to be present even if they're unused
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Status:", status) #Displays a status ensuring the code is running correctly

    signal = indata[:, channel].copy()  # mono channel

    freq = detect_pitch(signal) #returned value from pitch detection algorithm

    if freq is not None:
        print(f"{freq:6.1f} Hz") #continuously prints pitch


# Starts the audio stream
try:
    with sd.InputStream(
        device=device_index,
        channels=2,
        samplerate=sample_rate,
        blocksize=block_size,
        callback=audio_callback
    ):
        print("Press Enter to stop\n")
        input()
    # waits forever until user enters something into console or just presses enter,
    # Allowing the code to continue running using no CPU space
except KeyboardInterrupt:
    print("\nStopped by user")
except Exception as e:
    print("Error:", e)

