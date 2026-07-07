import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Home } from './pages/Home';
import { Search } from './pages/Search';
import { Map } from './pages/Map';
import { Scan } from './pages/Scan';
import { Profile } from './pages/Profile';
import { Admin } from './pages/Admin';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import type { ReactNode } from 'react';
import './App.css';

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading">Carregando...</div>;
  if (!user) {
    return (
      <div className="auth-required">
        <p>Faça login para acessar esta página.</p>
        <Link to="/login" className="btn-primary">Entrar</Link>
      </div>
    );
  }
  return <>{children}</>;
}

function AdminRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading">Carregando...</div>;
  if (!user || !user.is_admin) {
    return (
      <div className="auth-required">
        <p>Acesso restrito a administradores.</p>
        <Link to="/" className="btn-primary">Voltar</Link>
      </div>
    );
  }
  return <>{children}</>;
}

function BottomNav() {
  const location = useLocation();
  const { user } = useAuth();

  const hideNav = ['/login', '/register'].includes(location.pathname);
  if (hideNav) return null;

  return (
    <nav className="bottom-nav">
      <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
        🏠<span>Início</span>
      </Link>
      <Link to="/scan" className={location.pathname === '/scan' ? 'active' : ''}>
        📷<span>Escanear</span>
      </Link>
      <Link to="/profile" className={location.pathname === '/profile' ? 'active' : ''}>
        👤<span>Perfil</span>
      </Link>
      {user?.is_admin && (
        <Link to="/admin" className={location.pathname === '/admin' ? 'active' : ''}>
          ⚙️<span>Admin</span>
        </Link>
      )}
    </nav>
  );
}

function AppContent() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search/:productId" element={<Search />} />
        <Route path="/map/:productId" element={<Map />} />
        <Route path="/scan" element={
          <ProtectedRoute><Scan /></ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute><Profile /></ProtectedRoute>
        } />
        <Route path="/admin" element={
          <AdminRoute><Admin /></AdminRoute>
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
      <BottomNav />
    </div>
  );
}

function App() {
  return (
    <Router basename="/preco-perto">
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
