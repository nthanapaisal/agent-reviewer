import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_analysis(data: list[tuple[str, float, str]], summary: str):
    # Turn into dict
    scores_dict = {metric: score for (metric, score, _) in data}
    individual_scores = "\n".join([f"- {metric}: {score}" for metric, score in scores_dict.items()])
    print(individual_scores)
    metrics = list(scores_dict.keys())
    scores = list(scores_dict.values())

    # Mean and SD
    average_score = np.mean(scores)
    std_dev = np.std(scores)

    # Report
    analysis_report = {
        "Summary": summary,
        "Evaluated Metrics": individual_scores,
        "Average Score": round(average_score, 2),
        "Standard Deviation": round(std_dev, 2),
        "Performance Evaluation": "Consistent Performance" if average_score > 4.5 and std_dev < 0.5 else "Inconsistent Performance",
    }

    # Bar chart
    plt.figure(figsize=(8, 7))
    sns.barplot(x=metrics, y=scores, palette="Blues_d")
    plt.xticks(rotation=45)
    plt.ylim(0, 5.5)
    plt.title("Customer Service Evaluation Metrics")
    plt.ylabel("Score (out of 5)")
    plt.xlabel("Metrics")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    bar_chart_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    # Box plot
    plt.figure(figsize=(8, 7))
    sns.boxplot(x=scores, color="lightblue")
    plt.title("Customer Service Score Distribution")
    plt.xlabel("Score (out of 5)")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    box_chart_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    return {
        "analysis_report": analysis_report,
        "bar_chart": f"data:image/png;base64,{bar_chart_base64}",
        "box_chart": f"data:image/png;base64,{box_chart_base64}",
    }
