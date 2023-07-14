from pydub import AudioSegment
from pydub.utils import which
import subprocess
import urllib.parse
from datetime import datetime
import os



ffmpged_path = which("ffmpeg")
ffprobe_path = which("ffprobe")

AudioSegment.ffmpeg_path = "./ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
AudioSegment.ffprobe_path = "./ffmpeg-6.0-essentials_build/bin/ffprobe.exe"

# Convert the time stamps to milliseconds
def to_milliseconds(time_stamp):
    minutes, seconds = time_stamp.split(":")
    return (int(minutes) * 60 + int(seconds)) * 1000

def split_audio_by_time_stamps(time_stamps, input_file, output_dir):
    cleaned_input_file = urllib.parse.unquote(input_file).replace("file:///", "")

    time_stamps = [ts[0] for ts in time_stamps]
    time_stamps_ms = [to_milliseconds(ts) for ts in time_stamps]

    # Load the audio file using PyDub
    # audio = AudioSegment.from_file(input_file, format="mp3")
    audio = AudioSegment.from_file(cleaned_input_file, format="mp4")

    folder_name = os.path.splitext(os.path.basename(cleaned_input_file))[0]

    os.mkdir(os.path.join(output_dir, folder_name))

    # Loop through the time stamps and split the audio file
    for i in range(len(time_stamps_ms)-1):
        start = time_stamps_ms[i]
        end = time_stamps_ms[i+1]
        split_audio = audio[start:end]
        # output_file = output_dir + "output_" + str(i) + ".mp3"
        output_file = os.path.join(output_dir, folder_name, "output_" + str(i) + ".mp3")
        split_audio.export(output_file, format="mp3")

        # Use FFmpeg to add metadata to the output file
        subprocess.call(["ffmpeg", "-i", output_file, "-metadata", "title=output_" + str(i), "-y", output_file])
