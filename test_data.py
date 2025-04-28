# source ~/miniconda3/etc/profile.d/conda.sh
# conda create -n kagglehub-env python=3.10
# conda activate kagglehub-env
# pip install datasets
# spark-submit ./test_data.py
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("yifanmai/call-center")
dataset['test'].to_json("./call_center_data.json", orient="records", lines=True)

# test code
import pyspark
from pyspark.sql import SparkSession, Row
import json
import requests
 
print(pyspark.__version__)

spark = SparkSession.builder \
    .appName("CallCenterTranscripts") \
    .getOrCreate()

# string col of transcripts
df = spark.read.json("./call_center_data.json").select(["transcript"]).cache()

# list of transcripts
transcripts = df.select("transcript").rdd.flatMap(lambda x: x).collect()
i = 0
def call_api(transcript):
    print(i)
    i += 1
    try:
        response = requests.post(
            "http://localhost:8000/test",
            data={"transcript": transcript}
        )
        result = response.json()
        return {
            "input_transcript": transcript,
            "api_response": result
        }
    except Exception as e:
        return {
            "input_transcript": transcript,
            "api_response": {"error": str(e)}
        }

output_list = [call_api(t) for t in transcripts[:20]]

print("total rows:" + str(len(transcripts)))

with open("output_responses.json", "w") as f:
    json.dump(output_list, f, indent=2)

print("---All responses saved to output_responses.json")
