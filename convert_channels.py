from pydub import AudioSegment
import os

directory_path = "C:/Users/salgadom/Documents/CS 4980 003/Data/wav_files/2002-richard-dawkins-001-1200k"

import os
from pydub import AudioSegment

# Set the directory paths for input and output folders
input_directory = "C:/Users/salgadom/Documents/CS 4980 003/Data/wav_files/2002-richard-dawkins-001-1200k"
output_directory = "C:/Users/salgadom/Documents/CS 4980 003/Data/wav_files/2002-richard-dawkins-001-1200k-mono"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get a list of all the WAV files in the input directory
wav_files = [f for f in os.listdir(input_directory) if f.endswith(".wav")]

# Loop through each WAV file in the directory
for wav_file in wav_files:
    # Load the audio file
    # print(os.path.join(input_directory, wav_file))
    audio = AudioSegment.from_wav(os.path.join(input_directory, wav_file))
    
    # Split the audio into two separate channels
    left_channel = audio.split_to_mono()[0]
    
    # Construct the output filename
    output_filename = os.path.splitext(wav_file)[0] + "_mono.wav"
    
    # Export the left channel as a new mono audio file to the output directory
    left_channel.export(os.path.join(output_directory, output_filename), format="wav")

    # Check if the file has only one channel
    if left_channel.channels != 1:
        print(f"Error: {left_channel} is not mono")
    else:
        print(f"{left_channel} is mono")

