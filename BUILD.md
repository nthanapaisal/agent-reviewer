# Building the App

## 0. Pyannote.audio API key

Accept pyannote.audio terms for segmentation-3.0 and diarization-3.1 and generate an API key as directed [here](https://github.com/pyannote/pyannote-audio?tab=readme-ov-file#tldr)

Create a file ```.env``` in the ```/backend/src``` directory with the key ```HUGGING_FACE="your_api_key_here"```

## 1. Docker Compose (recommended)
1. docker-compose up --build
2. check if the ollama has been pulled into the volumne: docker exec -it ollama ollama list
3. http://127.0.0.1:8000/docs - endpoints
4. http://localhost:3000 - frontend
4. ctrlc and.. choose one below
   1.    stop+remove containers, but keep image and volume: docker-compose down
   2.    OR stop and delete containers and images: docker-compose down --rmi all
   3.    OR stop and delete EVERYTHING + volume: docker-compose down --rmi all --volumes
Explaination: 
- 3 containers: Ollama, Backend API, Frontend React app
- Custom Ollama Image: You build a custom image on top of the official ollama/ollama image (via Dockerfile.ollama).
- Volume Mount: A Docker volume (e.g., ollama_data) is mounted to /root/.ollama inside the container.
- Container Startup & Entrypoint Script: starts the Ollama server and ollama pull mistral into /root/.ollama.

## 2. Docker
1. docker build -t agent-reviewer .
2. docker run -p 127.0.0.1:8000:8000 agent-reviewer
3. http://127.0.0.1:8000/docs
4. ctrl+c
   not needed since you can build and overwrite previous image with same name but clean up process
   1. check running containers: docker ps -a
   2. stop running and remove manually: docker rm -f <container_id>
   3. check images: docker images
   4. remove image to free up space in your machine!!: docker rmi agent-reviewer

## 3. Conda (or Venv)
1. conda create -n agent-reviewer python=3.11 -y
2. conda activate agent-reviewer
3. pip install -r requirements.txt
4. PYTHONPATH=./backend uvicorn main:app --reload
   1. to kill process do: kill -9 $(lsof -ti :8000)
   2. http://127.0.0.1:8000/docs

---

Example input/output:

1. audio -> transcription
2. "transcription" -> prompt + transcription integration
3. prompt + transcription -> evaluation

---

Dependencies listed in [requirements.txt](./requirements.txt)
