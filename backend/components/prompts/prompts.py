import json
from typing import List
import spacy
from fastapi import HTTPException
from typing import Optional
import re
import json

spacy.cli.download("en_core_web_sm")

def load_json(filepath: str):
    """ Load JSON file """
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_keywords(user_prompt: str) -> List[str]:
    """
    Extract key phrases from user_prompt using NLP.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_prompt)
    
    keywords = set()
    for token, next_token in zip(doc, list(doc)[1:] + [None]):
        if next_token is not None and token.pos_ == "ADJ" and next_token.pos_ == "NOUN":
            phrase = f"{token.text} {next_token.text}".lower()
            keywords.add(phrase)
        elif token.pos_ == "NOUN" or token.pos_ == "ADJ":
            keywords.add(token.text.lower())

    # Avoid duplicate n. without adj. exists
    filtered_keywords = {kw for kw in keywords if not any(kw in other and kw != other for other in keywords)}

    return list(filtered_keywords)

def build_prompt(transcription: str, user_prompt: Optional[str], prompt_name: Optional[str]):
    
    print("-----------------------")
    print("Log: constructing prompts_payload")
    print("-----------------------")

    # Load your configs
    metrics = load_json("./src/configs/metrics.json")
    prompts = load_json("./src/configs/prompts.json")

    # Use default for prompt_name if it is None or empty, had to do it this way instead of via param
    prompt_name = prompt_name or "customer_service_metrics"

    # Check if the prompt_name exists in metrics
    if prompt_name not in metrics:
        raise HTTPException(status_code=400, detail=f"Unknown prompt_name: '{prompt_name}'")

    if not user_prompt:
        user_prompt = ", ".join(metrics[prompt_name].keys())

    # Optionally, you might extract keywords if needed:
    extracted_keywords = extract_keywords(user_prompt)

    # Get the prompt template
    prompt_template = prompts["template"]

    # Format the final prompt
    try:
        formatted_prompt = prompt_template.format(
            transcription=transcription,
            metrics=", ".join(metrics[prompt_name].keys()),  # or change to a different default if needed
            user_prompt=", ".join(extracted_keywords) if extracted_keywords else user_prompt
        )
    except Exception as e:
        raise ValueError(f"Prompt generation failed: {str(e)}")

    print("-----------------------")
    print("Log: completed construction prompts_payload")
    print("-----------------------")
    
    return (formatted_prompt, user_prompt, prompt_name)

