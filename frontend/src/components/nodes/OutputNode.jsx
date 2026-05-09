import { useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Download, Loader2, BookOpen, Trees } from 'lucide-react';
import usePipelineStore from '../../store/pipelineStore';
import { generateImage } from '../../services/api';

export default function OutputNode() {
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

  const handleGenerate = async (e) => {
    e.stopPropagation();
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

  const handleDownload = (e) => {
    e.stopPropagation();
    if (!generatedImage) return;
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${generatedImage}`;
    link.download = 'mockup-generated.png';
    link.click();
  };

  return (
    <div className="bg-gray-900 rounded-xl p-4 min-w-[200px] max-w-[240px] border-2 border-gray-700">
      <Handle type="target" position={Position.Left} className="!bg-blue-500 !w-3 !h-3" />

      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">🖼️</span>
        <span className="text-xs font-semibold text-white">Output</span>
      </div>

      {/* Magazine Mode Toggle */}
      <div
        className="flex items-center justify-between mb-2 px-1"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-1">
          <BookOpen className="w-3 h-3 text-amber-400" />
          <span className="text-[9px] text-gray-300">Magazine</span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setMagazineMode(!magazineMode);
          }}
          className={`relative w-8 h-4 rounded-full transition-colors ${
            magazineMode ? 'bg-amber-500' : 'bg-gray-600'
          }`}
        >
          <span
            className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${
              magazineMode ? 'translate-x-4' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>

      {/* Scenic Background Toggle */}
      <div
        className="flex items-center justify-between mb-3 px-1"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-1">
          <Trees className="w-3 h-3 text-emerald-400" />
          <span className="text-[9px] text-gray-300">Scenic BG</span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setScenicBackground(!scenicBackground);
          }}
          className={`relative w-8 h-4 rounded-full transition-colors ${
            scenicBackground ? 'bg-emerald-500' : 'bg-gray-600'
          }`}
        >
          <span
            className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${
              scenicBackground ? 'translate-x-4' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>

      {generatedImage ? (
        <div className="space-y-2">
          <img
            src={`data:image/png;base64,${generatedImage}`}
            alt="Generated"
            className="w-full rounded-lg border border-gray-700"
          />
          <button
            onClick={handleDownload}
            className="w-full flex items-center justify-center gap-1 px-2 py-1.5 bg-green-600
              hover:bg-green-700 text-white text-[10px] rounded-lg transition-colors"
          >
            <Download className="w-3 h-3" /> Download
          </button>
        </div>
      ) : (
        <div className="text-center py-4">
          <button
            onClick={handleGenerate}
            disabled={!finalPrompts?.positive || loading}
            className="px-3 py-2 bg-gradient-to-r from-purple-600 to-blue-600
              hover:from-purple-700 hover:to-blue-700 disabled:from-gray-700 disabled:to-gray-700
              text-white text-[10px] font-semibold rounded-lg transition-all disabled:text-gray-500"
          >
            {loading ? (
              <span className="flex items-center gap-1">
                <Loader2 className="w-3 h-3 animate-spin" />
                Generating...
              </span>
            ) : magazineMode ? (
              '📰 Generate Magazine'
            ) : (
              '🎨 Generate Image'
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-2 text-[9px] text-red-400 bg-red-900/30 rounded p-1.5">
          {error}
        </div>
      )}
    </div>
  );
}
