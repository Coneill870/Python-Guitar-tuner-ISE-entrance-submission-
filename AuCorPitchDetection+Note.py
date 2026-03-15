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

# Note detection component

note_names = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]

A4_freq = 440.0 # reference frequency corresponding to A4. this will be used to determine the frequency of other notes
A4_index = 69  # reference midi number corresponding to A4

#Function that will convert the detected frequency to a musical note
def freq_to_note(freq):

    # MIDI note number
    # MIDI is a system that assigns a number to each musical note
    # very handy for calculations relating to music
    midi = 69 + 12 * np.log2(freq / A4_freq) #reference midi (69) + formula used derived in notebook

    nearest_midi = int(round(midi))

    # Note name
    # removes the octave information from the midi,
    # leaving just the index corresponding to its musical note, outlined in NOTE_NAMES
    note_name = note_names[nearest_midi % 12]

    # note octave
    # used to find the octave associated with a note. the -1 must be included as midi numbering starts at 0,
    # without this the returned octave value will be 1 higher than it should be
    octave = (nearest_midi // 12) - 1

    # Exact frequency of nearest note which we are trying to tune to.
    # not to be confused with the detected frequency
    # formula for finding nearest note frequency, derived in notebook
    note_freq = A4_freq * 2 ** ((nearest_midi - 69) / 12)

    # cents difference
    # 100 cents between notes therefore 1200 cents between octaves,
    # combined with the midi number formula to find number of cents away from in tune note
    cents = 1200 * np.log2(freq / note_freq)

    return f"{note_name}{octave}", cents

print("Guitar tuner frequencies:")
print("Ctrl+C to stop\n")


# Sound device repeatedly calls this function with new audio data from the audio interface
#function requires middle 2 arguments to be present even if they're unused
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Status:", status) #Displays a status ensuring the code is running correctly

    signal = indata[:, channel].copy()  # mono channel

    freq = detect_pitch(signal) #returned value from pitch detection algorithm

    if freq is not None:
        note, cents = freq_to_note(freq)

        # within 3 cents is close enough to be considered intune.
        # above 25 cents off means its closer to another note and will show that note instead.
        arrow = ""
        if -25 <= cents < -3:
            arrow = "^"  # if flat tune up
        elif 3 < cents <= 25:
            arrow = "v"  # if sharp tune down
        else:
            arrow = "="  # in tune

        print(f"\r{freq:7.2f} Hz   {note:4s} {arrow} ({cents:+5.1f} cents)",
        end="")


# Starts the audio stream
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