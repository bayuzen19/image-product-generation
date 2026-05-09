# MockupGen AI — Product Image Generation

An AI-powered SaaS application that generates photorealistic product mockups, fashion editorials, and magazine covers from a single product photo. Powered by Google Gemini and a multi-agent pipeline.

## ✨ Features

- **Photorealistic Product Mockups** — Generate studio-quality product shots with natural lighting, shadows, and environmental integration
- **Fashion Model Integration** — Upload a model reference photo and the AI preserves their exact face/identity while wearing your product
- **Magazine Cover Generation** — Automatically creates professional magazine covers with masthead, article teasers, and depth layering
- **Logo/Brand Preservation** — Upload your brand logo (emblem, crest, or text) and it's faithfully reproduced in every mockup
- **Multi-Agent Pipeline** — 4 specialized AI agents (Analysis → Product → Editor → Prompt) collaborate to produce optimal results
- **Visual Node Editor** — Interactive React Flow-based UI showing the agent pipeline in real-time
- **Dockerized** — Full Docker Compose setup for one-command deployment

## 🖼️ Generated Examples

| | |
|:---:|:---:|
| ![Magazine Cover](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-83.png) | ![Fashion Editorial](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-82.png) |
| ![Product Shot](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-81.png) | ![Scenic Mockup](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-80.png) |
| ![Magazine Cover Nike](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-75.png) | ![Fashion Editorial](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-74.png) |
| ![Magazine Style](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-73.png) | ![Product Mockup](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-72.png) |
| ![Product Photography](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-70.png) | ![Scenic Product](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-69.png) |
| ![Fashion Model](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-66.png) | ![Magazine Layout](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-65.png) |
| ![Product Photography](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-64.png) | ![Editorial Shot](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-62.png) |
| ![Brand Mockup](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-61.png) | ![Creative Mockup](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-59.png) |
| ![Scenic Shot](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-58.png) | ![Product Design](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-54.png) |
| ![Product Mockup](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-35.png) | ![Studio Shot](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-26.png) |
| ![Mockup Style](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-8.png) | ![Product Render](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-4.png) |
| ![Creative Shot](https://raw.githubusercontent.com/bayuzen19/image-product-generation/main/images/mockup-generated-2.png) | |

## 🏗️ Architecture

```
mockupgen/
├── backend/                 # FastAPI Python backend
│   ├── agents/              # Multi-agent AI pipeline
│   │   ├── analysis_agent.py    # Analyzes product, logo, model inputs
│   │   ├── product_agent.py     # Generates creative direction & layout
│   │   ├── editor_agent.py      # Determines lighting & environment settings
│   │   └── prompt_agent.py      # Crafts final image generation prompt
│   ├── services/
│   │   ├── image_service.py     # Core image generation with Gemini
│   │   └── gemini_service.py    # Gemini API client wrapper
│   ├── models/schemas.py        # Pydantic request/response models
│   ├── utils/image_utils.py     # Image processing utilities
│   ├── main.py                  # FastAPI app with SSE streaming
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── PipelineFlow.jsx     # React Flow node editor
│   │   │   ├── UploadPanel.jsx      # Image upload interface
│   │   │   ├── GeneratedImage.jsx   # Result display
│   │   │   └── nodes/              # Custom flow nodes
│   │   ├── services/               # API client
│   │   ├── store/                  # Zustand state management
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── images/                  # Generated example outputs
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended)

```bash
docker-compose up --build
```

The app will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## ⚙️ Environment Variables

Create `backend/.env` with:

```env
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
IMAGEN_MODEL=nano-banana-pro-preview
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, React Flow, Zustand, Tailwind CSS |
| Backend | Python, FastAPI, Uvicorn |
| AI/ML | Google Gemini (text + image generation) |
| Infrastructure | Docker, Docker Compose |

## 📋 How It Works

1. **Upload** — User uploads a product image, optional logo, and optional fashion model reference
2. **Analysis Agent** — Analyzes the product type, colors, brand identity, and model features
3. **Product Agent** — Generates creative direction (environment, mood, typography, layout patterns)
4. **Editor Agent** — Determines optimal lighting, camera angles, and post-processing settings
5. **Prompt Agent** — Synthesizes all agent outputs into a final optimized prompt
6. **Image Generation** — Gemini generates the photorealistic mockup with all constraints applied
7. **Streaming** — Results stream back via SSE, showing each agent's progress in the node editor

## 📄 License

MIT
