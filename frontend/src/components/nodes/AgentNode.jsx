import { useState } from 'react';
import { Handle, Position } from '@xyflow/react';

const STATUS_COLORS = {
  idle: 'bg-gray-500',
  running: 'bg-blue-500 animate-pulse',
  done: 'bg-green-500',
  error: 'bg-red-500',
};

const BORDER_COLORS = {
  idle: 'border-gray-700',
  running: 'border-blue-500 animate-pulse-border',
  done: 'border-green-600',
  error: 'border-red-600',
};

export default function AgentNode({ data }) {
  const [expanded, setExpanded] = useState(false);
  const { label, description, icon, status = 'idle', result } = data;

  return (
    <div
      className={`bg-gray-900 rounded-xl p-4 min-w-[180px] max-w-[220px] border-2 transition-all cursor-pointer ${
        BORDER_COLORS[status]
      }`}
      onClick={() => result && setExpanded(!expanded)}
    >
      <Handle type="target" position={Position.Left} className="!bg-blue-500 !w-3 !h-3" />

      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{icon}</span>
        <span className="text-xs font-semibold text-white">{label}</span>
        <span className={`w-2.5 h-2.5 rounded-full ml-auto ${STATUS_COLORS[status]}`} />
      </div>

      <p className="text-[10px] text-gray-500 leading-tight">{description}</p>

      {status === 'running' && (
        <div className="mt-2 flex items-center gap-1">
          <span className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-[10px] text-blue-400">Processing...</span>
        </div>
      )}

      {expanded && result && (
        <div className="mt-3 bg-gray-800 rounded-lg p-2 max-h-[200px] overflow-y-auto">
          <pre className="text-[9px] text-gray-300 whitespace-pre-wrap break-words">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {status === 'error' && data.error && (
        <div className="mt-2 text-[10px] text-red-400 bg-red-900/30 rounded p-1">
          {data.error}
        </div>
      )}

      <Handle type="source" position={Position.Right} className="!bg-blue-500 !w-3 !h-3" />
    </div>
  );
}
