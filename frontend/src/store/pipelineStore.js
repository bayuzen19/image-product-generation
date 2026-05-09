import { create } from 'zustand';

const usePipelineStore = create((set) => ({
  productFile: null,
  logoFile: null,
  modelFile: null,
  agentStatuses: {
    analysis: 'idle',
    product: 'idle',
    editor: 'idle',
    prompt: 'idle',
  },
  agentResults: {
    analysis: null,
    product: null,
    editor: null,
    prompt: null,
  },
  finalPrompts: null,
  generatedImage: null,
  isRunning: false,
  error: null,
  selectedNodeId: null,

  setProductFile: (file) => set({ productFile: file }),
  setLogoFile: (file) => set({ logoFile: file }),
  setModelFile: (file) => set({ modelFile: file }),

  updateAgent: (agentId, status, result = null) =>
    set((state) => ({
      agentStatuses: { ...state.agentStatuses, [agentId]: status },
      agentResults: result
        ? { ...state.agentResults, [agentId]: result }
        : state.agentResults,
    })),

  setFinalPrompts: (prompts) => set({ finalPrompts: prompts }),
  setGeneratedImage: (base64) => set({ generatedImage: base64 }),
  setRunning: (bool) => set({ isRunning: bool }),
  setError: (msg) => set({ error: msg }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),

  reset: () =>
    set({
      agentStatuses: {
        analysis: 'idle',
        product: 'idle',
        editor: 'idle',
        prompt: 'idle',
      },
      agentResults: {
        analysis: null,
        product: null,
        editor: null,
        prompt: null,
      },
      finalPrompts: null,
      generatedImage: null,
      isRunning: false,
      error: null,
      selectedNodeId: null,
    }),
}));

export default usePipelineStore;
