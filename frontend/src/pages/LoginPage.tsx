import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { guestLogin, login, register } from "../api/auth";
import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { login: setAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const response = mode === "login" ? await login(email, password) : await register(email, password);
      setAuthenticated(response.access_token);
      navigate("/fridge");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "予期しないエラーが発生しました");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGuestLogin = async () => {
    setError(null);
    setSubmitting(true);
    try {
      const response = await guestLogin();
      setAuthenticated(response.access_token);
      navigate("/fridge");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "予期しないエラーが発生しました");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="centered-card">
      <h1>{mode === "login" ? "ログイン" : "新規登録"}</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          メールアドレス
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          パスワード
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </label>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={submitting}>
          {mode === "login" ? "ログイン" : "登録する"}
        </button>
      </form>
      <button
        type="button"
        className="link-button"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
      >
        {mode === "login" ? "アカウントを新規登録する" : "ログイン画面に戻る"}
      </button>
      <hr className="divider" />
      <button type="button" onClick={handleGuestLogin} disabled={submitting} className="guest-button">
        ログインせずにゲストとして試す
      </button>
    </div>
  );
}
