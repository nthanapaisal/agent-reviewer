import whisper
from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import re
import datetime

# Load the Whisper model globally
whisper_model = whisper.load_model("small")

def map_speakers(transcription):
    """
    Convert a transcription list of tuples into a single formatted string,
    mapping each unique speaker ID to an alphabetical label (A, B, …).

    Args:
        transcription (list of tuple): Each tuple is (speaker_id, text)

    Returns:
        str: A string with each line prefixed by the speaker label.
    """
    speaker_map = {}
    next_label = ord("A")
    formatted_lines = []
    
    for speaker_id, text in transcription:
        # If speaker_id hasn't been seen, assign the next available label.
        if speaker_id not in speaker_map:
            speaker_map[speaker_id] = chr(next_label)
            next_label += 1
        # Get the letter for the speaker.
        label = speaker_map[speaker_id]
        # Strip extra whitespace and format the line.
        formatted_lines.append(f"{label}: {text.strip()}")
    
    # Join lines with a space (or newline if you prefer).
    return " ".join(formatted_lines)

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
    
    # Use the pre-loaded Whisper model
    model = whisper_model  # No need to load it again
    
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
    
    transcription_final = map_speakers(transcription)

    return (transcription_final, time, duration)

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
