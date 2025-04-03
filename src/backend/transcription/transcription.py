import whisper

def transcribe_file(filepath: str) -> str:
    """
    you are given path, use model like whisper to transcribe it. 
    evaluate if you need to import model everytime you got the api call 
    should you have it install when docker image was built. 
    """
    
    """
    {
    Transcription:,
    datetime:,
    duration:
    }
    where transcription is a list of tuples with key as speaker and value as line of text of that speaker
    """
    
    model = whisper.load_model("tiny")
    
    print(f"Transcribing file: {filepath}")

    return f"Dummy transcription for file: {filepath}"
