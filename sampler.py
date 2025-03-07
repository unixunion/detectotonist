import collections
import hashlib
import os.path
import signal
import sys
import time

import soundfile as sf
import librosa
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from loguru import logger

INPUT_DIR = os.path.join("data", "input")


class AudioClassifierApp:
    def __init__(self):
        """Initialize audio parameters and recording variables"""
        # Configuration
        self.SAMPLE_RATE = 44100  # Hz
        self.BUFFER_DURATION = 2  # Seconds
        self.NOISE_THRESHOLD = 0.1  # Initial noise threshold
        self.SILENCE_THRESHOLD = 0.02  # Silence level
        self.SILENCE_DURATION = 1  # Seconds required to declare silence
        self.CALIBRATION_TIME = 3000  # Calibration time in milliseconds
        self.CHANNELS = 1
        self.ROLLING_WINDOW = 20  # Frames for silence detection up from 10

        # Compute buffer size
        self.BUFFER_SIZE = int(self.SAMPLE_RATE * self.BUFFER_DURATION)

        # Audio Buffers
        self.ring_buffer = collections.deque(maxlen=self.BUFFER_SIZE)
        self.rolling_silence_buffer = collections.deque(maxlen=self.ROLLING_WINDOW)

        # Flags & Variables
        self.recording = False
        self.captured_audio = []
        self.silence_start_time = None
        self.calibrated = False
        self.calibrating = False
        self.calibration_start_time = None
        self.calibrated_noise_threshold = self.NOISE_THRESHOLD
        self.calibrated_silence_threshold = self.SILENCE_THRESHOLD
        self.calibration_data = []

        # Register signal handler for clean exit
        signal.signal(signal.SIGINT, self.exit_handler)

    def process_audio(self, audio_sample):
        """Handle the recorded sample (e.g., save or analyze)"""
        logger.info(f"Captured {len(audio_sample)} samples.")
        filename = hashlib.sha1(f"{audio_sample}".encode(encoding="UTF-8")).digest().hex()
        self.save_image(audio_sample, filename=filename)

    def save_mel_spectrogram(self, audio_sample, filename=None):
        S = librosa.feature.melspectrogram(y=np.array(audio_sample), sr=self.SAMPLE_RATE)
        S_db = librosa.power_to_db(S, ref=np.max)
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_db, sr=self.SAMPLE_RATE)
        plt.savefig(f"{INPUT_DIR}/{filename}.png")
        plt.close()

    # def save_mel_spectrogram_trimmed(self, audio_sample, filename=None):
    #
    #     y = np.array(audio_sample)
    #
    #     # Trim leading and trailing silence
    #     # top_db=30 is a typical threshold; you can adjust as needed
    #     trimmed_audio, index = librosa.effects.trim(y, top_db=60)
    #
    #     # Compute Mel-spectrogram on the trimmed audio
    #     S = librosa.feature.melspectrogram(y=trimmed_audio, sr=self.SAMPLE_RATE)
    #     S_db = librosa.power_to_db(S, ref=np.max)
    #
    #     plt.figure(figsize=(10, 4))
    #     librosa.display.specshow(S_db, sr=self.SAMPLE_RATE)
    #     plt.savefig(f"{INPUT_DIR}/melt_{filename}.png")
    #     plt.close()
    #
    # def save_waveform(self, audio_sample, filename=None):
    #     plt.figure(figsize=(10, 3))
    #     librosa.display.waveshow(np.array(audio_sample), sr=self.SAMPLE_RATE)
    #     # plt.title("Waveform")  # optional
    #     save_path = f"{INPUT_DIR}/waveform_{filename}.png"
    #     plt.savefig(save_path)
    #     plt.close()
    #     print(f"Saved {save_path}")

    def save_wav(self, audio_sample, filename=None):
        """
        Save the audio sample as a WAV file at self.SAMPLE_RATE.
        """
        audio_array = np.array(audio_sample, dtype=np.float32)  # Ensure float32 for typical WAV usage
        wav_path = f"{INPUT_DIR}/{filename}.wav"

        # Write the file
        sf.write(wav_path, audio_array, self.SAMPLE_RATE)

        logger.info(f"Saved WAV: {wav_path}")

    def save_npy(self, audio_sample, filename=None):
        """
        Save the audio sample as a .npy (NumPy) file.
        """
        # Convert to a NumPy array if it's still a list
        audio_array = np.array(audio_sample, dtype=np.float32)
        npy_path = f"{INPUT_DIR}/{filename}.npy"

        np.save(npy_path, audio_array)

        logger.info(f"Saved NPY: {npy_path}")

    def save_image(self, audio_sample, filename=None):
        """Convert audio sample to spectrogram and save as image"""
        # if image_type is ImageType.MEL_SPECTROGRAM:
        self.save_mel_spectrogram(audio_sample, filename=filename)
        self.save_wav(audio_sample, filename=filename)
        self.save_npy(audio_sample, filename=filename)

    def audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback for continuous audio capture"""
        if status:
            logger.warning(f"Audio callback error: {status}")

        # Convert to numpy array and flatten (in case of stereo)
        audio_data = indata[:, 0]

        # Append to ring buffer
        self.ring_buffer.extend(audio_data)

        # Perform calibration
        if not self.calibrated and not self.calibration_start_time and not self.calibrating:
            self.calibration_start_time = round(time.time() * 1000)
            self.calibrating = True
            self.calibration_data = []  # Reset calibration accumulation
            logger.info("Starting calibration")

        if not self.calibrated and self.calibrating:
            self.calibration_data.extend(audio_data)
            if (round(time.time() * 1000) - self.calibration_start_time) > self.CALIBRATION_TIME:
                self.calibrated_noise_threshold = np.percentile(np.abs(self.calibration_data), 95) * 1.2
                self.calibrated_silence_threshold = np.mean(np.abs(self.calibration_data)) + \
                                                    np.std(np.abs(self.calibration_data)) * 0.5
                logger.info(
                    f"Calibration complete: noise_threshold: {self.calibrated_noise_threshold}, "
                    f"silence_threshold: {self.calibrated_silence_threshold}"
                )
                self.calibrated = True
                self.calibrating = False
            else:
                return  # Continue calibration

        # Check if audio exceeds threshold (detect noise peak)
        if not self.recording and np.max(np.abs(audio_data)) > self.calibrated_noise_threshold:
            self.recording = True
            self.captured_audio = list(self.ring_buffer)  # Store pre-trigger buffer
            logger.info(f"Noise detected: {np.max(np.abs(audio_data))}, starting capture...")
            self.rolling_silence_buffer.clear()  # Reset buffer on new recording

        # Continue recording if active
        if self.recording:
            self.captured_audio.extend(audio_data)

            frame_amplitude = np.mean(np.abs(audio_data))
            self.rolling_silence_buffer.append(frame_amplitude)

            # Update rolling silence buffer
            # self.rolling_silence_buffer.append(np.mean(audio_data))  # Use rolling mean to avoid spikes

            # Check if audio returns to silence
            if np.mean(self.rolling_silence_buffer) < self.calibrated_silence_threshold:
                if self.silence_start_time is None:
                    self.silence_start_time = time.time()
                    logger.info(f"Silence start detected at {self.silence_start_time:.3f}")
                elif time.time() - self.silence_start_time >= self.SILENCE_DURATION:
                    logger.info("Silence detected, stopping capture...")
                    self.recording = False
                    self.process_audio(self.captured_audio)
                    self.captured_audio = []
                    self.silence_start_time = None
            else:
                # **Only reset if consistently above threshold for multiple frames**
                if len(self.rolling_silence_buffer) == self.ROLLING_WINDOW and np.mean(
                        self.rolling_silence_buffer) > self.calibrated_silence_threshold:
                    logger.info("Resetting silence start time due to sustained noise")
                    self.silence_start_time = None  # Reset silence timer

    def run(self):
        """Start the audio stream and continuously listen"""
        logger.info("Listening for noise peaks...")
        with sd.InputStream(samplerate=self.SAMPLE_RATE, channels=self.CHANNELS, callback=self.audio_callback):
            while True:
                time.sleep(0.1)

    def exit_handler(self, sig, frame):
        """Handle SIGINT (Ctrl+C) for clean exit"""
        logger.info("Exiting application...")
        sys.exit(0)


if __name__ == "__main__":
    app = AudioClassifierApp()
    app.run()