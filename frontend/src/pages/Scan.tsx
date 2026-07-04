
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ReceiptScanner } from '../components/ReceiptScanner';

export const Scan = () => {
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleCapture = async () => {
    setProcessing(true);
    
    // TODO: Implement OCR processing
    // For now, just simulate processing
    setTimeout(() => {
      setProcessing(false);
      setResult({
        message: 'Nota fiscal processada (simulação)',
        items: [
          { description: 'Leite Integral 1L', price: 4.99, quantity: 2 },
          { description: 'Arroz 5kg', price: 25.90, quantity: 1 },
        ]
      });
    }, 2000);
  };

  return (
    <div className="scan-page">
      <header className="scan-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Escanear Nota Fiscal</h2>
      </header>

      <ReceiptScanner onCapture={handleCapture} />

      {processing && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>Processando nota fiscal...</p>
        </div>
      )}

      {result && (
        <div className="result-container">
          <h3>Produtos Extraídos</h3>
          <ul className="extracted-items">
            {result.items.map((item: any, index: number) => (
              <li key={index} className="extracted-item">
                <span>{item.description}</span>
                <span>R$ {item.price.toFixed(2)}</span>
              </li>
            ))}
          </ul>
          <button className="btn-confirm">Confirmar e Enviar</button>
        </div>
      )}
    </div>
  );
};
