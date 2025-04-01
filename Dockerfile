FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

# Run the application using uvicorn
CMD ["/bin/bash", "-c", "PYTHONPATH=./src uvicorn main:app --host 0.0.0.0 --reload"]
