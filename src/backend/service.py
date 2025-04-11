from backend.transcription.transcription import transcribe_file
from backend.prompts.prompts import build_prompt
from backend.evaluator.evaluator import evaluate_transcription_quality
from backend.analysis.analysis import generate_analysis
import uuid
import json
import os
from fastapi import HTTPException

async def transcribe_audio(filepath: str):
    return transcribe_file(filepath)

def generate_prompts(transcription: str, user_prompt: str, prompt_name: str):
    return build_prompt(transcription, user_prompt, prompt_name)

def evaluate_transcription(prompt: str):
    return evaluate_transcription_quality(prompt)

def create_analysis(evaluation: list[tuple[str, int, str]]):
    return generate_analysis(evaluation)

async def evaluate_conversation(filepath: str, user_prompt: str, prompt_name: str) -> dict:

    #generate uuid
    job_id = str(uuid.uuid4())

    transcription_final, timestamp, duration = transcribe_file(filepath)
    prompt_payload, user_prompt, prompt_name = build_prompt(transcription_final, user_prompt, prompt_name)
    result = evaluate_transcription_quality(prompt_payload)
    print(result)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM output is not valid JSON:\n{result}\n\nError: {e}")

    complete_analysis = {
        "job_id": job_id,
        "submission_date_time": timestamp.isoformat(),
        "audio_duration": duration, 
        "transcription": transcription_final,
        "input_user_prompt": user_prompt,
        "input_prompt_name": prompt_name,
        "prompt_payload": prompt_payload,
        "evaluated_transcription": result["report"],
        "evaluate_summary": result["summary"]
    }

    print("-----------------------")
    print("Log: completed final report")
    print("-----------------------")

    # save to database 
    os.makedirs("./reports", exist_ok=True)
    output_path = f"./reports/{job_id}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(complete_analysis, f, indent=2, ensure_ascii=False)

    return complete_analysis

def read_report_by_id(job_id: str):
    report_path = f"./reports/{job_id}.json"

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report with ID '{job_id}' not found.")

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Report file '{job_id}.json' is not valid JSON.")

    return report_data
