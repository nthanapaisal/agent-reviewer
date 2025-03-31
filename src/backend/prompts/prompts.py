from typing import List

def build_prompt(transcription: str, user_prompt: str) -> str:
    """
    You are given transcription stirng and user prompt. 
    build prompt by mixing transcription and userprompt into system prompt that will be in configs/prompts.json
    think of configs/prompts.json as template prompt, "you are agent evaluator, evalute this conversation {transcription}, with these metrics x y z and {user prompt}"
    """
    print(f"Generating prompts for: {transcription}")
    # read json, build prompt, return, think about basic template metrics too
    sys_prompt = "sys_prompt" #from json

    return f"""
        Base Metrics: {sys_prompt}
        Summarize this sentence: {transcription}
        Metrics: {user_prompt}
    """
