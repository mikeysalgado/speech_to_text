import pyaudio
import threading
import time
import argparse
import wave
import torchaudio
import torch
import sys
import numpy as np
###from neuralnet.dataset import get_featurizer
###from decoder import DecodeGreedy, CTCBeamDecoder
from threading import Event

###from model import SpeechRecognition
#import torch
#import torch.nn as nn
#from torch.nn import functional as F

# Nick - For my own reference
#Documents\NLPvenv\Scripts\activate
#python Documents\mltu\Tutorials\05_sound_to_text\myEngine.py --model_file Models\05_sound_to_text\202305031703

#Documents\NLPvenv\Scripts\activate
#python Documents\mltu\Tutorials\05_sound_to_text\inferenceModel.py

# 5120
#Documents\NLPvenv\Scripts\activate && python Documents\mltu\Tutorials\05_sound_to_text\myEngine.py --model_file Models\latest_model

from tensorflow import keras

import torch.nn as nn
from mltu.configs import BaseModelConfigs
from mltu.inferenceModel import OnnxInferenceModel
from mltu.preprocessors import WavReader
from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer
import typing
import os

class LogMelSpec(nn.Module):

    def __init__(self, sample_rate=8000, n_mels=128, win_length=160, hop_length=80):
        super(LogMelSpec, self).__init__()
        self.transform = torchaudio.transforms.MelSpectrogram(
                            sample_rate=sample_rate, n_mels=n_mels,
                            win_length=win_length, hop_length=hop_length)

    def forward(self, x):
        x = self.transform(x)  # mel spectrogram
        x = np.log(x + 1e-14)  # logrithmic, add small value to avoid inf
        return x

# EXPECT 1392, 193
def get_featurizer(sample_rate, n_feats=1392): # n_feats=81
    return LogMelSpec(sample_rate=sample_rate, n_mels=n_feats,  win_length=160, hop_length=26) # win_length=160, hop_length=80



class Listener:

    def __init__(self, sample_rate=8000, record_seconds=2):
        self.chunk = 2048
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)

    def listen(self, queue):
        while True:
            data = self.stream.read(self.chunk , exception_on_overflow=False)
            queue.append(data)
            time.sleep(0.01)

    def run(self, queue):
        thread = threading.Thread(target=self.listen, args=(queue,), daemon=True)
        thread.start()
        print("\Speech Recognition engine is now listening... \n")



class WavToTextModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list
        self.listener = Listener(sample_rate=8000)
        self.featurizer = get_featurizer(8000)
        
        self.root_dirname = os.path.dirname(os.path.abspath(__file__))
        

    def predict(self, audio):
        with torch.no_grad():
            fname = self.save(audio)
            #waveform, _ = torchaudio.load(fname)  # don't normalize on train
            #print("Waveform shape", waveform.shape)
            #input_featurizer = self.featurizer(waveform).numpy()
            #input_featurizer = np.delete(input_featurizer, [-4, -3,-2,-1], axis=2)
            #log_mel = self.featurizer(waveform).unsqueeze(1)
            #data_pred = np.expand_dims(log_mel, axis=0)
            #preds = self.model.run(None, {self.input_name: input_featurizer})[0]
            #text = ctc_decoder(preds, self.char_list)[0]
            
            spectrogram = WavReader.get_spectrogram(fname, frame_length=256, frame_step=160, fft_length=384)
            print("Spectrogram", type(spectrogram), spectrogram.shape)
            padded_spectrogram = np.pad(spectrogram, ((1392 - spectrogram.shape[0], 0),(0,0)), mode='constant', constant_values=0)
            print("padded_spectrogram", type(padded_spectrogram), padded_spectrogram.shape)
            data_pred = np.expand_dims(padded_spectrogram, axis=0)
            preds = self.model.run(None, {self.input_name: data_pred})[0]
            text = ctc_decoder(preds, self.char_list)[0]
            
            
        return text
        
    # FROM ENGINE.py
    def save(self, waveforms, fname="audio_temp.wav"):
        fname = os.path.join(self.root_dirname, fname)
        wf = wave.open(fname, "wb")
        # set the channels
        wf.setnchannels(1)
        # set the sample format
        wf.setsampwidth(self.listener.p.get_sample_size(pyaudio.paInt16))
        # set the sample rate
        wf.setframerate(8000)
        # write the frames as bytes
        wf.writeframes(b"".join(waveforms))
        # close the file
        wf.close()
        return fname

        
    
        
