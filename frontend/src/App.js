import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [employeeId, setEmployeeId] = useState("");
  const [searchEmployeeId, setSearchEmployeeId] = useState("");
  const [activeEmployeeId, setActiveEmployeeId] = useState(null);
  const [userPrompt, setUserPrompt] = useState("");
  const [promptName, setPromptName] = useState("");
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [overallAnalysis, setOverallAnalysis] = useState(null);
  const [employeeReports, setEmployeeReports] = useState(null);
  const [employeeAnalysis, setEmployeeAnalysis] = useState(null);
  const [promptOptions, setPromptOptions] = useState({});
  const [apiLog, setApiLog] = useState([]);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleEvaluateAudio = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("employee_id", employeeId);
    formData.append("user_prompt", userPrompt);
    formData.append("prompt_name", promptName);

    try {
      const res = await axios.post("http://localhost:8000/evaluate_audio", formData);
      setApiLog((log) => [...log, `✅ Evaluate Audio Success: ${JSON.stringify(res.data)}`]);
      fetchReports();
      fetchOverallAnalysis();
    } catch (error) {
      setApiLog((log) => [...log, `❌ Evaluate Audio Error: ${error.message}`]);
    }
  };

  const fetchReports = () => {
    const socket = new WebSocket("ws://localhost:8000/ws/reports");

    socket.onopen = () => {
      console.log("✅ WebSocket for reports connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setApiLog((log) => [...log, `❌ WebSocket Reports Error: ${data.error}`]);
      } else {
        setReports(data);
        setApiLog((log) => [...log, `✅ WebSocket Received Reports`]);
      }
    };

    socket.onerror = (error) => {
      setApiLog((log) => [...log, `❌ WebSocket Reports Connection Error`]);
    };
  };

  const fetchReportById = async (jobId) => {
    try {
      const res = await axios.get("http://localhost:8000/get-report-id", { params: { job_id: jobId } });
      setSelectedReport(res.data);
    } catch (error) {
      setApiLog((log) => [...log, `❌ Get Report ID Error: ${error.message}`]);
    }
  };

  const fetchOverallAnalysis = async () => {
    const socket = new WebSocket("ws://localhost:8000/ws/overall-analysis");

    socket.onopen = () => {
      console.log("✅ WebSocket for analysis connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setApiLog((log) => [...log, `❌ WebSocket Analysis Error: ${data.error}`]);
      } else {
        setOverallAnalysis(data);
        setApiLog((log) => [...log, `✅ WebSocket Received Analysis`]);
      }
    };

    socket.onerror = (error) => {
      setApiLog((log) => [...log, `❌ WebSocket Analysis Connection Error`]);
    };
  };

  const handleEmployeeSearch = async () => {
    try {
      const reportRes = await axios.get("http://localhost:8000/get-report-employee", {
        params: { employee_id: searchEmployeeId },
      });
      setEmployeeReports(reportRes.data);

      const analysisRes = await axios.post("http://localhost:8000/generate-employee-analysis", null, {
        params: { employee_id: searchEmployeeId },
      });
      setEmployeeAnalysis(analysisRes.data);

      setActiveEmployeeId(searchEmployeeId);

      setApiLog((log) => [...log, `✅ Employee report and analysis loaded for: ${employeeId}`]);
    } catch (error) {
      setEmployeeReports(null);
      setEmployeeAnalysis(null);
      setActiveEmployeeId(null);
      setApiLog((log) => [...log, `❌ Employee data error: ${error.message}`]);
    }
  };

  const clearEmployeeSearch = () => {
    setEmployeeReports(null);
    setEmployeeAnalysis(null);
    setActiveEmployeeId(null);
    setApiLog((log) => [...log, "✅ Cleared to show all reports and overall analysis"]);
  };

  useEffect(() => {
    fetchReports();
    fetchOverallAnalysis();
    axios
      .get("http://localhost:8000/get-prompt-options")
      .then((res) => setPromptOptions(res.data.prompt_options))
      .catch((error) => {
        setApiLog((log) => [...log, `❌ Get Prompt Options Error: ${error.message}`]);
      });
  }, []);

  return (
    <div style={{ display: "grid", gridTemplateRows: "auto 1fr", gap: "1rem", padding: "1rem" }}>
      <h1>Agent Evaluator Dashboard</h1>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <h2>Upload Files</h2>
          <input type="file" onChange={handleFileChange} />
          <input type="text" placeholder="Employee ID" value={employeeId} onChange={(e) => setEmployeeId(e.target.value)} />
          <input type="text" placeholder="User Prompt" value={userPrompt} onChange={(e) => setUserPrompt(e.target.value)} />
          <select id="prompt-name" value={promptName} onChange={(e) => setPromptName(e.target.value)}>
          <option value="">Select Metrics (Hover for details)</option>
            {Object.entries(promptOptions).map(([key, metrics]) => {
              const tooltipText = Object.entries(metrics).map(([metric, desc]) => `${metric}: ${desc}`).join("\n");
              return (
                <option key={key} value={key} title={tooltipText}>
                  {key}
                </option>
              );
            })}
          </select>
          <button onClick={handleEvaluateAudio}>Evaluate Audio</button>
        </div>

        <div>
          <h2>Search by Employee ID</h2>
          <input type="text" placeholder="Search Employee ID" value={searchEmployeeId} onChange={(e) => setSearchEmployeeId(e.target.value)}/>
          <button onClick={handleEmployeeSearch}>Search</button>
          {employeeReports && (
            <button
              onClick={clearEmployeeSearch}
              className="mt-2 px-4 py-1 border border-gray-400 rounded bg-white text-gray-700 hover:bg-gray-100"
            >
              Show All Reports / Overall Analysis
            </button>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "1rem" }}>
        <div>
        <h3>{employeeReports && activeEmployeeId ? `Employee ${activeEmployeeId} Reports` : "All Reports"}</h3>
          <ul className="space-y-2">
            {(employeeReports || reports) &&
              Object.entries(employeeReports || reports).map(([jobId, data]) => (
                <li key={jobId}>
                  <button
                    onClick={() => fetchReportById(jobId)}
                    className="text-left text-blue-500 hover:underline"
                  >
                    {jobId}
                  </button>
                </li>
              ))}
          </ul>

          {/* Selected Report */}
          {selectedReport && (
            <div>
              <h3>Selected Report</h3>
              <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(selectedReport, null, 2)}</pre>
            </div>
          )}
        </div>

        <div>
          <h3>{employeeAnalysis && activeEmployeeId ? `Employee ${activeEmployeeId} Analysis` : "Overall Analysis"}</h3>
          <div className="space-y-6">
            {(employeeAnalysis || overallAnalysis)?.metrics_data ? (
              Object.entries((employeeAnalysis || overallAnalysis).metrics_data).map(([metricName, metricInfo]) => {
                const stats = (employeeAnalysis || overallAnalysis).overall_performance_data[metricName];
                return (
                  <div key={metricName} className="border p-4 rounded shadow">
                    <h3 className="text-xl font-bold mb-2">{metricName}</h3>
                    {metricInfo.base64 && (
                      <img
                        src={`data:image/png;base64,${metricInfo.base64}`}
                        alt={`${metricName} trend graph`}
                        className="w-full max-w-md mb-4"
                      />
                    )}
                    {stats && (
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {Object.entries(stats).map(([key, value]) => (
                          <li key={key}>
                            <strong>{key.replace(/_/g, " ")}:</strong> {value}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              })
            ) : (
              <div>Loading analysis...</div>
            )}
          </div>
        </div>
      </div>

      {/* API Log */}
      <div>
        <h3>API Log</h3>
        <ul>
          {apiLog.map((entry, idx) => (
            <li key={idx} style={{ whiteSpace: "pre-wrap" }}>{entry}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
