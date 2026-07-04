
import { useNavigate } from 'react-router-dom';

export const Profile = () => {
  const navigate = useNavigate();

  return (
    <div className="profile-page">
      <header className="profile-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Meu Perfil</h2>
      </header>

      <div className="profile-content">
        <div className="profile-section">
          <h3>Contribuições</h3>
          <p>Você ainda não escaneou nenhuma nota fiscal</p>
          <button onClick={() => navigate('/scan')} className="btn-primary">
            Escanear Nota Fiscal
          </button>
        </div>

        <div className="profile-section">
          <h3>Configurações</h3>
          <button className="btn-secondary">Editar Perfil</button>
          <button className="btn-secondary">Notificações</button>
          <button className="btn-secondary">Privacidade</button>
        </div>
      </div>
    </div>
  );
};
