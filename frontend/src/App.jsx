import { useEffect, useState } from "react";
import "./App.css";

function App() {

  const [problems, setProblems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);


  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [selectedProblemId, setSelectedProblemId] = useState("");


  useEffect(() => {
    async function loadProblems() {
      try {
        const response = await fetch("/api/problems");

        if (!response.ok) {
          throw new Error("Failed to load problems");
        }

        const data = await response.json();
        setProblems(data);

        // Select the first problem by default
        if (data.length > 0) {
          setSelectedProblemId(String(data[0].id));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProblems();
  }, []);


  async function handleSubmit() {
    if (!answer.trim() || !selectedProblemId) {
      return;
    }

    setSubmitting(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch("/api/attempts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem_id: Number(selectedProblemId),
          answer: answer,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to check answer");
      }

      // Save the backend response so React can display it
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  const selectedProblem = problems.find(
    (problem) => problem.id === Number(selectedProblemId)
  );

  return (
    <div className="app">
      <h1>MathWiz</h1>

      <p>Your personal math visualiser.</p>

      <h2>Available problems</h2>

      {loading && <p>Loading problems...</p>}
      {error && <p>Error: {error}</p>}

      {problems.map((problem) => (
        <div className="problem" key={problem.id}>
          <h3>{problem.title}</h3>
          <p>{problem.equationLatex}</p>
        </div>
      ))}

      {!loading && problems.length > 0 && (
        <div className="answer-section">
          <h2>Try a problem</h2>

          <label htmlFor="problem-select">
            Choose a problem:
          </label>

          <select
            id="problem-select"
            value={selectedProblemId}
            onChange={(event) => {
              setSelectedProblemId(event.target.value);
              setResult(null);
            }}
          >
            {problems.map((problem) => (
              <option key={problem.id} value={problem.id}>
                {problem.title}
              </option>
            ))}
          </select>

          {selectedProblem && (
            <p>
              Solve: <strong>{selectedProblem.equationLatex} = 0</strong>
            </p>
          )}

          <label htmlFor="answer-input">
            Your answer:
          </label>

          <input
            id="answer-input"
            type="text"
            value={answer}
            onChange={(event) => {
              setAnswer(event.target.value);
              setResult(null);
            }}
            placeholder="For example, x = 2"
          />

          <button
            onClick={handleSubmit}
            disabled={submitting || !answer.trim()}
          >
            {submitting ? "Checking..." : "Submit answer"}
          </button>

          {result && (
            <div className="result">
              <h3>Result</h3>
              <p>
                <strong>Verdict:</strong> {result.verdict}
              </p>
              <p>
                <strong>Your extracted roots:</strong>{" "}
                {result.student_roots.length > 0
                  ? result.student_roots.join(", ")
                  : "No numbers found"}
              </p>


              <video
                controls
                width="640"
                src={result.video_url}>
                Your browser does not support video playback.
              </video>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
