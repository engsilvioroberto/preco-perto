import { useState, useRef } from 'react';

interface ReceiptScannerProps {
  onCapture: () => void;
}

export const ReceiptScanner = ({ onCapture }: ReceiptScannerProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      alert('Não foi possível acessar a câmera. Verifique as permissões.');
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg');
        setPreview(imageData);
        onCapture();
      }
    }
  };

  return (
    <div className="receipt-scanner">
      {!preview ? (
        <div className="camera-container">
          <video ref={videoRef} autoPlay playsInline />
          <button onClick={startCamera} className="btn-start-camera">
            📷 Abrir Câmera
          </button>
          <button onClick={captureImage} className="btn-capture">
            Capturar
          </button>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
      ) : (
        <div className="preview-container">
          <img src={preview} alt="Preview" />
        </div>
      )}
    </div>
  );
};
