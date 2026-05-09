import { useCallback, useRef } from 'react';
import { Upload, Image as ImageIcon, User } from 'lucide-react';
import usePipelineStore from '../store/pipelineStore';
import { runPipeline } from '../services/api';

export default function UploadPanel() {
  const {
    productFile,
    logoFile,
    modelFile,
    isRunning,
    error,
    setProductFile,
    setLogoFile,
    setModelFile,
    setRunning,
    setError,
    updateAgent,
    setFinalPrompts,
    reset,
  } = usePipelineStore();

  const productInputRef = useRef(null);
  const logoInputRef = useRef(null);
  const modelInputRef = useRef(null);

  const handleProductDrop = useCallback(
    (e) => {
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
      if (file && file.type.startsWith('image/')) setProductFile(file);
    },
    [setProductFile]
  );

  const handleLogoDrop = useCallback(
    (e) => {
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
      if (file && file.type.startsWith('image/')) setLogoFile(file);
    },
    [setLogoFile]
  );

  const handleModelDrop = useCallback(
    (e) => {
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
      if (file && file.type.startsWith('image/')) setModelFile(file);
    },
    [setModelFile]
  );

  const handleRun = async () => {
    if (!productFile || isRunning) return;
    reset();
    setProductFile(productFile);
    if (logoFile) setLogoFile(logoFile);
    if (modelFile) setModelFile(modelFile);
    setRunning(true);
    setError(null);

    await runPipeline(productFile, logoFile, modelFile, {
      onAgentUpdate: (agent, status, result) => {
        updateAgent(agent, status, result);
        if (agent === 'prompt' && status === 'done' && result) {
          setFinalPrompts(result);
        }
      },
      onComplete: () => {
        setRunning(false);
      },
      onError: (msg) => {
        setError(msg);
        setRunning(false);
      },
    });
  };

  const preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-4">
      <div className="flex gap-6 items-start">
        {/* Product Image Upload */}
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-400 mb-2 block">
            Product Image <span className="text-red-400">*</span>
          </label>
          <div
            className="border-2 border-dashed border-gray-700 rounded-lg p-4 text-center cursor-pointer
              hover:border-blue-500 transition-colors min-h-[120px] flex flex-col items-center justify-center"
            onDrop={handleProductDrop}
            onDragOver={preventDefaults}
            onDragEnter={preventDefaults}
            onClick={() => productInputRef.current?.click()}
          >
            {productFile ? (
              <div className="flex flex-col items-center gap-2">
                <img
                  src={URL.createObjectURL(productFile)}
                  alt="Product"
                  className="h-16 w-16 object-cover rounded-lg"
                />
                <span className="text-xs text-gray-400 truncate max-w-[150px]">
                  {productFile.name}
                </span>
              </div>
            ) : (
              <>
                <Upload className="w-8 h-8 text-gray-500 mb-2" />
                <span className="text-sm text-gray-500">Drop product image here</span>
              </>
            )}
            <input
              ref={productInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml,.svg,.webp"
              className="hidden"
              onChange={handleProductDrop}
            />
          </div>
        </div>

        {/* Logo Image Upload */}
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-400 mb-2 block">
            Logo Image <span className="text-gray-600">(optional)</span>
          </label>
          <div
            className="border-2 border-dashed border-gray-700 rounded-lg p-4 text-center cursor-pointer
              hover:border-purple-500 transition-colors min-h-[120px] flex flex-col items-center justify-center"
            onDrop={handleLogoDrop}
            onDragOver={preventDefaults}
            onDragEnter={preventDefaults}
            onClick={() => logoInputRef.current?.click()}
          >
            {logoFile ? (
              <div className="flex flex-col items-center gap-2">
                <img
                  src={URL.createObjectURL(logoFile)}
                  alt="Logo"
                  className="h-16 w-16 object-contain rounded-lg"
                />
                <span className="text-xs text-gray-400 truncate max-w-[150px]">
                  {logoFile.name}
                </span>
              </div>
            ) : (
              <>
                <ImageIcon className="w-8 h-8 text-gray-500 mb-2" />
                <span className="text-sm text-gray-500">Drop logo image here</span>
              </>
            )}
            <input
              ref={logoInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml,.svg,.webp"
              className="hidden"
              onChange={handleLogoDrop}
            />
          </div>
        </div>

        {/* Fashion Model Upload */}
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-400 mb-2 block">
            Fashion Model <span className="text-gray-600">(optional)</span>
          </label>
          <div
            className="border-2 border-dashed border-gray-700 rounded-lg p-4 text-center cursor-pointer
              hover:border-pink-500 transition-colors min-h-[120px] flex flex-col items-center justify-center"
            onDrop={handleModelDrop}
            onDragOver={preventDefaults}
            onDragEnter={preventDefaults}
            onClick={() => modelInputRef.current?.click()}
          >
            {modelFile ? (
              <div className="flex flex-col items-center gap-2">
                <img
                  src={URL.createObjectURL(modelFile)}
                  alt="Model"
                  className="h-16 w-16 object-cover rounded-lg"
                />
                <span className="text-xs text-gray-400 truncate max-w-[150px]">
                  {modelFile.name}
                </span>
              </div>
            ) : (
              <>
                <User className="w-8 h-8 text-gray-500 mb-2" />
                <span className="text-sm text-gray-500">Drop model photo here</span>
              </>
            )}
            <input
              ref={modelInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              className="hidden"
              onChange={handleModelDrop}
            />
          </div>
        </div>

        {/* Run Button */}
        <div className="flex flex-col items-center justify-center min-h-[120px] pt-6">
          <button
            onClick={handleRun}
            disabled={!productFile || isRunning}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500
              text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
          >
            {isRunning ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Running...
              </span>
            ) : (
              'Run Pipeline'
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
