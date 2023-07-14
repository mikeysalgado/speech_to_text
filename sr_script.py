import sys
import os
import csv
import random
import speech_recognition as sr

folder_path = 'output_files\\2007-david-gallo-006-5000k'
transcription_path = 'transcript\\2007-david-gallo-006-5000k.csv'

import numpy as np

def wer(expected, predicted):
    """
    Computes the Word Error Rate (WER) between two text sequences.
    """
    # Split the text sequences into individual words
    expected_words = expected.split()
    predicted_words = predicted.split()

    # Create a matrix of edit distances between all pairs of words
    n = len(expected_words)
    m = len(predicted_words)
    distances = np.zeros((n+1, m+1))
    for i in range(n+1):
        distances[i, 0] = i
    for j in range(m+1):
        distances[0, j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            if expected_words[i-1] == predicted_words[j-1]:
                distances[i, j] = distances[i-1, j-1]
            else:
                substitution = distances[i-1, j-1] + 1
                insertion = distances[i, j-1] + 1
                deletion = distances[i-1, j] + 1
                distances[i, j] = min(substitution, insertion, deletion)

    # Return the WER
    return distances[n, m] / n


def transcribe_audio(audio):
    r = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = r.record(source)

    try:
        transcript = r.recognize_sphinx(audio_data)
        return transcript
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
        return None

def transcribe_audio_realtime():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Recording started. Speak now...")

        while True:
            audio_data = r.listen(source, phrase_time_limit=5)

            try:
                transcript = r.recognize_sphinx(audio_data)
                print("Transcription: " + transcript)
            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Speech Recognition service; {0}".format(e))


def test_transcription():
    texts = []
    with open(transcription_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            texts.append(row[1])

    wer_scores = []
    file_idx = 0
    wav_files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
    sorted_files = sorted(wav_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    for file in sorted_files:
        wav_path = os.path.join(folder_path, file).replace('\\', '/')
        print(wav_path)
        if os.path.isfile(wav_path):
            print(f"Test {file_idx + 1}/{len(texts)}")
            expected_output = texts[file_idx]
            print(f"Expected Output: {expected_output}")
            predicted_output = transcribe_audio(wav_path)
            print(f"Predicted Output: {predicted_output}")
            wer_score = wer(expected_output, predicted_output)
            print("WER: ", wer_score)
            wer_scores.append(wer_score)
            print()
            file_idx += 1
    average_wer = sum(wer_scores) / len(wer_scores)
    print(f"The average WER score was {average_wer}.\nThis means that {average_wer * 100}% of the words in the expected output were incorrect in the predictions\n")

if __name__ == '__main__':
    test_transcription()
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if not os.path.isfile(audio_file):
            print("Error: File not found.")
            sys.exit(1)

        transcript = transcribe_audio(audio_file)

        if transcript is not None:
            print("Transcription: " + transcript)
    else:
        transcribe_audio_realtime()


