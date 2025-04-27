import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Button,
  Container,
  Divider,
  Heading,
  Input,
  Select,
  Textarea,
  VStack,
  Text,
  Image,
  HStack,
  useColorMode,
  useColorModeValue,
  IconButton,
  UnorderedList,
  ListItem,
  Flex,
} from "@chakra-ui/react";
import { MoonIcon, SunIcon } from "@chakra-ui/icons";

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
  const [isEvaluating, setIsEvaluating] = useState(false);
  const { colorMode, toggleColorMode } = useColorMode();
  const [fileInputKey, setFileInputKey] = useState(Date.now());

  const boxBg = useColorModeValue("gray.50", "gray.700");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleEvaluateAudio = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("employee_id", employeeId);
    formData.append("user_prompt", userPrompt);
    formData.append("prompt_name", promptName);

    setIsEvaluating(true);
    try {
      const res = await axios.post("http://localhost:8000/evaluate_audio", formData);
      setApiLog((log) => [...log, `Evaluate Audio Success: ${JSON.stringify(res.data)}`]);
      fetchReports();
      fetchOverallAnalysis();
      setFile(null);
      setFileInputKey(Date.now());
      setEmployeeId("");
      setUserPrompt("");
      setPromptName("");
    } catch (error) {
      setApiLog((log) => [...log, `Evaluate Audio Error: ${error.message}`]);
    } finally {
      setIsEvaluating(false);
    }
  };

  const fetchReports = () => {
    const socket = new WebSocket("ws://localhost:8000/ws/reports");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setApiLog((log) => [...log, `WebSocket Reports Error: ${data.error}`]);
      } else {
        setReports(data);
        setApiLog((log) => [...log, `WebSocket Received Reports`]);
      }
    };
    socket.onerror = () => {
      setApiLog((log) => [...log, `WebSocket Reports Connection Error`]);
    };
  };

  const fetchReportById = async (jobId) => {
    try {
      const res = await axios.get("http://localhost:8000/get-report-id", { params: { job_id: jobId } });
      setSelectedReport(res.data);
    } catch (error) {
      setApiLog((log) => [...log, `Get Report ID Error: ${error.message}`]);
    }
  };

  const fetchOverallAnalysis = () => {
    const socket = new WebSocket("ws://localhost:8000/ws/overall-analysis");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setApiLog((log) => [...log, `WebSocket Analysis Error: ${data.error}`]);
      } else {
        setOverallAnalysis(data);
        setApiLog((log) => [...log, `WebSocket Received Analysis`]);
      }
    };
    socket.onerror = () => {
      setApiLog((log) => [...log, `WebSocket Analysis Connection Error`]);
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
      setApiLog((log) => [...log, `Employee report and analysis loaded for: ${searchEmployeeId}`]);
    } catch (error) {
      setEmployeeReports(null);
      setEmployeeAnalysis(null);
      setActiveEmployeeId(null);
      setApiLog((log) => [...log, `Employee data error: ${error.message}`]);
    }
  };

  const clearEmployeeSearch = () => {
    setSearchEmployeeId("");
    setEmployeeReports(null);
    setEmployeeAnalysis(null);
    setActiveEmployeeId(null);
    setApiLog((log) => [...log, "Cleared to show all reports and overall analysis"]);
  };

  useEffect(() => {
    fetchReports();
    fetchOverallAnalysis();
    axios
      .get("http://localhost:8000/get-prompt-options")
      .then((res) => setPromptOptions(res.data.prompt_options))
      .catch((error) => {
        setApiLog((log) => [...log, `Get Prompt Options Error: ${error.message}`]);
      });
  }, []);

  return (
    <Container maxW="7xl" p={4}>
      <HStack justify="space-between" mb={4}>
        <Heading>Customer Service Audio Analyzer</Heading>
        <IconButton
          icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          aria-label="Toggle dark mode"
        />
      </HStack>

      <Divider mb={6} />

      <HStack spacing={10} align="flex-start" mb={8}>
        <VStack spacing={4} align="stretch" flex={1}>
          <Heading size="md">Upload Conversation Autio Files</Heading>
          <Input key={fileInputKey} type="file" onChange={handleFileChange}/>
          <Input placeholder="Employee ID (Required)" value={employeeId} onChange={(e) => setEmployeeId(e.target.value)}/>
          <Textarea placeholder="User Prompt" value={userPrompt} onChange={(e) => setUserPrompt(e.target.value)} />
          <Select id="prompt-name" value={promptName} onChange={(e) => setPromptName(e.target.value)}>
          <option value="">Select Metrics (Required, hover for details)</option>
            {Object.entries(promptOptions).map(([key, metrics]) => {
              const tooltipText = Object.entries(metrics).map(([metric, desc]) => `${metric}: ${desc}`).join("\n");
              return (
                <option key={key} value={key} title={tooltipText}>
                  {key}
                </option>
              );
            })}
          </Select>
          
          <Button onClick={handleEvaluateAudio}
                  colorScheme="teal"
                  isLoading={isEvaluating}
                  loadingText="Evaluating..."
                  isDisabled={!file || !employeeId || !promptName}>
            Evaluate Audio
          </Button>
        </VStack>

        <Divider orientation="vertical" height="100%" />

        <VStack spacing={4} align="stretch" flex={1}>
          <Heading size="md">Search by Employee ID</Heading>
          <Input placeholder="Search Employee ID" value={searchEmployeeId} onChange={(e) => setSearchEmployeeId(e.target.value)} />
          <Button onClick={handleEmployeeSearch} colorScheme="blue" isDisabled={!searchEmployeeId}>Search</Button>
          {employeeReports && (
            <Button onClick={clearEmployeeSearch}>Show All Reports / Overall Analysis</Button>
          )}
        </VStack>
      </HStack>

      <Divider mb={6} />

      <Flex align="flex-start" gap={8} wrap="nowrap">
        <Box flex="1" maxW="60%">
          <Heading size="md" mb={2}>
            {employeeReports && activeEmployeeId ? `Employee ${activeEmployeeId} Reports` : "All Reports"}
          </Heading>
          <VStack align="start">
            {(employeeReports || reports) &&
              Object.entries(employeeReports || reports).map(([jobId]) => (
                <Button key={jobId} variant="link" colorScheme="blue" onClick={() => fetchReportById(jobId)}>
                  {jobId}
                </Button>
              ))}
          </VStack>

          {selectedReport && (
            <Box mt={6} maxW="100%">
              <Divider mb={4} />
              <Heading size="sm" mb={2}>Selected Report</Heading>
              <Box p={3} border="1px solid #ddd" borderRadius="md" bg={boxBg} whiteSpace="pre-wrap" maxH="1000px" overflowY="auto">
                <pre>{JSON.stringify(selectedReport, null, 2)}</pre>
              </Box>
            </Box>
          )}
        </Box>

        <Box flex="1" maxW="60%">
          <Heading size="md" mb={4}>
            {employeeAnalysis && activeEmployeeId ? `Employee ${activeEmployeeId} Analysis` : "Overall Analysis"}
          </Heading>
          <VStack spacing={4} align="stretch">
            {(employeeAnalysis || overallAnalysis)?.metrics_data ? (
              Object.entries((employeeAnalysis || overallAnalysis).metrics_data).map(([metricName, metricInfo]) => {
                const stats = (employeeAnalysis || overallAnalysis).overall_performance_data[metricName];
                return (
                  <Box key={metricName} borderWidth={1} borderRadius="md" p={4}>
                    <Heading size="sm" mb={2}>{metricName}</Heading>
                    {metricInfo.base64 && (
                      <Image src={`data:image/png;base64,${metricInfo.base64}`} alt={`${metricName} graph`} mb={2} />
                    )}
                    {stats && (
                      <UnorderedList fontSize="sm">
                        {Object.entries(stats).map(([key, value]) => (
                          <ListItem key={key}>
                            <strong>{key.replace(/_/g, " ")}:</strong> {value}
                          </ListItem>
                        ))}
                      </UnorderedList>
                    )}
                  </Box>
                );
              })
            ) : (
              <Text>Loading analysis...</Text>
            )}
          </VStack>
        </Box>
      </Flex>

      <Box mt={10}>
        <Heading size="md" mb={2}>API Log</Heading>
        <Box bg={boxBg} p={3} borderRadius="md" maxHeight="200px" overflowY="auto" fontFamily="mono" fontSize="sm">
          {apiLog.map((entry, idx) => (
            <Text key={idx}>{entry}</Text>
          ))}
        </Box>
      </Box>
    </Container>
  );
}

export default App;
