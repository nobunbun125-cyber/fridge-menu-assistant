import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">冷蔵庫AI献立アシスタント</span>
        <nav className="app-nav">
          <NavLink to="/fridge">冷蔵庫</NavLink>
          <NavLink to="/menu/new">献立作成</NavLink>
          <NavLink to="/history">履歴</NavLink>
          <button type="button" onClick={handleLogout} className="link-button">
            ログアウト
          </button>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
