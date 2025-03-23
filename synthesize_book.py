import argparse
import csv
import os
import re

from nltk.tokenize import sent_tokenize, word_tokenize
from num2words import num2words

from glados import tts_runner


def text_to_words(text):
    return re.sub(r"\d+", lambda x: num2words(int(x.group(0))), text)


def preprocess_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    text = text.replace("\n", " ").strip()
    sentences = sent_tokenize(text)
    return sentences, [text_to_words(s) for s in sentences]


def create_output_folder(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    wav_folder = os.path.join(base_folder, "wavs")
    if not os.path.exists(wav_folder):
        os.makedirs(wav_folder)
    return base_folder, wav_folder


def synthesize_book(book_path, output_path):
    original_sentences, processed_sentences = preprocess_text(book_path)
    total_sentences = len(original_sentences)
    num_short = int(0.2 * total_sentences)
    num_medium = int(0.6 * total_sentences)
    num_long = total_sentences - num_short - num_medium
    sentence_pairs = list(zip(original_sentences, processed_sentences))
    short_sentences = [s for s in sentence_pairs if 1 <= len(word_tokenize(s[1])) <= 9][
        :num_short
    ]
    medium_sentences = [
        s for s in sentence_pairs if 10 <= len(word_tokenize(s[1])) <= 15
    ][:num_medium]
    long_sentences = [s for s in sentence_pairs if 16 <= len(word_tokenize(s[1]))][
        :num_long
    ]
    selected_sentences = short_sentences + medium_sentences + long_sentences
    tts = tts_runner()
    book_name = os.path.basename(book_path).split(".")[0]
    base_folder, wav_folder = create_output_folder(output_path)
    metadata_path = os.path.join(base_folder, "metadata.csv")
    with open(metadata_path, "w", encoding="utf-8", newline="") as meta_file:
        writer = csv.writer(meta_file, delimiter="|")
        for idx, (orig_sentence, proc_sentence) in enumerate(
            selected_sentences, start=1
        ):
            wav_filename = f"{book_name}_{idx:05d}.wav"
            final_path = os.path.join(wav_folder, wav_filename)
            audio = tts.run_tts(proc_sentence)
            audio.export(final_path, format="wav")
            writer.writerow([wav_filename[:-4], orig_sentence, proc_sentence])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesize a book into speech.")
    parser.add_argument(
        "--book_path", type=str, help="The book to synthesize.", required=True
    )
    parser.add_argument(
        "--output_path",
        type=str,
        help="The output path for the synthesized speech.",
        required=True,
    )
    args = parser.parse_args()
    synthesize_book(args.book_path, args.output_path)
