import os
import pandas as pd
from num2words import num2words
from tqdm import tqdm
import regex as re
from pathlib import Path

root_dirname = os.path.abspath(os.getcwd())
ted_talks_path = os.path.join(root_dirname, "Datasets", "ted_talks") # Contains 2 folders: output_files, transcript

ted_audio_path = os.path.join(ted_talks_path, "output_files") # Contains all folders. In folders are the wav files
ted_transcript_path = os.path.join(ted_talks_path, "transcript") # Contains all csvs

print("Root dirname", root_dirname)
print("Ted Talks path", ted_talks_path)
print("Ted Audio path", ted_audio_path)
print("Ted Transcript  path", ted_transcript_path)


def convert_num_to_words(utterance):
    numbers = re.findall("\d+", utterance)
    for num in sorted([int(i) for i in numbers], reverse=True):
        utterance  = utterance.replace(str(num), num2words(num))
    return utterance


def preprocess_single_ted_talk(transcript_path, audio_path, file_name):
    transcript_df = pd.read_csv(transcript_path)
    audience_sound_only_mask = transcript_df['text'].str.contains('^\s?[\[\(].+[\]\)]\s?$', regex=True) # '^\s?\(\w+\)\s?$'
    transcript_df['text'] = transcript_df['text'].apply(convert_num_to_words)
    transcript_df = transcript_df[~audience_sound_only_mask]['text'].str.lower()\
                .str.replace("\s?\w+\:\s?", "", regex=True)\
                .str.replace('[\[\(].+[\]\)]', '', regex=True)\
                .str.replace("[\"\?\.\!\:\,\-\;\-\']", "", regex=True)
                

    audio_file_name = os.listdir(audio_path)
    audio_file_size = []
    for audio in audio_file_name:
        audio_file_size.append(Path(os.path.join(audio_path, audio)).stat().st_size)
        
    ted_talk_df = pd.DataFrame({"file_name":audio_file_name}) # , "wav_filesize":audio_file_size
    ted_talk_df = pd.merge(ted_talk_df, transcript_df.rename('normalized_transcription'), left_index=True, right_index=True)
    
    ted_talk_df['file_name'] = ted_talk_df['file_name'].apply(lambda x: os.path.join("Datasets", "ted_talks", file_name, x))
    
    return ted_talk_df
    
    
def preprocess_all_ted_talks():
    combined_transcript_df = pd.DataFrame()
    # Combines all transcripts together
    for file_name in tqdm(os.listdir(ted_audio_path)):
        print(file_name)
        ted_talk_df = preprocess_single_ted_talk(\
                        transcript_path=os.path.join(ted_transcript_path, file_name+".csv"), \
                        audio_path=os.path.join(ted_audio_path, file_name), \
                        file_name=file_name)
        combined_transcript_df = pd.concat([combined_transcript_df, ted_talk_df])
        #break
        
    print(f"Saved metadata.csv to {ted_talks_path}")
    combined_transcript_df.to_csv(os.path.join(ted_talks_path, "metadata.csv"), index=False)
    
    print("DONE")
    
    
preprocess_all_ted_talks()