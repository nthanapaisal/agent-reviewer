Instruction
# I used mini conda currently since we dont have docker yet. to run:
# conda create -n agent-reviewer python=3.11 -y
# conda activate agent-reviewer
# pip install -r requirements.txt
# uvicorn src.main:app --reload
# notes: to kill process do: kill -9 $(lsof -ti :8000)
# http://127.0.0.1:8000/docs

Example input/output:

1. audio (check data dir) -> transcription

2. "transcription" -> prompt + transcription integration

3. prompt + transcription -> evaluation
