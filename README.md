# 🎧 Agent Reviewer

Agent Reviewer is a powerful application designed to evaluate call center personnel by analyzing audio recordings. It provides in-depth assessments using a combination of built-in and user customizable metrics, delivering actionable business insights from every conversation.

## 🚀 Features

- Audio Processing: Upload audio files directly, no pre-processing or conversion required.
- Format Support: Compatible with all common audio formats (mp3, wav, etc.).
- Automated Evaluation: Assess agent performance with powerful LLM analytics.
- Custom Metrics: Supply additional evaluation criteria to fit your business case.
- Business Insights: Extract trends, sentiment, and customer satisfaction indicators.

## 💼 Use Cases

- Quality assurance for customer service teams
- Agent performance benchmarking
- Identification of training opportunities
- Measuring customer sentiment and engagement

## 🛠️ How It Works

1. <b>Upload</b> a call recording through the app interface.
2. <b>Process</b> the audio using built-in or user-supplied metrics.
3. <b>Review</b> an automatically generated evaluation report.
4. <b>Analyze</b> employee trends and insights across multiple recordings.

## 📦 Quick Start

1. Agree to the Pyannote.audio [terms](https://github.com/pyannote/pyannote-audio?tab=readme-ov-file#tldr)

2. A Hugging Face API key must be supplied in a ```.env``` file in ```/backend/src``` directory
HUGGING_FACE="your_api_key_here"

```
git clone https://github.com/nthanapaisal/agent-reviewer
cd agent-reviewer
docker compose up --build -d
```

Further documentation  located in [BUILD.md](./BUILD.md)

## ⚙️ Pipeline (simplified)

1. Speaker Diarization: pyannote.audio
2. Audio Transcription: openai-whisper
3. Prompt Construction: Spacy
4. Analysis: Mistral-7B
5. Trend Generation: Numpy
