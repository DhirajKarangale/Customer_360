import sys
import os
import time
import logging

logger = logging.getLogger(__name__)
try:
    import winsound
except ImportError:
    winsound = None


def _mac_play_beeps(beeps_with_pauses):
    try:
        import math
        import wave

        sample_rate = 44100
        wave_file = "/tmp/mac_beep.wav"
        with wave.open(wave_file, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            audio_data = bytearray()
            for freq, duration_ms, pause_ms in beeps_with_pauses:
                num_samples = int(sample_rate * (duration_ms / 1000.0))
                for i in range(num_samples):
                    value = int(
                        32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate)
                    )
                    audio_data.extend(value.to_bytes(2, "little", signed=True))
                if pause_ms > 0:
                    pause_samples = int(sample_rate * (pause_ms / 1000.0))
                    audio_data.extend(b"\x00\x00" * pause_samples)
            wf.writeframesraw(audio_data)
        os.system(f"afplay {wave_file}")
        os.remove(wave_file)
    except Exception:
        pass


def _play_error_windows():
    try:
        if winsound:
            for _ in range(7):
                winsound.Beep(3000, 1000)
                time.sleep(0.05)
        else:
            logger.info("\x07")
    except:
        logger.info("\x07")


def _play_success_windows():
    try:
        if winsound:
            winsound.Beep(392, 150)
            winsound.Beep(523, 150)
            winsound.Beep(659, 150)
            winsound.Beep(784, 200)
            winsound.Beep(659, 150)
            winsound.Beep(784, 600)
    except:
        pass


def _play_error_mac():
    _mac_play_beeps([(3000, 1000, 50)] * 7)


def _play_success_mac():
    _mac_play_beeps(
        [
            (392, 150, 0),
            (523, 150, 0),
            (659, 150, 0),
            (784, 200, 0),
            (659, 150, 0),
            (784, 600, 0),
        ]
    )


def _play_error():
    if sys.platform == "win32":
        _play_error_windows()
    elif sys.platform == "darwin":
        _play_error_mac()
    else:
        logger.info("\x07")


def _play_success():
    if sys.platform == "win32":
        _play_success_windows()
    elif sys.platform == "darwin":
        _play_success_mac()
    else:
        pass


def play_sound(status: str):
    if status.lower() == "success":
        _play_success()
    elif status.lower() == "error":
        _play_error()
    else:
        logger.info(f"Unknown sound status: {status}")
