def transcribe_file(filepath: str) -> str:
    """
    you are given path, use model like whisper to transcribe it. 
    evaluate if you need to import model everytime you got the api call 
    should you have it install when docker image was built. 
    """
    print(f"Transcribing file: {filepath}")

    return f"Dummy transcription for file: {filepath}"
