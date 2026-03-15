import numpy as np
import sounddevice as sd

# audio interface / general settings for variables used in calculations / sounddevice functions
device_index = 25  # PreSonus Studio 24c
channel = 0  # 0 = left, 1 = right, Guitar is plugged into left
sample_rate = 44100 # how many samples of the audio input are taken per second
block_size = 2048  # bigger = more stable, slower response

min_freq = 60  # roughly B1, The lowest note on a guitar tuned to B standard / Baritone tuning
max_freq = 1200  # about 3 octaves up from this


def detect_pitch(signal): #using a fourier transform
    # DC offset: an imposed voltage shifting the average value, and subsequently the whole signal up or down.
    # magnitude of the offset = mean value of the signal
    # (think midline of a basic sin function). this is removed for accurate pitch detection
    signal = signal - np.mean(signal)

    # very quiet signal > probably no note being played
    if np.max(np.abs(signal)) < 0.004:
        return None

    # fast Fourier Transform using numpy, taking its absolute value to only consider positive frequencies
    fft_result = np.fft.rfft(signal)
    magnitudes = np.abs(fft_result)

    #the following lines return the frequencies corresponding to each bin (interval) of the rfft output
    #len(signal) = the number of audio samples in the current frame.
    #d = 1/sample rate as T = 1/f > if sample rate is 44100 hz, each sample is taken every 1/44100th of a second
    #the resulting array contains the frequencies for each FFT bin (interval)
    #from here we can map magnitudes to frequencies to find the frequency with the largest magnitude (the fundamental)
    freqs = np.fft.rfftfreq(len(signal), d=1/sample_rate)

    #mask defines the plausible range of frequencies which could be produced by an electric guitar
    mask = (freqs >= min_freq) & (freqs <= max_freq)
    # checks if any of the frequencies detected are in the plausible range for a guitar note.
    # if not, no value is returned
    if not np.any(mask):
        return None

    #extracts only frequencies in range
    magnitudes_in_range = magnitudes[mask]
    freqs_in_range = freqs[mask]

    # find the frequency peak with the largest magnitude, and hence the fundamental frequency of an inputted note
    peak_idx = np.argmax(magnitudes_in_range)
    peak_freq = freqs_in_range[peak_idx]
    peak_magnitude = magnitudes_in_range[peak_idx]

    # quality check that should help with unwanted noise
    if peak_magnitude < 3.0 * np.mean(magnitudes_in_range):
        return None

    return peak_freq


print("Guitar tuner - printing frequencies:")
print("Ctrl+C to stop\n")


# sound device repeatedly calls this function with new audio data from the audio interface
# function requires middle 2 arguments to be present even if they're unused
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Status:", status) #Displays a status ensuring the code is running correctly

    signal = indata[:, channel].copy()  # mono channel

    freq = detect_pitch(signal) #returned value from pitch detection algorithm

    if freq is not None:
        print(f"{freq:6.1f} Hz") #continuously prints pitch


# starts the audio stream
try:
    with sd.InputStream(
        device=device_index,
        channels=2,
        samplerate=sample_rate,
        blocksize=block_size,
        callback=audio_callback
    ):
        print("Press Enter to stop...\n")
        input()
# waits forever until user enters something into console or just presses enter,
# Allowing the code to continue running using no CPU space
except KeyboardInterrupt:
    print("\nStopped by user")
except Exception as e:
    print("Error:", e)