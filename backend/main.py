from fastapi import FastAPI, UploadFile, File, HTTPException, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os
from src.service import transcribe_audio, generate_prompts as generate_prompt_suggestions, evaluate_transcription, create_analysis, evaluate_conversation, read_all_reports, read_report_by_id, read_reports_by_employee, generate_reports_analysis, generate_employee_analysis, get_reports_analysis, get_prompt_options

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
    metric_name: Optional[str] = None

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
        prompts = generate_prompt_suggestions(prompt_payload.transcription, prompt_payload.user_prompt, prompt_payload.metric_name)
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
    metric_name: Optional[str] = Form(None)       # optional, defaults to None
):
    temp_filename = f"temp_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            print(f"Temp file created: {temp_filename}")

        complete_analysis = await evaluate_conversation(temp_filename, employee_id, user_prompt, metric_name)
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
    
@app.get("/get-report-employee")
def get_report_id(employee_id: str):
    try:
        report = read_reports_by_employee(employee_id)
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
    
@app.post("/generate-employee-analysis")
def get_employee_analysis(employee_id: str):
    try:
        analysis = generate_employee_analysis(employee_id)
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
    
@app.get("/get-prompt-options")
def get_prompt_options_route():
    try:
        options = get_prompt_options()
        return {"prompt_options": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/reports")
async def websocket_get_reports(websocket: WebSocket):
    await websocket.accept()
    try:
        all_reports = read_all_reports()
        await websocket.send_json(all_reports)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@app.websocket("/ws/overall-analysis")
async def websocket_get_overall_analysis(websocket: WebSocket):
    await websocket.accept()
    try:
        generate_reports_analysis()
        analysis = get_reports_analysis()
        await websocket.send_json(analysis)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
