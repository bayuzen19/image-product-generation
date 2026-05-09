import { X } from 'lucide-react';

const STATUS_LABELS = {
  idle: { text: 'Waiting', color: 'text-gray-400', bg: 'bg-gray-700' },
  running: { text: 'Processing...', color: 'text-blue-400', bg: 'bg-blue-900/50' },
  done: { text: 'Completed', color: 'text-green-400', bg: 'bg-green-900/50' },
  error: { text: 'Error', color: 'text-red-400', bg: 'bg-red-900/50' },
};

const AGENT_INFO = {
  upload: {
    title: '📤 Upload Node',
    description: 'Upload product and logo images to start the pipeline.',
  },
  analysis: {
    title: '🔍 Analysis Agent',
    description:
      'Analyzes the uploaded product image and logo to detect shape, color, finish, label area, and logo properties.',
  },
  product: {
    title: '📦 Product Agent',
    description:
      'Recommends bottle color, logo treatment, layout positioning, background style, and creative direction.',
  },
  editor: {
    title: '✏️ Editor Agent',
    description:
      'Refines the prompt with lighting setup, camera angle, quality boosters, risk flags, and negative terms.',
  },
  prompt: {
    title: '✨ Prompt Agent',
    description:
      'Generates the final positive/negative prompts optimized for Midjourney, Stable Diffusion, and DALL-E.',
  },
  output: {
    title: '🖼️ Output Node',
    description: 'Displays the generated mockup image using Imagen 3 or your preferred image generation tool.',
  },
};

export default function NodeDetailModal({ nodeId, status, result, error, onClose }) {
  if (!nodeId) return null;

  const info = AGENT_INFO[nodeId] || { title: nodeId, description: '' };
  const statusInfo = STATUS_LABELS[status] || STATUS_LABELS.idle;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <h2 className="text-lg font-bold text-white">{info.title}</h2>
            <p className="text-xs text-gray-500 mt-0.5">{info.description}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Status Badge */}
        <div className="px-6 pt-4">
          <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${statusInfo.bg} ${statusInfo.color}`}>
            {status === 'running' && (
              <span className="w-2 h-2 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            {status === 'done' && <span className="w-2 h-2 rounded-full bg-green-400" />}
            {status === 'error' && <span className="w-2 h-2 rounded-full bg-red-400" />}
            {status === 'idle' && <span className="w-2 h-2 rounded-full bg-gray-500" />}
            {statusInfo.text}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
              <span className="font-semibold">Error: </span>{error}
            </div>
          )}

          {result ? (
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-2">Agent Output</h3>

              {/* Render key fields as cards */}
              <div className="space-y-3 mb-4">
                {Object.entries(result).map(([key, value]) => (
                  <div key={key} className="bg-gray-800/80 rounded-lg p-3">
                    <div className="text-xs font-semibold text-blue-400 mb-1">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    </div>
                    {typeof value === 'string' ? (
                      <p className="text-sm text-gray-300">{value}</p>
                    ) : Array.isArray(value) ? (
                      <div className="space-y-1">
                        {value.map((item, i) => (
                          <div key={i} className="text-sm text-gray-300">
                            {typeof item === 'object' ? (
                              <pre className="text-xs text-gray-400 whitespace-pre-wrap">
                                {JSON.stringify(item, null, 2)}
                              </pre>
                            ) : (
                              <span className="inline-block bg-gray-700 rounded px-2 py-0.5 text-xs mr-1 mb-1">
                                {String(item)}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : typeof value === 'object' && value !== null ? (
                      <div className="grid grid-cols-2 gap-1">
                        {Object.entries(value).map(([k, v]) => (
                          <div key={k} className="text-xs">
                            <span className="text-gray-500">{k.replace(/_/g, ' ')}: </span>
                            <span className="text-gray-300">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-300">{String(value)}</p>
                    )}
                  </div>
                ))}
              </div>

              {/* Raw JSON toggle */}
              <details className="mt-2">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300 transition-colors">
                  View Raw JSON
                </summary>
                <pre className="mt-2 text-xs text-gray-400 bg-gray-800 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap break-words max-h-[300px] overflow-y-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          ) : status === 'idle' ? (
            <p className="text-sm text-gray-500 italic">
              This agent hasn't run yet. Start the pipeline to see results.
            </p>
          ) : status === 'running' ? (
            <div className="flex items-center gap-3 py-8 justify-center">
              <span className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-blue-400">Agent is processing...</span>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
