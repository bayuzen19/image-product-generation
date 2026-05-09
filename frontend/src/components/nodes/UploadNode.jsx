import { Handle, Position } from '@xyflow/react';
import { Upload, ImageIcon } from 'lucide-react';
import usePipelineStore from '../../store/pipelineStore';

export default function UploadNode() {
  const productFile = usePipelineStore((s) => s.productFile);
  const logoFile = usePipelineStore((s) => s.logoFile);

  const ready = !!productFile;

  return (
    <div
      className={`bg-gray-900 rounded-xl p-4 min-w-[160px] border-2 transition-colors ${
        ready ? 'border-green-500' : 'border-gray-700'
      }`}
    >
      <div className="text-xs font-semibold text-gray-400 mb-3 text-center">📤 Upload</div>

      <div className="space-y-2">
        {/* Product thumbnail */}
        <div className="flex items-center gap-2">
          {productFile ? (
            <>
              <img
                src={URL.createObjectURL(productFile)}
                alt="Product"
                className="w-10 h-10 object-cover rounded"
              />
              <span className="text-[10px] text-gray-400 truncate max-w-[80px]">
                Product ✓
              </span>
            </>
          ) : (
            <>
              <div className="w-10 h-10 bg-gray-800 rounded flex items-center justify-center">
                <Upload className="w-4 h-4 text-gray-600" />
              </div>
              <span className="text-[10px] text-gray-600">No product</span>
            </>
          )}
        </div>

        {/* Logo thumbnail */}
        <div className="flex items-center gap-2">
          {logoFile ? (
            <>
              <img
                src={URL.createObjectURL(logoFile)}
                alt="Logo"
                className="w-10 h-10 object-contain rounded"
              />
              <span className="text-[10px] text-gray-400 truncate max-w-[80px]">
                Logo ✓
              </span>
            </>
          ) : (
            <span className="text-[10px] text-gray-600 ml-12">No logo (optional)</span>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-blue-500 !w-3 !h-3" />
    </div>
  );
}
