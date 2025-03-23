import re
import subprocess
import tempfile
import time
from sys import modules as mod

import numpy as np
import torch
from nltk import download
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
from pydub.playback import play
from scipy.io.wavfile import write

from utils.tools import prepare_text

try:
    import winsound
except ImportError:
    from subprocess import call
print("Initializing TTS Engine...")

kwargs = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.PIPE,
    "stdin": subprocess.PIPE,
}


class tts_runner:
    def __init__(self, use_p1: bool = False, log: bool = False):
        self.log = log
        if use_p1:
            self.emb = torch.load("models/emb/glados_p1.pt")
        else:
            self.emb = torch.load("models/emb/glados_p2.pt")
        # Select the device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.is_vulkan_available():
            self.device = "vulkan"
        else:
            self.device = "cpu"

        # Load models
        self.glados = torch.jit.load("models/glados-new.pt")
        self.vocoder = torch.jit.load("models/vocoder-gpu.pt", map_location=self.device)
        for i in range(2):
            init = self.glados.generate_jit(prepare_text(str(i)), self.emb, 1.0)
            init_mel = init["mel_post"].to(self.device)
            init_vo = self.vocoder(init_mel)

    def run_tts(self, text, alpha: float = 1.0) -> AudioSegment:
        x = prepare_text(text)

        with torch.no_grad():

            # Generate generic TTS-output
            old_time = time.time()
            tts_output = self.glados.generate_jit(x, self.emb, alpha)
            if self.log:
                print(
                    "Forward Tacotron took "
                    + str((time.time() - old_time) * 1000)
                    + "ms"
                )

            # Use HiFiGAN as vocoder to make output sound like GLaDOS
            old_time = time.time()
            mel = tts_output["mel_post"].to(self.device)
            audio = self.vocoder(mel)
            if self.log:
                print("HiFiGAN took " + str((time.time() - old_time) * 1000) + "ms")

            # Normalize audio to fit in wav-file
            audio = audio.squeeze()
            audio = audio * 32768.0
            audio = audio.cpu().numpy().astype("int16")
            output_file = tempfile.TemporaryFile()
            write(output_file, 22050, audio)
            sound = AudioSegment.from_wav(output_file)
            output_file.close()
            return sound

    def speak_one_line(self, audio, name: str):
        audio.export(name, format="wav")
        if "winsound" in mod:
            winsound.PlaySound(name, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            try:
                subprocess.Popen(["play", name], **kwargs)
            except FileNotFoundError:
                try:
                    subprocess.Popen(["aplay", name], **kwargs)
                except FileNotFoundError:
                    subprocess.Popen(["pw-play", name], **kwargs)

    def speak(self, text, alpha: float = 1.0, save: bool = True, delay: float = 0.1):
        download("punkt", quiet=self.log)
        sentences = sent_tokenize(text)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            first_wav_path = temp_file.name

        audio = self.run_tts(sentences[0], alpha)
        pause = AudioSegment.silent(duration=int(delay * 1000))

        first_segment = AudioSegment.silent(duration=1000) + audio
        first_segment.export(first_wav_path, format="wav")
        self.speak_one_line(first_segment, first_wav_path)

        complete_audio = audio

        old_time = time.time()
        old_dur = first_segment.duration_seconds
        if len(sentences) > 1:
            for idx in range(1, len(sentences)):

                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    current_wav_path = temp_file.name

                current_segment = self.run_tts(sentences[idx], alpha)
                complete_audio += pause + current_segment

                time_left = old_dur - (time.time() + old_time)
                if time_left <= 0 and self.log:
                    print("Processing is slower than realtime!")
                else:
                    time.sleep(max(0, time_left) + delay)

                current_segment.export(current_wav_path, format="wav")
                self.speak_one_line(current_segment, current_wav_path)

                old_time = time.time()
                old_dur = current_segment.duration_seconds
        else:
            time.sleep(old_dur + 0.1)

        if save:
            safe_filename = re.sub(r"[^\w\s-]", "", text)[:50].strip().replace(" ", "_")

            output_file = f"{safe_filename}.wav"
            complete_audio.export(output_file, format="wav")

        time_left = old_dur - (time.time() + old_time)
        if time_left > 0:
            time.sleep(time_left + delay)


if __name__ == "__main__":
    glados = tts_runner(False, True)
    while True:
        text = input("Input: ")
        if len(text) > 0:
            glados.speak(text, True)
