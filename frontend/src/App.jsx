import { useState } from "react";
import "./App.css";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [userID, setUserID] = useState(null);
  const [fullName, setFullName] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginMessage, setLoginMessage] = useState("");
  const [loginError, setLoginError] = useState(false);

  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState("");

  const [activeTab, setActiveTab] = useState("upload");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchError, setSearchError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginMessage("");
    try {
      const response = await fetch("http://127.0.0.1:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setLoginError(false);
        setLoggedIn(true);
        setUserID(data.userID);
        setFullName(data.fullName);
      } else {
        setLoginError(true);
        setLoginMessage(data.error || "Login failed.");
      }
    } catch {
      setLoginError(true);
      setLoginMessage("Could not reach the server. Is the backend running?");
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploadError("");
    setUploadResult(null);
    if (!file) {
      setUploadError("Please choose a file first.");
      return;
    }
    const formData = new FormData();
    formData.append("userID", userID);
    formData.append("file", file);
    try {
      const response = await fetch("http://127.0.0.1:5000/resources/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setUploadResult(data);
      } else {
        setUploadError(data.error || "Upload failed.");
      }
    } catch {
      setUploadError("Could not reach the server.");
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearchError("");
    setSearchResults([]);
    try {
      const response = await fetch("http://127.0.0.1:5000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      const data = await response.json();
      if (response.ok) {
        setSearchResults(data.results || []);
      } else {
        setSearchError(data.error || "Search failed.");
      }
    } catch {
      setSearchError("Could not reach the server.");
    }
  };

  if (!loggedIn) {
    return (
      <div className="si-container">
        <div className="si-card">
          <h2 className="si-title">SnapIndex</h2>
          <p className="si-subtitle">Log in to your knowledge base</p>
          <form onSubmit={handleLogin}>
            <label className="si-label">Email</label>
            <input
              className="si-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <label className="si-label">Password</label>
            <input
              className="si-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button className="si-button" type="submit">Log In</button>
          </form>
          {loginMessage && (
            <p className={loginError ? "si-message-error" : "si-message-success"} style={{ marginTop: "16px" }}>
              {loginMessage}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="si-container">
      <p className="si-welcome">Welcome, {fullName} 🌸</p>

      <div className="si-tabs">
        <button
          className={`si-tab ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          Upload
        </button>
        <button
          className={`si-tab ${activeTab === "search" ? "active" : ""}`}
          onClick={() => setActiveTab("search")}
        >
          Search
        </button>
      </div>

      {activeTab === "upload" && (
        <div className="si-card">
          <h3 className="si-title" style={{ fontSize: "18px" }}>Upload a Resource</h3>
          <form onSubmit={handleUpload}>
            <input
              className="si-input"
              type="file"
              accept=".png,.jpg,.jpeg,.pdf"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button className="si-button" type="submit">Upload</button>
          </form>

          {uploadError && <p className="si-message-error" style={{ marginTop: "12px" }}>{uploadError}</p>}

          {uploadResult && (
            <div className="si-result-card">
              <p className="si-message-success">Uploaded successfully.</p>
              <p style={{ fontSize: "13px" }}>Resource ID: {uploadResult.resourceID}</p>
              <p style={{ fontSize: "13px" }}>
                OCR Confidence: {uploadResult.ocrConfidence ? uploadResult.ocrConfidence.toFixed(1) + "%" : "N/A"}
              </p>
              {uploadResult.needsReview && (
                <p className="si-warning">⚠ Low OCR confidence — flagged for review.</p>
              )}
              {uploadResult.duplicateWarning && uploadResult.duplicateWarning.length > 0 && (
                <p className="si-warning">
                  ⚠ Possible duplicate — similar to resource ID {uploadResult.duplicateWarning[0].resourceID}
                  {" "}({(uploadResult.duplicateWarning[0].similarity * 100).toFixed(1)}% match).
                </p>
              )}
              <p className="si-label" style={{ marginTop: "10px" }}>Extracted text</p>
              <div className="si-extracted-box">{uploadResult.extractedText || "(no text extracted)"}</div>
            </div>
          )}
        </div>
      )}

      {activeTab === "search" && (
        <div className="si-card">
          <h3 className="si-title" style={{ fontSize: "18px" }}>Search Your Resources</h3>
          <form onSubmit={handleSearch}>
            <input
              className="si-input"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g. customer order process"
            />
            <button className="si-button" type="submit">Search</button>
          </form>

          {searchError && <p className="si-message-error" style={{ marginTop: "12px" }}>{searchError}</p>}

          {searchResults.length === 0 && !searchError && (
            <p style={{ color: "#b98d94", fontSize: "14px", marginTop: "12px" }}>No results yet — try a search above.</p>
          )}

          {searchResults.map((r, i) => (
            <div className="si-result-card" key={`${r.resourceID}-${i}`}>
              <p className="si-result-title">
                {r.title} <span className="si-result-score">({r.similarityScore}% match)</span>
              </p>
              <p className="si-result-snippet">{r.extractedText}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;