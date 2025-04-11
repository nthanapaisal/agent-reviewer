import json
import statistics
import os
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List

def extract_evaluated_metrics(all_reports: Dict[str, Dict]) -> Dict[str, List[float]]:
    result = {}

    for report in all_reports.values():
        evaluated_transcription = report.get("evaluated_transcription", [])
        
        # Iterate through each metric in evaluated_transcription
        for metric, score, _ in evaluated_transcription:
            if metric not in result:
                result[metric] = []  # Create an empty list if the metric is not yet in the result
            result[metric].append(score)
    
    return result

def create_trend_graphs(metrics_data: Dict[str, List[float]]) -> Dict[str, Dict]:
    result = {}

    for metric_name, values in metrics_data.items():
        # Create a new figure
        plt.figure(figsize=(10, 6))
        
        # x-axis: report number (or simply the index of the metric values)
        x_vals = [f"Report {i+1}" for i in range(len(values))]
        
        # Plot the values for the current metric
        plt.plot(x_vals, values, marker='o', label=metric_name)
        
        # Set titles and labels
        plt.title(f'Trending Graph for {metric_name}')
        plt.xlabel('Reports')
        plt.ylabel(f'{metric_name} Score')
        
        # Add grid and labels
        plt.grid(True)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()
        
        # Save the plot to a BytesIO object instead of a file
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='jpeg')
        img_stream.seek(0)
        
        # Convert the image to a base64-encoded string
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

        # Add the raw values and base64 image string to the result dictionary
        result[metric_name] = {
            'raw_val': values,
            'base64': img_base64
        }
        
        # Close the plot to free up memory for the next plot
        plt.close()

    return result

def compute_overall_performance_percentages(data: Dict[str, List[float]], threshold: float = 4.5) -> Dict[str, Dict]:
    performance_data = {}

    for metric, scores in data.items():
        # Compute basic performance metrics
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        min_score = np.min(scores)
        max_score = np.max(scores)
        percentile_10 = np.percentile(scores, 10)
        percentile_90 = np.percentile(scores, 90)

        # Convert any numpy.int64 to int to ensure compatibility with JSON serialization
        mean_score = int(mean_score)
        median_score = int(median_score)
        min_score = int(min_score)
        max_score = int(max_score)
        percentile_10 = int(percentile_10)
        percentile_90 = int(percentile_90)

        # Calculate the percentage of scores above the threshold
        above_threshold_count = sum(1 for score in scores if score >= threshold)
        
        if len(scores) > 0:
            percentage_above_threshold = (above_threshold_count / len(scores)) * 100
        else:
            percentage_above_threshold = 0

        # Store the results in a dictionary
        performance_data[metric] = {
            "mean": mean_score,
            "median": median_score,
            "min": min_score,
            "max": max_score,
            "10th_percentile": percentile_10,
            "90th_percentile": percentile_90,
            "percentage_above_threshold": percentage_above_threshold
        }
    
    return performance_data
