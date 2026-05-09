import { useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import UploadNode from './nodes/UploadNode';
import AgentNode from './nodes/AgentNode';
import PromptNode from './nodes/PromptNode';
import OutputNode from './nodes/OutputNode';
import usePipelineStore from '../store/pipelineStore';

const nodeTypes = {
  uploadNode: UploadNode,
  agentNode: AgentNode,
  promptNode: PromptNode,
  outputNode: OutputNode,
};

const AGENT_META = {
  analysis: { label: 'Analysis Agent', description: 'Detects shape, color, logo', icon: '🔍' },
  product: { label: 'Product Agent', description: 'Recommends style & layout', icon: '📦' },
  editor: { label: 'Editor Agent', description: 'Refines lighting & quality', icon: '✏️' },
  prompt: { label: 'Prompt Agent', description: 'Generates final prompts', icon: '✨' },
};

function buildInitialNodes(agentStatuses, agentResults) {
  return [
    {
      id: 'upload',
      type: 'uploadNode',
      position: { x: 0, y: 150 },
      data: {},
    },
    {
      id: 'analysis',
      type: 'agentNode',
      position: { x: 250, y: 100 },
      data: {
        ...AGENT_META.analysis,
        status: agentStatuses.analysis,
        result: agentResults.analysis,
      },
    },
    {
      id: 'product',
      type: 'agentNode',
      position: { x: 500, y: 100 },
      data: {
        ...AGENT_META.product,
        status: agentStatuses.product,
        result: agentResults.product,
      },
    },
    {
      id: 'editor',
      type: 'agentNode',
      position: { x: 750, y: 100 },
      data: {
        ...AGENT_META.editor,
        status: agentStatuses.editor,
        result: agentResults.editor,
      },
    },
    {
      id: 'prompt-node',
      type: 'promptNode',
      position: { x: 1000, y: 50 },
      data: {},
    },
    {
      id: 'output',
      type: 'outputNode',
      position: { x: 1300, y: 100 },
      data: {},
    },
  ];
}

function getEdgeStyle(sourceStatus) {
  switch (sourceStatus) {
    case 'done':
      return { stroke: '#22c55e', strokeWidth: 2 };
    case 'running':
      return { stroke: '#3b82f6', strokeWidth: 2 };
    case 'error':
      return { stroke: '#ef4444', strokeWidth: 2 };
    default:
      return { stroke: '#4b5563', strokeWidth: 1.5 };
  }
}

function buildEdges(agentStatuses, isRunning) {
  const productFileStatus = isRunning || Object.values(agentStatuses).some((s) => s !== 'idle') ? 'done' : 'idle';

  return [
    {
      id: 'e-upload-analysis',
      source: 'upload',
      target: 'analysis',
      animated: isRunning,
      style: getEdgeStyle(productFileStatus),
    },
    {
      id: 'e-analysis-product',
      source: 'analysis',
      target: 'product',
      animated: agentStatuses.analysis === 'running',
      style: getEdgeStyle(agentStatuses.analysis),
    },
    {
      id: 'e-product-editor',
      source: 'product',
      target: 'editor',
      animated: agentStatuses.product === 'running',
      style: getEdgeStyle(agentStatuses.product),
    },
    {
      id: 'e-editor-prompt',
      source: 'editor',
      target: 'prompt-node',
      animated: agentStatuses.editor === 'running',
      style: getEdgeStyle(agentStatuses.editor),
    },
    {
      id: 'e-prompt-output',
      source: 'prompt-node',
      target: 'output',
      animated: agentStatuses.prompt === 'running',
      style: getEdgeStyle(agentStatuses.prompt),
    },
  ];
}

export default function PipelineFlow() {
  const agentStatuses = usePipelineStore((s) => s.agentStatuses);
  const agentResults = usePipelineStore((s) => s.agentResults);
  const isRunning = usePipelineStore((s) => s.isRunning);
  const setSelectedNodeId = usePipelineStore((s) => s.setSelectedNodeId);

  const [nodes, setNodes, onNodesChange] = useNodesState(
    buildInitialNodes(agentStatuses, agentResults)
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    buildEdges(agentStatuses, isRunning)
  );

  // Update nodes & edges when store changes
  useEffect(() => {
    setNodes(buildInitialNodes(agentStatuses, agentResults));
    setEdges(buildEdges(agentStatuses, isRunning));
  }, [agentStatuses, agentResults, isRunning, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_, node) => {
      const id = node.id === 'prompt-node' ? 'prompt' : node.id;
      setSelectedNodeId(id);
    },
    [setSelectedNodeId]
  );

  return (
    <div className="h-[500px] bg-gray-950 rounded-xl border border-gray-800 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        minZoom={0.3}
        maxZoom={1.5}
      >
        <Background variant="dots" gap={20} size={1} color="#1f2937" />
        <Controls className="!bg-gray-800 !border-gray-700 !rounded-lg" />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'uploadNode') return '#3b82f6';
            if (node.type === 'outputNode') return '#8b5cf6';
            const status = node.data?.status;
            if (status === 'done') return '#22c55e';
            if (status === 'running') return '#3b82f6';
            if (status === 'error') return '#ef4444';
            return '#4b5563';
          }}
          className="!bg-gray-900 !border-gray-800"
        />
      </ReactFlow>
    </div>
  );
}