class SpeechRecognitionEngine:

    def __init__(self, model_file, ken_lm_file, context_length=10):
        self.listener = Listener(sample_rate=8000)
        
        root_dirname = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(root_dirname, model_file)
        print("Root dirname:", root_dirname)
        print("Model path:", model_path)
        configs = BaseModelConfigs.load(os.path.join(model_path, "configs.yaml"))
        model = WavToTextModel(model_path=model_path, char_list=configs.vocab, force_cpu=False)
        self.model = model
        """      
        checkpoint = torch.load(model_file)
        print(checkpoint.keys())
        
        prefix = 'model.'
        n_clip = len(prefix)
        checkpoint['state_dict'] = {k[n_clip:]: v for k, v in checkpoint['state_dict'].items()
                if k.startswith(prefix)}
                
        print(checkpoint['state_dict'].keys())
        h_params = {
        "num_classes": 29,
        "n_feats": 81,
        "dropout": 0.1,
        "num_layers": 1}
        #self.model = Net(checkpoint['state_dict'])
        model = SpeechRecognition(**SpeechRecognition.hyper_parameters)
        model.load_state_dict(checkpoint['state_dict'])
        self.model = model
        print(type(self.model), self.model)
        #self.model = SpeechRecognition(checkpoint['state_dict'], **h_params)#**SpeechRecognition.hyper_parameters

        #optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        #epoch = checkpoint['epoch']
        #loss = checkpoint['loss']
        
        #self.model = torch.jit.load(model_file)
        self.model.eval().to('cpu')  #run on cpu
        """
        self.featurizer = get_featurizer(8000)
        
        self.audio_q = list()
        """
        self.hidden = (torch.zeros(1, 1, 1024), torch.zeros(1, 1, 1024))
        self.beam_results = ""
        self.out_args = None
        self.beam_search = CTCBeamDecoder(beam_size=100, kenlm_path=ken_lm_file)
        self.context_length = context_length * 50 # multiply by 50 because each 50 from output frame is 1 second
        self.start = False
        """

    
    """
    def predict(self, audio):
        with torch.no_grad():
            fname = self.save(audio)
            waveform, _ = torchaudio.load(fname)  # don't normalize on train
            log_mel = self.featurizer(waveform).unsqueeze(1)
            out, self.hidden = self.model(log_mel, self.hidden)
            out = torch.nn.functional.softmax(out, dim=2)
            out = out.transpose(0, 1)
            self.out_args = out if self.out_args is None else torch.cat((self.out_args, out), dim=1)
            #print(torch.cat((self.out_args, out), dim=1).size(), torch.cat((self.out_args, out), dim=1))
            #print("OUT ARGS:", type(self.out_args), (self.out_args).size(), (self.out_args[0]).size())
            results = self.beam_search(self.out_args[0])
            current_context_length = self.out_args.shape[1] / 50  # in seconds
            if self.out_args.shape[1] > self.context_length:
                self.out_args = None
            return results, current_context_length
    """

    def inference_loop(self, action):
        while True:
            #print("INFERENCE LOOP")
            if len(self.audio_q) < 5:
                continue
            else:
                pred_q = self.audio_q.copy()
                self.audio_q.clear()
                action(self.model.predict(pred_q))
                results = self.model.predict(pred_q)
                print("Prediction\n\n", "-"*30)
                print(results)
            time.sleep(0.05)

    def run(self, action):
        self.listener.run(self.audio_q)
        thread = threading.Thread(target=self.inference_loop,
                                    args=(action,), daemon=True)
        thread.start()


class DemoAction:

    def __init__(self):
        self.asr_results = ""
        self.current_beam = ""

    def __call__(self, x):
        #results, current_context_length = x
        results = x
        self.current_beam = results
        trascript = " ".join(self.asr_results.split() + results.split())
        #print(trascript)
        #if current_context_length > 10:
        #    self.asr_results = trascript

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="demoing the speech recognition engine in terminal.")
    parser.add_argument('--model_file', type=str, default=None, required=True,
                        help='optimized file to load. use optimize_graph.py')
    parser.add_argument('--ken_lm_file', type=str, default=None, required=False,
                        help='If you have an ngram lm use to decode')

    args = parser.parse_args()
    asr_engine = SpeechRecognitionEngine(args.model_file, args.ken_lm_file)
    action = DemoAction()

    asr_engine.run(action)
    threading.Event().wait()
    # activate speech recognition engine