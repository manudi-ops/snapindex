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

  if (!loggedIn) {
    return (
      <div style={{ maxWidth: "360px", margin: "80px auto", fontFamily: "sans-serif" }}>
        <h2>SnapIndex Login</h2>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: "12px" }}>
            <label>Email</label><br />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: "100%", padding: "8px" }} />
          </div>
          <div style={{ marginBottom: "12px" }}>
            <label>Password</label><br />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: "100%", padding: "8px" }} />
          </div>
          <button type="submit" style={{ padding: "8px 16px" }}>Log In</button>
        </form>
        {loginMessage && (
          <p style={{ color: loginError ? "red" : "green", marginTop: "16px" }}>{loginMessage}</p>
        )}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "480px", margin: "80px auto", fontFamily: "sans-serif" }}>
      <h2>Welcome, {fullName}</h2>
      <h3>Upload a Resource</h3>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.pdf"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ marginBottom: "12px" }}
        />
        <br />
        <button type="submit" style={{ padding: "8px 16px" }}>Upload</button>
      </form>

      {uploadError && <p style={{ color: "red" }}>{uploadError}</p>}

      {uploadResult && (
        <div style={{ marginTop: "16px", padding: "12px", border: "1px solid #ccc" }}>
          <p><strong>Uploaded successfully.</strong></p>
          <p>Resource ID: {uploadResult.resourceID}</p>
          <p>OCR Confidence: {uploadResult.ocrConfidence ? uploadResult.ocrConfidence.toFixed(1) + "%" : "N/A"}</p>
          {uploadResult.needsReview && (
            <p style={{ color: "orange" }}>⚠ Low OCR confidence — flagged for review.</p>
          )}
          <p><strong>Extracted text:</strong></p>
          <p style={{ maxHeight: "150px", overflow: "auto", background: "#f5f5f5", padding: "8px" }}>
            {uploadResult.extractedText || "(no text extracted)"}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;