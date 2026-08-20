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

  const [categories, setCategories] = useState([]);
  const [showCategoryPicker, setShowCategoryPicker] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");

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
        loadCategories();
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
        body: JSON.stringify({ query: searchQuery, userID }),
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

  const handleOpenResource = async (resourceID) => {
  try {
    await fetch(`http://127.0.0.1:5000/resources/${resourceID}/open`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userID }),
    });
  } catch {
  }
};

const loadCategories = async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/categories");
    const data = await response.json();
    setCategories(data);
  } catch {
   
  }
};

const handleCategoryChange = async (resourceID, categoryID) => {
  try {
    const response = await fetch(`http://127.0.0.1:5000/resources/${resourceID}/category`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categoryID }),
    });
    const data = await response.json();
    if (response.ok) {
      setUploadResult((prev) => ({ ...prev, category: data.category }));
    }
  } catch {
   
  }
};

const handleAddCategory = async () => {
  if (!newCategoryName.trim()) return;
  try {
    const response = await fetch("http://127.0.0.1:5000/categories", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categoryName: newCategoryName.trim() }),
    });
    const data = await response.json();
    if (response.ok) {
      setNewCategoryName("");
      loadCategories();
      if (uploadResult) {
        handleCategoryChange(uploadResult.resourceID, data.categoryID);
      }
    }
  } catch {
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
             {uploadResult.category && (
                <div style={{ fontSize: "13px", marginTop: "8px" }}>
                  <strong>Category:</strong> {uploadResult.category}
                  {uploadResult.categoryConfidence !== null && ` (${uploadResult.categoryConfidence}% confidence)`}
                  {" "}
                  <button
                    type="button"
                    className="si-button"
                    style={{ padding: "2px 10px", fontSize: "12px" }}
                    onClick={() => setShowCategoryPicker(!showCategoryPicker)}
                  >
                    {showCategoryPicker ? "Cancel" : "Not right? Fix it"}
                  </button>

                  {showCategoryPicker && (
                    <div style={{ marginTop: "10px" }}>
                      <select
                        className="si-input"
                        style={{ marginBottom: "8px" }}
                        onChange={(e) => {
                          if (e.target.value) {
                            handleCategoryChange(uploadResult.resourceID, parseInt(e.target.value));
                            setShowCategoryPicker(false);
                          }
                        }}
                        defaultValue=""
                      >
                        <option value="" disabled>Choose a category...</option>
                        {categories.map((c) => (
                          <option key={c.categoryID} value={c.categoryID}>{c.categoryName}</option>
                        ))}
                      </select>

                      <p className="si-label">Or add a new category</p>
                      <input
                        className="si-input"
                        type="text"
                        value={newCategoryName}
                        onChange={(e) => setNewCategoryName(e.target.value)}
                        placeholder="e.g. Nursing & Healthcare"
                      />
                      <button type="button" className="si-button" onClick={handleAddCategory}>
                        Add & Assign
                      </button>
                    </div>
                  )}
                </div>
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
            <div
              className="si-result-card"
              key={`${r.resourceID}-${i}`}
              onClick={() => handleOpenResource(r.resourceID)}
              style={{ cursor: "pointer" }}
            >
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