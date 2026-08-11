import { useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsError(false);
        setMessage(`Login successful. Welcome, ${data.fullName}.`);
      } else {
        setIsError(true);
        setMessage(data.error || "Login failed.");
      }
    } catch (err) {
      setIsError(true);
      setMessage("Could not reach the server. Is the backend running?");
    }
  };

  return (
    <div style={{ maxWidth: "360px", margin: "80px auto", fontFamily: "sans-serif" }}>
      <h2>SnapIndex Login</h2>
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: "12px" }}>
          <label>Email</label><br />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: "8px" }}
          />
        </div>
        <div style={{ marginBottom: "12px" }}>
          <label>Password</label><br />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "8px" }}
          />
        </div>
        <button type="submit" style={{ padding: "8px 16px" }}>Log In</button>
      </form>
      {message && (
        <p style={{ color: isError ? "red" : "green", marginTop: "16px" }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default App;