import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState("");
  const [userPrompt, setUserPrompt] = useState("");
  const [generatedPrompt, setGeneratedPrompt] = useState("");
  const [evaluationResult, setEvaluationResult] = useState("");
  const [analysisResult, setAnalysisResult] = useState({});
  const [barChart, setBarChart] = useState("");
  const [boxChart, setBoxChart] = useState("");
  const [apiLog, setApiLog] = useState([]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTranscribe = async () => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/transcribe", formData);
      setTranscription(res.data.transcription);
      setApiLog((log) => [...log, `✅ Transcription: ${res.data.transcription}`]);
    } catch (error) {
      console.error(error);
      setApiLog((log) => [...log, `❌ Transcription Error: ${error.message}`]);
    }
  };

  const handleGeneratePrompt = async () => {
    try {
      const res = await axios.post("http://localhost:8000/generate-prompts", {
        transcription,
        user_prompt: userPrompt,
      });

      const prompt = res.data.prompts;
      setGeneratedPrompt(prompt);
      setApiLog((log) => [...log, `✅ Generated Prompt: ${prompt}`]);
    } catch (error) {
      console.error(error);
      setApiLog((log) => [...log, `❌ Prompt Generation Error: ${error.message}`]);
    }
  };

  const handleEvaluate = async () => {
    try {
      const res = await axios.post("http://localhost:8000/evaluate", {
        prompt: generatedPrompt,
      });

      setEvaluationResult(res.data.evaluation.evaluation);
      setApiLog((log) => [...log, `✅ Evaluation: ${res.data.evaluation.evaluation}`]);
    } catch (error) {
      console.error(error);
      setApiLog((log) => [...log, `❌ Evaluation Error: ${error.message}`]);
    }
  };

  const handleAnalysis = async () => {
    try {
      const parsedResult = JSON.parse(evaluationResult);
      const res = await axios.post("http://localhost:8000/create-analysis", {
        report: parsedResult.report,
        summary: parsedResult.summary,
      });
      const { analysis_report, bar_chart, box_chart} = res.data;
      setAnalysisResult(analysis_report);
      setBarChart(bar_chart);
      setBoxChart(box_chart);
      setApiLog((log) => [...log, `✅ Analysis: ${JSON.stringify(res.data)}`]);
    } catch (error) {
      console.error(error);
      setApiLog((log) => [...log, `❌ Analysis Error: ${error.message}`]);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Agent Evaluator Dashboard</h1>

      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleTranscribe}>Transcribe</button>
      </div>

      <div>
        <h3>Transcription:</h3>
        <textarea rows={4} value={transcription} onChange={(e) => setTranscription(e.target.value)} />
      </div>

      <div>
        <h3>User Prompt:</h3>
        <input type="text" value={userPrompt} onChange={(e) => setUserPrompt(e.target.value)} />
        <button onClick={handleGeneratePrompt}>Generate Prompt</button>
        {generatedPrompt && (
          <><div>
            <h4>Generated Prompt:</h4>
            <pre style={{ whiteSpace: "pre-wrap" }}>{generatedPrompt}</pre>
            </div></>
          )}
      </div>

      <div>
        <button onClick={handleEvaluate}>Evaluate</button>
        <h3>Evaluation Result:</h3>
        <textarea rows={4} value={evaluationResult} onChange={(e) => setEvaluationResult(e.target.value)} />
      </div>

      <div>
      <button onClick={handleAnalysis}>Generate Analysis</button>
        <h3>Performance Report:</h3>
        {analysisResult && barChart && boxChart && (
          <><div>
            <h5>Bar Chart:</h5>
            <img src={barChart} alt="Bar Chart" />
            <h5>Evaluated Metrics:</h5>
            <p>{analysisResult["Evaluated Metrics"]}</p>
          </div><div>
          <h5>Box Chart:</h5>
            <img src={boxChart} alt="Box Chart" />
            <p>Average Score: {analysisResult["Average Score"]}</p>
            <p>Standard Deviation: {analysisResult["Standard Deviation"]}</p>
            <p>Performance Evaluation: {analysisResult["Performance Evaluation"]}</p>
            <p>Summary: {analysisResult["Summary"]}</p>
          </div></>
        )}
      </div>

      <div>
        <h3>API Call Log:</h3>
        <ul>
          {apiLog.map((entry, index) => (
            <li key={index} style={{ whiteSpace: "pre-wrap" }}>
              {entry}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;