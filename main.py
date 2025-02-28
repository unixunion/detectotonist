import sounddevice as sd
import numpy as np
import collections
import time

from loguru import logger

# Configuration
SAMPLE_RATE = 44100  # Sample rate in Hz
BUFFER_DURATION = 2  # Seconds (for pre-trigger buffer)
NOISE_THRESHOLD = 0.1  # Adjust based on environment noise
SILENCE_THRESHOLD = 0.02  # Silence level
SILENCE_DURATION = 0.5  # Seconds required to declare silence
CALIBRATION_TIME = 3000  # number of millis to sample for "silence" levels
CHANNELS = 1

# Compute buffer size
BUFFER_SIZE = int(SAMPLE_RATE * BUFFER_DURATION)

# Ring buffer to store continuous recording
ring_buffer = collections.deque(maxlen=BUFFER_SIZE)

# Flags and recording variables
recording = False
captured_audio = []
silence_start_time = None
calibrated = False
calibrating = False
calibration_start_time = None
calibrated_noise_threshold = NOISE_THRESHOLD
calibrated_silence_threshold = SILENCE_THRESHOLD
calibration_data = []  # global variable for calibration

def process_audio(audio_sample):
    """Handle the recorded sample (e.g., save or analyze)"""
    print(f"Captured {len(audio_sample)} samples.")
    # Example: Save to a file
    np.save("captured_audio.npy", np.array(audio_sample))


def audio_callback(indata, frames, time_info, status):
    """Stream callback for continuous audio capture"""
    global recording, captured_audio, silence_start_time, calibration_start_time, calibrating, calibrated, \
        calibrated_noise_threshold, calibrated_silence_threshold, calibration_data

    if status:
        logger.info(f"Audio callback error: {status}")

    # Convert to numpy array and flatten (in case of stereo)
    audio_data = indata[:, 0]

    # Append to ring buffer
    ring_buffer.extend(audio_data)

    # sample for CALIBRATION_TIME time and use that to establish the thresholds
    if not calibrated and not calibration_start_time and not calibrating:
        calibration_start_time = round(time.time() * 1000)
        calibrating = True
        calibration_data = []  # reset calibration accumulation
        logger.info("Starting calibration")
    if not calibrated and calibrating:
        calibration_data.extend(audio_data)
        if (round(time.time() * 1000) - calibration_start_time) > CALIBRATION_TIME:
            calibrated_noise_threshold = np.max(np.abs(calibration_data)) * 1.2  # for example, a margin factor
            calibrated_silence_threshold = np.mean(np.abs(calibration_data))
            logger.info(
                f"Calibration complete: noise_threshold: {calibrated_noise_threshold}, silence_threshold: {calibrated_silence_threshold}")
            calibrated = True
            calibrating = False
        else:
            logger.debug("Calibrating...")
            return

    logger.info(f"Recording: {recording} Level: {np.max(np.abs(audio_data))}, silence_threshold: {calibrated_silence_threshold}")

    # Check if audio exceeds threshold (detect noise peak)
    if not recording and np.max(np.abs(audio_data)) > calibrated_noise_threshold:
        recording = True
        captured_audio = list(ring_buffer)  # Pre-trigger buffer
        logger.info("Noise detected, starting capture...")

    # Continue recording if active
    if recording:
        captured_audio.extend(audio_data)

        # Check if audio returns to silence
        if np.max(np.abs(audio_data)) < calibrated_silence_threshold:
            if silence_start_time is None:
                silence_start_time = time.time()
            elif time.time() - silence_start_time >= SILENCE_DURATION:
                logger.info("Silence detected, stopping capture...")
                recording = False
                process_audio(captured_audio)
                captured_audio = []
                silence_start_time = None
        else:
            silence_start_time = None  # Reset silence timer


# Start continuous recording
with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
    logger.info("Listening for noise peaks...")
    while True:
        time.sleep(0.1)
