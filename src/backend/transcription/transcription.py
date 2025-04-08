import whisper
from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import re
import datetime

"""
Input: 
    string path to an audio file
Output:
    (
    Transcription: list of tuples (speaker, text),
    datetime: datetime object,
    duration length of the original audio file in milliseconds (ms):
    )
"""
def transcribe_file(filepath: str):
    time = datetime.datetime.now()
    temp_name = "audio.wav"
    
    audio = AudioSegment.from_file(filepath)
    duration = len(audio)
    
    file = pad_audio(filepath, temp_name)
    
    load_dotenv()
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.getenv("HUGGING_FACE"))
    dz = pipeline(file)
    
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(dz))

    # extract the diarization data into an easily parsable list
    dz = open('diarization.txt').read().splitlines()
    dzList = []
    for l in dz:
        start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
        start = millisec(start)
        end = millisec(end)
        lex = re.findall('\sSPEAKER_(\d\d)', string=l)
        dzList.append((start, end, lex[0]))
    
    print("---------------------") 
    print("Log: diarization done")
    print("---------------------")
    
    # available models: tiny, base, small, medium, large, turbo
    model = whisper.load_model("small")
    
    # for each segment transcribe it and append to the list
    transcription = []
    print("Log: adding items to transcription list")
    for item in dzList:
        audio = AudioSegment.from_wav(file)
        a = audio[item[0]: item[1]]
        a.export("a.wav", format="wav")
        result = model.transcribe("a.wav")
        transcription.append((item[2], result["text"]))
    
    print("-----------------------")
    print("Log: transcription done")
    print("-----------------------")
    
    # clean up temp files
    os.remove("a.wav")
    os.remove("audio.wav")
    os.remove("diarization.txt")

    return (transcription, time, duration)

# adds a blank 2 second pad to the beginning of the clip to ensure the model doesn't miss any audio
def pad_audio(filepath, output_name="audio.wav"):    
    audio = AudioSegment.from_file(filepath)
    spacermilli = 2000
    spacer = AudioSegment.silent(duration=spacermilli)
    audio = spacer.append(audio, crossfade=0)

    audio.export(output_name, format='wav')
    
    return output_name

def millisec(timeStr):
    spl = timeStr.split(":")
    s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
    return s
