import json
import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from agents import analysis_agent, product_agent, editor_agent, prompt_agent
from services import image_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="MockupGen AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def run_pipeline(product_bytes: bytes, logo_bytes: bytes | None, model_bytes: bytes | None):
    agents = [
        ("analysis", lambda: analysis_agent.run(product_bytes, logo_bytes, model_bytes)),
        ("product", None),
        ("editor", None),
        ("prompt", None),
    ]

    results = {}

    # --- Analysis Agent ---
    yield sse_event({"agent": "analysis", "status": "running"})
    try:
        analysis_result = await asyncio.to_thread(analysis_agent.run, product_bytes, logo_bytes, model_bytes)
        results["analysis"] = analysis_result
        yield sse_event({"agent": "analysis", "status": "done", "result": analysis_result})
    except Exception as e:
        yield sse_event({"agent": "analysis", "status": "error", "error": str(e)})
        return

    # --- Product Agent ---
    yield sse_event({"agent": "product", "status": "running"})
    try:
        product_result = await asyncio.to_thread(product_agent.run, results["analysis"], product_bytes, logo_bytes, model_bytes)
        results["product"] = product_result
        yield sse_event({"agent": "product", "status": "done", "result": product_result})
    except Exception as e:
        yield sse_event({"agent": "product", "status": "error", "error": str(e)})
        return

    # --- Editor Agent ---
    yield sse_event({"agent": "editor", "status": "running"})
    try:
        editor_result = await asyncio.to_thread(editor_agent.run, results["analysis"], results["product"], product_bytes, logo_bytes, model_bytes)
        results["editor"] = editor_result
        yield sse_event({"agent": "editor", "status": "done", "result": editor_result})
    except Exception as e:
        yield sse_event({"agent": "editor", "status": "error", "error": str(e)})
        return

    # --- Prompt Agent ---
    yield sse_event({"agent": "prompt", "status": "running"})
    try:
        prompt_result = await asyncio.to_thread(
            prompt_agent.run, results["analysis"], results["product"], results["editor"], product_bytes, logo_bytes, model_bytes
        )
        results["prompt"] = prompt_result
        yield sse_event({"agent": "prompt", "status": "done", "result": prompt_result})
    except Exception as e:
        yield sse_event({"agent": "prompt", "status": "error", "error": str(e)})
        return

    yield sse_event({"type": "complete"})


@app.post("/api/pipeline/run")
async def pipeline_run(
    product_image: UploadFile = File(...),
    logo_image: UploadFile | None = File(None),
    model_image: UploadFile | None = File(None),
):
    product_bytes = await product_image.read()
    logo_bytes = None
    if logo_image:
        logo_bytes = await logo_image.read()
    model_bytes = None
    if model_image:
        model_bytes = await model_image.read()

    return StreamingResponse(
        run_pipeline(product_bytes, logo_bytes, model_bytes),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/generate-image")
async def generate_image_endpoint(
    positive_prompt: str = Form(...),
    magazine_mode: str = Form("false"),
    scenic_background: str = Form("false"),
    product_info: str = Form("{}"),
    product_image: UploadFile | None = File(None),
    logo_image: UploadFile | None = File(None),
    model_image: UploadFile | None = File(None),
):
    if not positive_prompt:
        return JSONResponse(status_code=400, content={"error": "positive_prompt is required"})

    product_bytes = None
    filename = None
    if product_image:
        product_bytes = await product_image.read()
        filename = product_image.filename

    logo_bytes = None
    if logo_image:
        logo_bytes = await logo_image.read()

    model_bytes = None
    if model_image:
        model_bytes = await model_image.read()

    is_magazine = magazine_mode.lower() in ("true", "1", "yes")
    is_scenic_bg = scenic_background.lower() in ("true", "1", "yes")

    info_dict = {}
    if product_info and product_info != "{}":
        try:
            info_dict = json.loads(product_info)
        except json.JSONDecodeError:
            pass

    try:
        result = await asyncio.to_thread(
            image_service.generate_image,
            positive_prompt,
            product_bytes,
            is_magazine,
            info_dict,
            filename,
            logo_bytes,
            model_bytes,
            is_scenic_bg,
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/health")
async def health():
    return {"status": "ok"}
