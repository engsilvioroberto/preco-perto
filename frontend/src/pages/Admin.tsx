
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const Admin = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);

  const handleUpload = () => {
    setUploading(true);
    // TODO: Implement offer flyer upload
    setTimeout(() => {
      setUploading(false);
      alert('Jornal de ofertas enviado (simulação)');
    }, 2000);
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Painel Admin</h2>
      </header>

      <div className="admin-content">
        <div className="admin-section">
          <h3>Upload Jornal de Ofertas</h3>
          <p>Faça upload de jornais de ofertas para popular o sistema</p>
          
          <div className="upload-form">
            <input type="file" accept="image/*,.pdf" />
            <select>
              <option value="">Selecione o mercado</option>
              <option value="1">Carrefour Ribeirão</option>
              <option value="2">Extra Hiper</option>
              <option value="3">Dalben</option>
            </select>
            <input type="date" placeholder="Válido de" />
            <input type="date" placeholder="Válido até" />
            
            <button onClick={handleUpload} disabled={uploading} className="btn-primary">
              {uploading ? 'Enviando...' : 'Enviar Jornal'}
            </button>
          </div>
        </div>

        <div className="admin-section">
          <h3>Cadastrar Mercado</h3>
          <button className="btn-secondary">Novo Mercado</button>
        </div>
      </div>
    </div>
  );
};
