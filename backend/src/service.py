from src.transcription.transcription import transcribe_file
from src.prompts.prompts import build_prompt
from src.evaluator.evaluator import evaluate_transcription_quality
from src.analysis.analysis import generate_analysis
from src.analysis.general_analysis import extract_evaluated_metrics, create_trend_graphs, compute_overall_performance_percentages
import uuid
import json
import os
from fastapi import HTTPException

async def transcribe_audio(filepath: str):
    return transcribe_file(filepath)

def generate_prompts(transcription: str, user_prompt: str, metric_name: str):
    return build_prompt(transcription, user_prompt, metric_name)

def evaluate_transcription(prompt: str):
    return evaluate_transcription_quality(prompt)

def create_analysis(evaluation: list[tuple[str, int, str]]):
    return generate_analysis(evaluation)

async def evaluate_conversation(filepath: str, employee_id: str, user_prompt: str, metric_name: str) -> dict:

    print("-----------------------")
    print(f"Log: evaluating conversation audio")
    print("-----------------------")

    #generate uuid
    job_id = str(uuid.uuid4())

    transcription_final, timestamp, duration = transcribe_file(filepath)
    prompt_payload, user_prompt, metric_name = build_prompt(transcription_final, user_prompt, metric_name)
    result = evaluate_transcription_quality(prompt_payload)
    print(result)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM output is not valid JSON:\n{result}\n\nError: {e}")

    complete_analysis = {
        "job_id": job_id,
        "employee_id": employee_id,
        "submission_date_time": timestamp,
        "audio_duration": duration, 
        "transcription": transcription_final,
        "input_user_prompt": user_prompt,
        "input_metric_name": metric_name,
        "prompt_payload": prompt_payload,
        "evaluated_transcription": result["report"],
        "evaluate_summary": result["summary"]
    }

    # save to database 
    os.makedirs("./reports", exist_ok=True)
    output_path = "./reports/all_reports.json"

    # Load existing data if file exists, otherwise start with empty dict
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            all_reports = json.load(f)
    else:
        all_reports = {}

    # Add or update the current job's report
    all_reports[job_id] = complete_analysis

    # Save back to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_reports, f, indent=2, ensure_ascii=False)

    print("-----------------------")
    print(f"Log: completed final report and saved to all_reports.json for job_id {job_id}")
    print("-----------------------")

    return complete_analysis

def read_all_reports():
    print("-----------------------")
    print(f"Log: reading all reports in the database")
    print("-----------------------")

    report_path = "./reports/all_reports.json"

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report database not found.")

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            all_reports = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Report database is not valid JSON.")
        
    return all_reports
    
def read_report_by_id(job_id: str):
    print("-----------------------")
    print(f"Log: retriving a report for {job_id}")
    print("-----------------------")

    all_reports = read_all_reports()

    if job_id not in all_reports:
        print("Log: job_id doesn't exist")
        return "job_id doesn't exist"

    return all_reports[job_id]

def read_reports_by_employee(employee_id: str):
    print("-----------------------")
    print(f"Log: retrieving all reports for employee_id: {employee_id}")
    print("-----------------------")

    all_reports = read_all_reports()

    employee_reports = {
        job_id: report for job_id, report in all_reports.items()
        if report.get("employee_id") == employee_id
    }

    if not employee_reports:
        raise HTTPException(status_code=404, detail=f"No reports found for employee_id: {employee_id}")

    return employee_reports

def generate_reports_analysis():
    print("-----------------------")
    print(f"Log: generating overall analysis for all reports")
    print("-----------------------")

    all_reports = read_all_reports()

    # Trend Analysis
    metrics_data = extract_evaluated_metrics(all_reports)
    metrics_data_with_graphs64 = create_trend_graphs(metrics_data)

    # Overall Analysis
    overall_performance_percentages = compute_overall_performance_percentages(metrics_data)

    # Combine the data into a single dictionary
    overall_analysis = {
        "metrics_data": metrics_data_with_graphs64,
        "overall_performance_data": overall_performance_percentages
    }

    # Save the overall analysis to a JSON file
    os.makedirs("./analysis", exist_ok=True)
    with open('./analysis/overall_analysis.json', 'w') as f:
        json.dump(overall_analysis, f, indent=4)

    print("-----------------------")
    print(f"Log: completed overall analysis for all reports")
    print("-----------------------")

    return overall_analysis

def generate_employee_analysis(employee_id: str):
    print("-----------------------")
    print(f"Log: generating analysis for employee_id: {employee_id}")
    print("-----------------------")

    employee_reports = read_reports_by_employee(employee_id)

    # Trend Analysis
    metrics_data = extract_evaluated_metrics(employee_reports)
    metrics_data_with_graphs64 = create_trend_graphs(metrics_data)

    # Overall Analysis
    overall_performance_percentages = compute_overall_performance_percentages(metrics_data)

    employee_analysis = {
        "employee_id": employee_id,
        "metrics_data": metrics_data_with_graphs64,
        "overall_performance_data": overall_performance_percentages
    }

    # Optionally save to file
    os.makedirs("./analysis/employee", exist_ok=True)
    output_path = f'./analysis/employee/{employee_id}_analysis.json'
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(employee_analysis, f, indent=4)

    print("-----------------------")
    print(f"Log: completed analysis for employee_id {employee_id}")
    print("-----------------------")

    return employee_analysis

    
def get_reports_analysis():
    print("-----------------------")
    print(f"Log: reading analysis in the database")
    print("-----------------------")

    file_path = './analysis/overall_analysis.json'
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report database not found.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Report database is not valid JSON.")

    return analysis

def get_prompt_options():
    metrics_path = os.path.join(os.path.dirname(__file__), "../configs/metrics.json")
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to load prompt options: {e}")
