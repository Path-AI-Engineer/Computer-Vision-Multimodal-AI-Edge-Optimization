import { useEffect, useRef } from "react";

export function ImageCanvas({ src, label, pixelated = false }: { src: string; label: string; pixelated?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !src) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const image = new Image();
    image.onload = () => {
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      context.imageSmoothingEnabled = !pixelated;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0);
    };
    image.src = src;
  }, [src, pixelated]);

  return <canvas ref={canvasRef} className="evidence-canvas" role="img" aria-label={label} />;
}

