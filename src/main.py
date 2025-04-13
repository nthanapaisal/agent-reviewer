from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Form
from pydantic import BaseModel
from typing import Optional
from typing import List
import shutil
import os
from backend.service import transcribe_audio, generate_prompts as generate_prompt_suggestions, evaluate_transcription, create_analysis, evaluate_conversation, read_all_reports, read_report_by_id, generate_reports_analysis, get_reports_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    transcription: str
    user_prompt: Optional[str] = None
    prompt_name: Optional[str] = None

class EvaluatorRequest(BaseModel):
    prompt: str

class AnalysisRequest(BaseModel):
    report: list[tuple[str, float, str]]
    summary: str

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            print(f"Temp file created: {temp_filename}")

        transcription = await transcribe_audio(temp_filename)
        return {"transcription": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/generate-prompts")
def generate_prompts(prompt_payload: PromptRequest):
    try:
        prompts = generate_prompt_suggestions(prompt_payload.transcription, prompt_payload.user_prompt, prompt_payload.prompt_name)
        return {"prompts": prompts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt generation failed: {str(e)}")


@app.post("/evaluate")
def evaluate(evaluator_payload: EvaluatorRequest):
    try:
        result = evaluate_transcription(evaluator_payload.prompt)
        return {"evaluation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/generate-report-analysis")
def generate_report_analysis(analysis_payload: AnalysisRequest):
    try:
        analysis = create_analysis(analysis_payload.report, analysis_payload.summary)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")

@app.post("/evaluate_audio")
async def evaluate_audio(
    file: UploadFile = File(...),                 # required
    employee_id: str = Form(...),
    user_prompt: Optional[str] = Form(None),      # optional, defaults to None
    prompt_name: Optional[str] = Form(None)       # optional, defaults to None
):
    temp_filename = f"temp_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            print(f"Temp file created: {temp_filename}")

        complete_analysis = await evaluate_conversation(temp_filename, employee_id, user_prompt, prompt_name)
        return complete_analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.get("/get-reports")
def get_reports():
    try:
        all_reports = read_all_reports()
        return all_reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")

@app.get("/get-report-id")
def get_report_id(job_id: str):
    try:
        report = read_report_by_id(job_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")

@app.post("/generate-overall-analysis")
def generate_overall_analysis():
    try:
        analysis = generate_reports_analysis()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")

@app.get("/get-overall-analysis")
def get_overall_analysis():
    try:
        analysis = get_reports_analysis()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")
