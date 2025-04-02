import json
from typing import List
import spacy

def load_json(filepath: str):
    """ Load JSON file """
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_keywords(user_prompt: str) -> List[str]:
    """
    Extract key phrases from user_prompt using NLP.
    """
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_prompt)
    
    # Extract complete n. chunks
    noun_phrases = {chunk.text.lower() for chunk in doc.noun_chunks}

    keywords = set()
    for token in doc:
        if token.pos_ == "ADJ" and token.head.pos_ == "NOUN":
            phrase = f"{token.text} {token.head.text}".lower()
            keywords.add(phrase)
        elif token.pos_ == "NOUN" or token.pos_ == "ADJ":
            keywords.add(token.text.lower())

    # Avoid duplicate n. without adj. exists
    filtered_keywords = {kw for kw in keywords if not any(kw in phrase and kw != phrase for phrase in noun_phrases)}

    return list(filtered_keywords)


def build_prompt(transcription: str, user_prompt: str, prompt_name: str = "template") -> str:
    """
    Construct a system prompt based on the conversation transcription, user-defined metrics, and selected prompt template.
    """
    # Load predefined metrics and system templates
    metrics = load_json("./src/configs/metrics.json")
    prompts = load_json("./src/configs/prompts.json")
    
    # Ensure the user_prompt is not empty, pad it if necessary
    if not user_prompt:
        user_prompt = prompts["default"]
    
    # Extract key points from user_prompt
    extracted_keywords = extract_keywords(user_prompt)
    
    # Add a default metric if necessary
    prompt_template = prompts.get(prompt_name, prompts["template"])
    
    # Format the prompt with predefined metrics and user input
    formatted_prompt = prompt_template.format(
        transcription=transcription,
        metrics=", ".join(metrics["metrics"]),
        user_prompt=", ".join(extracted_keywords) if extracted_keywords else user_prompt
    )
    
    return formatted_prompt
