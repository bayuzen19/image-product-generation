import axios from 'axios';

export async function runPipeline(productFile, logoFile, modelFile, callbacks) {
  const formData = new FormData();
  formData.append('product_image', productFile);
  if (logoFile) {
    formData.append('logo_image', logoFile);
  }
  if (modelFile) {
    formData.append('model_image', modelFile);
  }

  try {
    const response = await fetch('/api/pipeline/run', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Pipeline request failed: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data: ')) continue;

        try {
          const data = JSON.parse(trimmed.slice(6));

          if (data.type === 'complete') {
            callbacks.onComplete?.();
            return;
          }

          if (data.agent) {
            callbacks.onAgentUpdate?.(data.agent, data.status, data.result || null);
          }

          if (data.status === 'error') {
            callbacks.onError?.(data.error || 'Unknown agent error');
            return;
          }
        } catch {
          // skip non-JSON lines
        }
      }
    }
  } catch (err) {
    callbacks.onError?.(err.message);
  }
}

export async function generateImage(positivePrompt, productFile, magazineMode = false, productInfo = {}, logoFile = null, modelFile = null, scenicBackground = false) {
  const formData = new FormData();
  formData.append('positive_prompt', positivePrompt);
  formData.append('magazine_mode', magazineMode ? 'true' : 'false');
  formData.append('scenic_background', scenicBackground ? 'true' : 'false');
  formData.append('product_info', JSON.stringify(productInfo));
  if (productFile) {
    formData.append('product_image', productFile);
  }
  if (logoFile) {
    formData.append('logo_image', logoFile);
  }
  if (modelFile) {
    formData.append('model_image', modelFile);
  }
  const response = await axios.post('/api/generate-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}
