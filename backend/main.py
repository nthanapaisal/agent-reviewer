from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi import Form
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from typing import List
import shutil
import os
from components.service import transcribe_audio, generate_prompts as generate_prompt_suggestions, evaluate_transcription, create_analysis, evaluate_conversation, read_all_reports, read_report_by_id, generate_reports_analysis, get_reports_analysis
from fastapi import WebSocket

active_connections: List[WebSocket] = []

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except:
        active_connections.remove(websocket)

async def notify_frontend_ws(analysis: dict):
    for conn in active_connections:
        try:
            await conn.send_json({"event": "new_analysis", "summary": "New analysis generated"})
        except:
            active_connections.remove(conn)
            
async def trigger_background_analysis():
    analysis = generate_reports_analysis()
    await notify_frontend_ws(analysis)

app = FastAPI()

class PromptRequest(BaseModel):
    transcription: str
    user_prompt: Optional[str] = None
    prompt_name: Optional[str] = None

class EvaluatorRequest(BaseModel):
    prompt: str

class AnalysisRequest(BaseModel):
    report: list[tuple[str, int, str]]
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
        analysis = create_analysis(analysis_payload.report)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")

@app.post("/evaluate_audio")
async def evaluate_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    employee_id: str = Form(...),
    user_prompt: Optional[str] = Form(None),
    prompt_name: Optional[str] = Form(None)
):
    temp_filename = f"temp_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        complete_analysis = await evaluate_conversation(temp_filename, employee_id, user_prompt, prompt_name)

        # Trigger background analysis after transcription completes
        background_tasks.add_task(trigger_background_analysis)

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
