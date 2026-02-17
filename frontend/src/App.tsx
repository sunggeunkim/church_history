import { BrowserRouter, Routes, Route } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { HomePage } from "@/pages/HomePage";
import { LoginPage } from "@/pages/LoginPage";
import { ChatPage } from "@/pages/ChatPage";
import { ErasPage } from "@/pages/ErasPage";
import { EraDetailPage } from "@/pages/EraDetailPage";
import { QuizPage } from "@/pages/QuizPage";
import { ProgressPage } from "@/pages/ProgressPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

function App() {
  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route index element={<HomePage />} />
                <Route path="chat" element={<ChatPage />} />
                <Route path="eras" element={<ErasPage />} />
                <Route path="eras/:slug" element={<EraDetailPage />} />
                <Route path="quiz" element={<QuizPage />} />
                <Route path="progress" element={<ProgressPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
