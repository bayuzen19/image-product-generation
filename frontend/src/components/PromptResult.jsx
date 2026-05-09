import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import usePipelineStore from '../store/pipelineStore';

export default function PromptResult() {
  const finalPrompts = usePipelineStore((s) => s.finalPrompts);
  const [copiedField, setCopiedField] = useState(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!finalPrompts) return null;

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl mt-4 overflow-hidden">
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full px-6 py-3 flex items-center justify-between text-left hover:bg-gray-800/50 transition-colors"
      >
        <span className="text-sm font-semibold text-green-400">
          ✨ Generated Prompts
        </span>
        <span className="text-gray-500 text-xs">{isCollapsed ? '▼' : '▲'}</span>
      </button>

      {!isCollapsed && (
        <div className="px-6 pb-6 space-y-4">
          {/* Positive Prompt */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-medium text-gray-400">Positive Prompt</label>
              <button
                onClick={() => copyToClipboard(finalPrompts.positive, 'positive')}
                className="text-gray-500 hover:text-white transition-colors"
              >
                {copiedField === 'positive' ? (
                  <Check className="w-4 h-4 text-green-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-sm text-gray-300 bg-gray-800 rounded-lg p-3 leading-relaxed">
              {finalPrompts.positive}
            </p>
          </div>

          {/* Negative Prompt */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-medium text-gray-400">Negative Prompt</label>
              <button
                onClick={() => copyToClipboard(finalPrompts.negative, 'negative')}
                className="text-gray-500 hover:text-white transition-colors"
              >
                {copiedField === 'negative' ? (
                  <Check className="w-4 h-4 text-green-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-sm text-gray-300 bg-gray-800 rounded-lg p-3">
              {finalPrompts.negative}
            </p>
          </div>

          {/* Settings Row */}
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-xs font-medium text-gray-400 mb-1 block">
                Midjourney Suffix
              </label>
              <div className="text-sm text-blue-300 bg-gray-800 rounded-lg p-2 font-mono">
                {finalPrompts.midjourney_suffix}
              </div>
            </div>
            <div className="flex-1">
              <label className="text-xs font-medium text-gray-400 mb-1 block">
                Stable Diffusion Settings
              </label>
              <div className="text-sm text-purple-300 bg-gray-800 rounded-lg p-2 font-mono">
                {finalPrompts.sd_settings}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
