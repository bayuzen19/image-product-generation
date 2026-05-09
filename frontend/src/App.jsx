import UploadPanel from './components/UploadPanel';
import PipelineFlow from './components/PipelineFlow';
import PromptResult from './components/PromptResult';
import GeneratedImage from './components/GeneratedImage';
import NodeDetailModal from './components/NodeDetailModal';
import usePipelineStore from './store/pipelineStore';

export default function App() {
  const finalPrompts = usePipelineStore((s) => s.finalPrompts);
  const selectedNodeId = usePipelineStore((s) => s.selectedNodeId);
  const setSelectedNodeId = usePipelineStore((s) => s.setSelectedNodeId);
  const agentStatuses = usePipelineStore((s) => s.agentStatuses);
  const agentResults = usePipelineStore((s) => s.agentResults);

  const getNodeStatus = (id) => {
    if (id === 'upload' || id === 'output') return 'idle';
    return agentStatuses[id] || 'idle';
  };

  const getNodeResult = (id) => {
    if (id === 'upload' || id === 'output') return null;
    return agentResults[id] || null;
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          MockupGen AI
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          AI-powered product mockup generation pipeline — click any node to see details
        </p>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-4 flex flex-col gap-4 max-w-[1600px] mx-auto w-full">
        {/* Upload Panel */}
        <UploadPanel />

        {/* Pipeline Visualization */}
        <PipelineFlow />

        {/* Results */}
        {finalPrompts && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <PromptResult />
            <GeneratedImage />
          </div>
        )}
      </main>

      {/* Node Detail Modal */}
      {selectedNodeId && (
        <NodeDetailModal
          nodeId={selectedNodeId}
          status={getNodeStatus(selectedNodeId)}
          result={getNodeResult(selectedNodeId)}
          onClose={() => setSelectedNodeId(null)}
        />
      )}
    </div>
  );
}
