import { useState } from 'react';
import { Download, Loader2, BookOpen, Trees } from 'lucide-react';
import usePipelineStore from '../store/pipelineStore';
import { generateImage } from '../services/api';

export default function GeneratedImage() {
  const generatedImage = usePipelineStore((s) => s.generatedImage);
  const setGeneratedImage = usePipelineStore((s) => s.setGeneratedImage);
  const finalPrompts = usePipelineStore((s) => s.finalPrompts);
  const productFile = usePipelineStore((s) => s.productFile);
  const logoFile = usePipelineStore((s) => s.logoFile);
  const modelFile = usePipelineStore((s) => s.modelFile);
  const agentResults = usePipelineStore((s) => s.agentResults);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [magazineMode, setMagazineMode] = useState(false);
  const [scenicBackground, setScenicBackground] = useState(false);

  const handleGenerate = async () => {
    if (!finalPrompts?.positive) return;
    setLoading(true);
    setError(null);
    try {
      const productInfo = {
        analysis: agentResults?.analysis || {},
        product: agentResults?.product || {},
        editor: agentResults?.editor || {},
        prompt: agentResults?.prompt || {},
      };
      const promptText = magazineMode && finalPrompts.magazine_positive 
        ? finalPrompts.magazine_positive 
        : finalPrompts.positive;
      const result = await generateImage(promptText, productFile, magazineMode, productInfo, logoFile, modelFile, scenicBackground);
      if (result.image_base64) {
        setGeneratedImage(result.image_base64);
      } else {
        setError(result.error || 'No image generated');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${generatedImage}`;
    link.download = 'mockup-generated.png';
    link.click();
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mt-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-400">Generated Image</h3>
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-amber-400" />
          <span className="text-xs text-gray-400">Magazine</span>
          <button
            onClick={() => setMagazineMode(!magazineMode)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              magazineMode ? 'bg-amber-500' : 'bg-gray-600'
            }`}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                magazineMode ? 'translate-x-5' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <Trees className="w-4 h-4 text-emerald-400" />
          <span className="text-xs text-gray-400">Scenic BG</span>
          <button
            onClick={() => setScenicBackground(!scenicBackground)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              scenicBackground ? 'bg-emerald-500' : 'bg-gray-600'
            }`}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                scenicBackground ? 'translate-x-5' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>
      </div>

      {generatedImage ? (
        <div className="space-y-3">
          <img
            src={`data:image/png;base64,${generatedImage}`}
            alt="Generated mockup"
            className="w-full max-w-md rounded-lg border border-gray-700 mx-auto"
          />
          <div className="flex gap-2 justify-center">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700
                text-white text-sm rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" /> Download
            </button>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700
                text-white text-sm rounded-lg transition-colors"
            >
              Regenerate
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <button
            onClick={handleGenerate}
            disabled={!finalPrompts?.positive || loading}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600
              hover:from-purple-700 hover:to-blue-700 disabled:from-gray-700 disabled:to-gray-700
              text-white font-semibold rounded-lg transition-all disabled:text-gray-500"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </span>
            ) : (
              '🎨 Generate Image'
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
