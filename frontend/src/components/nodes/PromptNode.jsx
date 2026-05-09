import { useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Copy, Check } from 'lucide-react';
import usePipelineStore from '../../store/pipelineStore';

export default function PromptNode() {
  const finalPrompts = usePipelineStore((s) => s.finalPrompts);
  const status = usePipelineStore((s) => s.agentStatuses.prompt);
  const [copiedField, setCopiedField] = useState(null);

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const borderClass = status === 'done' ? 'border-green-600' : 'border-gray-700';

  return (
    <div className={`bg-gray-900 rounded-xl p-4 min-w-[240px] max-w-[280px] border-2 ${borderClass}`}>
      <Handle type="target" position={Position.Left} className="!bg-blue-500 !w-3 !h-3" />

      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">📝</span>
        <span className="text-xs font-semibold text-white">Final Prompts</span>
      </div>

      {finalPrompts ? (
        <div className="space-y-2">
          {/* Positive */}
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-400 font-medium">Positive</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(finalPrompts.positive, 'positive');
                }}
                className="text-gray-600 hover:text-white"
              >
                {copiedField === 'positive' ? (
                  <Check className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
            <p className="text-[9px] text-gray-300 bg-gray-800 rounded p-1.5 max-h-[60px] overflow-y-auto leading-tight">
              {finalPrompts.positive}
            </p>
          </div>

          {/* Negative */}
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-400 font-medium">Negative</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(finalPrompts.negative, 'negative');
                }}
                className="text-gray-600 hover:text-white"
              >
                {copiedField === 'negative' ? (
                  <Check className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
            <p className="text-[9px] text-gray-300 bg-gray-800 rounded p-1.5 max-h-[40px] overflow-y-auto leading-tight">
              {finalPrompts.negative}
            </p>
          </div>

          <div className="text-[8px] text-blue-300 font-mono">{finalPrompts.midjourney_suffix}</div>
        </div>
      ) : (
        <p className="text-[10px] text-gray-600">Waiting for pipeline...</p>
      )}

      <Handle type="source" position={Position.Right} className="!bg-blue-500 !w-3 !h-3" />
    </div>
  );
}
