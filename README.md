# GLaDOS Text-to-Speech Research Fork

Python TTS project based on the GLaDOS voice engine from
[`R2D2FISH/glados-tts`](https://github.com/R2D2FISH/glados-tts). This fork keeps
the original neural TTS engine and adds two research-facing extensions:

- a browser UI for interactive GLaDOS-style text-to-speech and chat playback;
- a book-to-audio synthesis script used to generate synthetic speech data for
  voice-model training experiments.

This repository is best treated as one research artifact with three layers:
upstream TTS engine, interactive UI, and synthetic-corpus generation. Keeping the
layers together makes the paper artifact easier to inspect because the same model
runtime powers both the demo UI and the dataset generation pipeline.

The project is compatible with Python 3.9, 3.10, 3.11, and 3.12. It has been
primarily developed and tested with Python 3.10.

## What This Fork Adds

### Browser UI

The Flask app in `engine.py` serves a web interface from `templates/` and
`static/`. The UI sends user text to `/synthesize`, receives generated speech,
and plays the synthesized audio in the browser. When `OPENAI_API_KEY` is
configured, the route can first generate an in-character text response and then
synthesize that response.

Run the UI server from the repository root:

```console
python3 engine.py
```

Default port is `8124`.

### Synthetic Book Audio Pipeline

`synthesize_book.py` converts a plain-text book into sentence-level WAV files and
metadata suitable for later voice-model training experiments. The script:

- reads a UTF-8 text file;
- splits the text into sentences;
- converts numbers to words;
- samples short, medium, and long sentence groups;
- synthesizes one WAV per selected sentence;
- writes `metadata.csv` rows as `wav_id|original_sentence|processed_sentence`.

Example:

```console
python3 synthesize_book.py --book_path books/example.txt --output_path processed_books/example
```

Generated WAV files and book corpora are local research artifacts and should not
be committed to the repository. The pipeline is documented here for
reproducibility; generated datasets can be published separately when needed.

## Original TTS Engine Usage

For direct command-line playback:

```console
python3 glados.py
```

The TTS engine can also be used remotely on a more powerful machine to process
in-house TTS requests. In this fork, the Flask server is started with:

```console
python3 engine.py
```

Set the downstream voice-assistant configuration to point at the synthesize
route:

```env
TTS_ENGINE_API=http://192.168.1.3:8124/synthesize/
```

## Installation

1. Download the model files from
   [`Google Drive`](https://drive.google.com/file/d/1TRJtctjETgVVD5p7frSVPmgw8z8FFtjD/view?usp=sharing)
   and unzip them into the repository folder.
2. Install Python packages:

   ```console
   pip install -r requirements.txt
   ```

3. Add a `.env` file in the repository root when using the chat-backed UI:

   ```env
   OPENAI_API_KEY=your_key_here
   ```

The base TTS engine can run without the OpenAI key. The browser chat route needs
the key because it generates a text response before synthesis.

## Upstream Model Training Notes

These notes describe the upstream model provenance retained by this fork.

### Training (New Model)

The Tacotron and ForwardTacotron models were trained as multispeaker models on
two datasets separated into three speakers. LJSpeech (13,100 lines), and then on
the heavily modified version of the Ellen McClain dataset, separated into Portal
1 and 2 voices (with punctuation and corrections added manually). The lines from
the end of Portal 1 after the cores get knocked off were counted as Portal 2
lines.

### Training (Old Model)

The initial, regular Tacotron model was trained first on LJSpeech, and then on a
heavily modified version of the Ellen McClain dataset (all non-Portal 2 voice
lines removed, punctuation added).

- The Forward Tacotron model was only trained on about 600 voice lines.
- The HiFiGAN model was generated through transfer learning from the sample.
- All models have been optimized and quantized.

## Research Artifact Notes

This repository does not claim ownership of the original GLaDOS TTS model work.
It documents the local fork used for UI experimentation and synthetic audio
generation. For paper reproducibility, cite this fork for the UI and corpus
generation workflow, and cite the upstream project for the original engine and
model assets.
