import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const Profile = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(user?.name || '');

  const handleSaveName = () => {
    if (editName.trim()) {
      const updated = { ...user!, name: editName.trim() };
      localStorage.setItem('precoperto_user', JSON.stringify(updated));
      window.location.reload();
    }
    setEditing(false);
  };

  return (
    <div className="profile-page">
      <header className="profile-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Meu Perfil</h2>
      </header>

      <div className="profile-content">
        <div className="profile-section user-card">
          <div className="user-avatar">{user?.name?.charAt(0).toUpperCase()}</div>
          {editing ? (
            <div className="edit-name">
              <input
                type="text"
                value={editName}
                onChange={e => setEditName(e.target.value)}
                autoFocus
              />
              <div className="edit-actions">
                <button onClick={handleSaveName} className="btn-primary">Salvar</button>
                <button onClick={() => setEditing(false)} className="btn-secondary">Cancelar</button>
              </div>
            </div>
          ) : (
            <>
              <h3>{user?.name}</h3>
              <p className="user-email">{user?.email}</p>
              <button onClick={() => { setEditName(user?.name || ''); setEditing(true); }} className="btn-secondary">
                Editar Nome
              </button>
            </>
          )}
        </div>

        <div className="profile-section">
          <h3>Histórico de Escaneamentos</h3>
          <p className="empty-state">Você ainda não escaneou nenhuma nota fiscal</p>
          <button onClick={() => navigate('/scan')} className="btn-primary">
            Escanear Nota Fiscal
          </button>
        </div>

        <div className="profile-section">
          <button onClick={logout} className="btn-logout">Sair da Conta</button>
        </div>
      </div>
    </div>
  );
};
