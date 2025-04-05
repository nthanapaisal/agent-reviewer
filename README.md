# Conda instruction
I used mini conda currently since we dont have docker yet. to run:
1. conda create -n agent-reviewer python=3.11 -y
2. conda activate agent-reviewer
3. pip install -r requirements.txt
4. PYTHONPATH=./src uvicorn main:app --reload
   1. to kill process do: kill -9 $(lsof -ti :8000)
   2. http://127.0.0.1:8000/docs

# Docker instructions
1. docker build -t agent-reviewer .
2. docker run -p 127.0.0.1:8000:8000 agent-reviewer

---

Example input/output:

1. audio (check data dir) -> transcription
2. "transcription" -> prompt + transcription integration
3. prompt + transcription -> evaluation
