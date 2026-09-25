import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { FridgePage } from "./pages/FridgePage";
import { MenuCreatePage } from "./pages/MenuCreatePage";
import { ResultPage } from "./pages/ResultPage";
import { HistoryPage } from "./pages/HistoryPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/fridge" element={<FridgePage />} />
          <Route path="/menu/new" element={<MenuCreatePage />} />
          <Route path="/menu/result" element={<ResultPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/fridge" replace />} />
      </Routes>
    </AuthProvider>
  );
}
