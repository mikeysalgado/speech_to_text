# Ted-Talk_Scraper

This README contains all the details for our project submission.

Github Repository is found here: https://github.com/MikeSalgado/Ted-Talk_Scraper

## Setup Environment
This is to create the SpeechToTextVenv folder in this repo if you don't have it already. You must delete the old folder before running this.

```bash
$ setup_venv.bat
```

## Run Model (Not Complete)
This is to run the sr_script.py file which lets you feed in audio for the model to predict text. Currently this doesn't work in real time since we have trouble setting up our environment to grab audio input device without using anaconda or a virtual machine (Ubuntu)

```bash
$ run_script.bat
```

## Testing the Model
Running this python script and passing in a wav file will print the transcription that the model output. All our wav files are in the output_files folder. Change the 

Run this with the current working directory in the github repository.
```bash
$ SpeechToTextVenv\Scripts\activate
$ python .\sr_script.py "output_files\2007-david-gallo-006-5000k\output_0.wav"
```

## Our Model

We included our trained model named model_prototype.ckpt that we trained in an Ubuntu environment. The model was trained on a single Ted talk since we had to use our local machine which is fairly weak and training on audio files is intensive. We couldn't set up a training environment on Rosie since it required us to sudo apt-get audio modules which we don't have access to do on Rosie. The code used to train the model could be found here: https://github.com/LearnedVector/A-Hackers-AI-Voice-Assistant. 

This model was not possible to run on windows and required a lot of setup to load in an Ubuntu environment so we decided to use SpeechRecognition to submit as our model prototype (https://github.com/Uberi/speech_recognition) since we can actually set up a working demo.

# Training Data
The transcripts and wav audio data could be found here: https://msoe.app.box.com/s/e4tre8q5m7c43ljpfwviklvywvtneqj9
- Folders in the audio directory are separated by Ted Talks.
- There is a train.csv and test.csv file in this github repository that has the example of what the transcribed text is for each audio segment. 
   - All the transcripts could be found here: https://msoe.app.box.com/s/0dkiyworh3bydjx39hki626wglhbfxvg
