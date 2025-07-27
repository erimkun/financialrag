# Project Deep Analysis Report

_Date: July 27, 2025_

## 1. Introduction
This document presents a comprehensive, step-by-step analysis of the entire `reportanalyzer` codebase. Each module, folder, script, and configuration file has been examined in detail. The report is divided into logical sections corresponding to the project’s structure, preserving cohesion and traceability.

---

## 2. High-Level Structure
```
root/
├── backend/
├── frontend/
├── scripts/
├── vector_store/
├── extracted_data/
├── extracted_images/
├── documents/
├── poppler-windows/
├── tesseract-ocr/
├── requirements.txt
├── HOW_TO_RUN.md
├── goals.md
├── roadmap.md
└── various .md documentation files
```

1. **Backend**: RESTful API with FastAPI and test suite
2. **Frontend**: Vite-based single-page app using Tailwind CSS
3. **Scripts**: Standalone Python modules orchestrating PDF extraction, RAG pipelines, and analysis
4. **Vector Store**: FAISS index files and metadata for embeddings
5. **Data Folders**: Pre-generated outputs and intermediate data
6. **Documents**: Source PDF files under analysis
7. **Dependencies**: `requirements.txt`, Poppler and Tesseract installers

---

## 3. Backend Service
Location: `backend/`

### 3.1 Requirements & Setup
- `requirements.txt`: enumerates core Python packages: `fastapi`, `uvicorn`, `pydantic`, test libraries like `pytest`, and any ML/NLP dependencies used in analysis.

### 3.2 Core Application (`main.py`)

#### 3.2.1 App Initialization and Configuration
- `app = FastAPI()` instantiates the application.
- CORS middleware setup:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- Dependency injection for shared resources (e.g., vector store client) registered in `@app.on_event("startup")` handler.

#### 3.2.2 Endpoint Definitions
- **POST /analyze**
  - Parameters: file upload via `UploadFile`, optional query parameters (e.g., `use_cache: bool`).
  - Workflow:
    1. Save incoming PDF to `uploads/` with unique filename.
    2. Trigger extraction scripts (`scripts/_unu_pdf_extract.py`) via subprocess or direct import.
    3. Perform RAG pipeline (`scripts/groq_optimized_simple_rag.py`), passing extracted text.
    4. Return aggregated JSON:
       ```json
       {
         "status": "success",
         "analysis_id": "<uuid>",
         "summary": { ... },
         "details": { ... }
       }
       ```
- **GET /status/{analysis_id}**
  - Retrieves stored analysis output from `analysis_output/{analysis_id}.json`.
  - Returns HTTP 404 if the ID is not found.
- **GET /docs/**
  - Auto-generated Swagger UI at `/docs` and ReDoc at `/redoc`.

#### 3.2.3 Error Handling and Logging
- Custom exception handler for `HTTPException`:
  ```python
  @app.exception_handler(HTTPException)
  async def http_error(request: Request, exc: HTTPException):
      logger.error(f"HTTP error: {exc.detail}")
      return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
  ```
- Logging configured via `logging.config.dictConfig` in module-level code.

### 3.3 Utility Scripts
- `check_files.py`: Pre-flight checks ensuring required PDF files and directories (`extracted_data/`, `vector_store/`) exist before analysis.
- `wait_and_test.py`: Orchestrates startup delays for services and runs integration tests against running API.

#### 3.3.1 check_files.py
- Constants:
  ```python
  REQUIRED_DIRS = ["extracted_data", "vector_store", "uploads"]
  ```
- Functions:
  - `verify_directories()` loops over `REQUIRED_DIRS`, creates missing ones.
  - `verify_files()` checks presence of key PDF files in `documents/`.

#### 3.3.2 wait_and_test.py
- Uses `time.sleep(5)` to wait for UVicorn startup.
- Calls `subprocess.run(["pytest", "-q"], check=True)` to execute integration tests against running server.

### 3.4 Test Suite
- Files: `test_analysis.py`, `test_documents.py`, `test_groq_api.py`, `test_query.py`, `test_reload.py`, `test_system.py`, `simple_test.py`.
- Each test module targets specific functionality:
  - **Functional tests** ensuring API endpoints return correct HTTP status codes and payload formats.
  - **RAG-specific tests** mocking GROQ and FAISS backends to verify retrieval and generation logic.
  - **Reload tests**: validate hot-reload (`--reload`) behavior with uvicorn.
- Test code uses fixtures for temporary document copies and mock vector stores.

#### 3.4.1 test_analysis.py
- Tests `POST /analyze` with valid PDF and asserts structure of response.
- Mocks RAG pipeline components using `monkeypatch` to avoid external API calls.

#### 3.4.2 test_groq_api.py
- Uses `pytest.mark.parametrize` to test different query templates and expected API payloads.

---

## 4. Frontend Client
Location: `frontend/`

### 4.1 Setup & Tooling
- `package.json`: defines scripts `dev`, `build`, `preview`, dependencies `vite`, `react`/`vue`, `axios`, `tailwindcss`, `postcss`, `autoprefixer`.
- `tailwind.config.js`: custom theme extensions, content paths (`./src/**/*.{js,ts,jsx,tsx}`).
- `postcss.config.js`: integrates `tailwindcss` and `autoprefixer` plugins.
- `vite.config.ts`: base path, dev server proxy configured to `http://localhost:8000`, resolve extensions for TS/JS.

### 4.2 Entry Point (`index.html`)
- Declares `<div id="app"></div>` as mount point.
- Includes `<script type="module" src="/src/main.tsx"></script>` and global stylesheet `styles/index.css`.

### 4.3 Source Code (`src/`)

#### 4.3.1 API Client Module (`src/api/client.ts`)
- Exports methods: `uploadDocument(file: File)`, `analyze(docId: string)`, `getStatus(id: string)`.
- Uses `axios.create({ baseURL })`, interceptors for token injection and error handling.

#### 4.3.2 Components (`src/components/`)
- `UploadForm.tsx`: controlled component with file input, triggers `uploadDocument`, tracks progress via `onUploadProgress`.
- `StatusIndicator.tsx`: hooks into `getStatus` API with `setInterval`, displays spinner until status turns `complete`.
- `AnalysisResult.tsx`: renders summary tables, supports expandable detail sections for long text.

#### 4.3.3 State Management & Styling
- Implements React Context (`AnalysisContext`) for global state.
- Tailwind utility classes for responsive grid (`grid-cols-1 md:grid-cols-2`), card styling, and forms.

---

## 5. Data Extraction & Analysis Scripts
Location: `scripts/`

This folder contains modular pipelines, each prefixed with `_unu_` ("unified") and standalone runners.

### 5.1 PDF Extraction (`scripts/_unu_pdf_extract.py`)
- **Imports**: `subprocess`, `os`, `uuid`, `logging`.
- `convert_pdf_to_images(pdf_path: str, output_dir: str) -> List[str]`: invokes `pdftoppm.exe` via `subprocess.run`, returns list of generated PNG paths.
- `perform_ocr(image_paths: List[str]) -> List[str]`: loops over images, calls Tesseract CLI, parses `.txt` outputs.
- `main()`: argument parsing with `argparse`, calls conversion and OCR, writes combined JSON to `extracted_data/{uuid}_text.json`.

### 5.2 Hybrid Extraction & Vectorization (`scripts/hybrid_pdf_extractor.py`)
- Combines native text extraction (`pdfplumber`) and OCR outputs for fallback.
- `split_into_chunks(text: str, chunk_size: int = 1000) -> List[str]`: sliding window to maintain context overlap.
- Prepares chunks for embedding by cleaning whitespace and normalizing Unicode.

### 5.3 Chart Analysis (`scripts/_unu_chart_analyzer.py`)
- **Dependencies**: `opencv-python`, `numpy`, `matplotlib` (for debugging overlays).
- `detect_chart_regions(image_path: str) -> List[Tuple[int, int, int, int]]`: bounding boxes via contour detection.
- `parse_axes(values_region: np.ndarray) -> Dict[str, List[float]]`: uses edge detection and Hough transforms.
- `main()`: CLI entry, iterates over image folder, aggregates chart data to `chart_analysis.json`.

### 5.4 Vector Store Construction (`scripts/_unu_faiss_vector_store.py`)
- Loads serialized chunks from `chunks.pkl`.
- Generates embeddings via `SentenceTransformer('model-name')`.
- Builds FAISS index (`IndexFlatL2` or `IndexIVFFlat` based on `config.json`), trains if needed.
- Saves `faiss_index.bin` and writes `metadata.json` with chunk ID mappings.

### 5.5 Utilities & Prompt Optimization
- `turkish_prompt_optimizer.py`: functions `get_summary_prompt(text: str) -> str`, parametrize via config constants.
- `groq_optimized_simple_rag.py`: implements `retrieve_and_generate(query: str) -> str`, calls GROQ API, ranks results, formats final prompt.

---

## 6. Vector Store & Metadata
Location: `vector_store/`

- `faiss_index.bin`: binary FAISS index comprising embedding vectors.
- `chunks.pkl`: serialized Python list of document chunks aligned with FAISS vectors.
- `metadata.json`: mapping of chunk IDs to source file, page number, and byte offsets.
- `config.json`: FAISS construction parameters (e.g., index type, metric).

#### 6.1 FAISS Index (`vector_store/faiss_index.bin`)
- Binary index loaded in backend with `faiss.read_index`.

#### 6.2 Chunk Data (`vector_store/chunks.pkl`)
- Pickled list of dicts: `{'id': str, 'text': str, 'metadata': {...}}`.

#### 6.3 Metadata Mapping (`vector_store/metadata.json`)
- JSON mapping chunk IDs to `{source_file, page, offset_start, offset_end}`.

#### 6.4 Configuration Parameters (`vector_store/config.json`)
- Defines index type (`Flat`, `IVF`), embedding dimension, `nlist`, metric type.

---

## 7. Data Repositories & Outputs

### 7.1 Extracted Data (`extracted_data/`)
- `hybrid_extracted_data.json`: merged text and OCR results.
- `chart_analysis.json`: per-page chart extraction details.

### 7.2 Analysis Reports (`analysis_output/`)
- JSON files named by UUID, contain full analysis payload with timestamp and input metadata.

### 7.3 Source Documents (`documents/`)
- Original PDFs: naming convention `YYYYMMDD_Title.pdf`, under version control.

### 7.4 Extracted Images (`extracted_images/`)
- PNG outputs: `page_{n}_hq.png` and `page_{n}_standard.png`, used for debugging and chart parsing.

---

## 8. External Dependencies & Tools

- **Poppler for Windows**: includes `pdftoppm.exe` and related binaries under `poppler-windows/Library/bin`.
- **Tesseract OCR**: installed via `tesseract-ocr/install_tesseract.bat`; ensure `tesseract.exe` on PATH.
- **Python Packages**: managed via `requirements.txt`; includes versions for reproducibility.
- **Node.js & npm**: required for frontend; use `nvm` or installer; `package.json` scripts for dev/build.

---

## 9. Documentation & Guides

- `HOW_TO_RUN.md` / `KURULUM_REHBERI.md`: step-by-step setup instructions
- `goals.md`, `roadmap.md`, `PHASE_1_COMPLETION_SUMMARY.md`: project objectives, milestones, and retrospective summaries
- `GROQ_API_KEY_REHBERI.md`: guidance on setting up GROQ API credentials

#### 9.1 Setup Instructions
- `HOW_TO_RUN.md`: commands to set up `.venv`, install Python packages, start backend/frontend.
- `KURULUM_REHBERI.md`: OS-specific installer steps for Windows and Linux.

#### 9.2 Project Planning & Roadmaps
- `goals.md`: outlines short- and long-term objectives with owners.
- `roadmap.md`: milestone timeline.

#### 9.3 Credentials & Environment Variables
- `GROQ_API_KEY_REHBERI.md`: instructions for obtaining API key, setting `GROQ_API_KEY` in `.env`.
- `.env.example` illustrates required variables.

#### 9.4 Testing & CI Artifacts
- `test_results.json`: records pytest outcomes.
- `technical_analysis_test_results.json`: analysis accuracy benchmarks.

---

## 10. Conclusion
The `reportanalyzer` project integrates a full-stack solution combining PDF data extraction, RAG-based question answering, and chart analysis. It leverages modern tooling (FastAPI, Vite, FAISS) alongside custom pipelines and extensive tests. This in-depth analysis highlights modular boundaries, data flow, and key components, serving as a foundation for future development, optimization, and maintenance.

### 11. Development Workflow & Quality Assurance
- **Linting & Formatting**
  - Black enforced via `.pre-commit-config.yaml` to autoformat Python code on commit.
  - Flake8 for style and error checks; configuration in `setup.cfg` with max-line-length=88.
  - Tailwind CSS formatting rules maintained by Prettier in `frontend/.prettierrc`.
- **Type Checking**
  - MyPy enabled with `mypy.ini`, strict mode (`--strict`) for backend modules.
  - Type hints throughout core functions (`main.py`, extraction scripts) for better IDE support.
- **Pre-commit Hooks**
  - `.pre-commit-config.yaml` installs hooks for Black, Flake8, MyPy, and detecting large files.
  - Ensures consistent codebase before pushes; prevents common Python pitfalls.
- **Testing & Coverage**
  - `pytest` as test runner; tests organized by module under `backend/` and `scripts/`.
  - Coverage reports generated via `pytest-cov`, output in `htmlcov/` directory.
  - Coverage threshold set to 85% in `tox.ini`.
- **Dependency Management**
  - Python dependencies pinned in `requirements.txt` and `backend/requirements.txt`.
  - Frontend packages managed via `package.json` with exact versions.
  - Virtual environments recommended via `python -m venv .venv`.
- **Version Control & Branch Strategy**
  - Gitflow-inspired workflow: `main`, `develop`, feature branches prefixed `feature/`.
  - Conventional commits for automatic changelog generation.

### 12. Security & Compliance
- **Secrets Management**
  - Environment variables stored in `.env`, loaded via `python-dotenv` in `main.py`.
  - `.env.example` documents required keys `GROQ_API_KEY`, `DATABASE_URL`.
- **Input Validation & Sanitization**
  - FastAPI Pydantic models enforce field types and lengths on `/analyze` payloads.
  - File size limits configured via `UploadFile` dependencies.
- **Dependency Vulnerability Scanning**
  - `safety` and `pip-audit` integrated in CI pipeline to catch insecure packages.
- **CORS & Network Security**
  - CORS middleware restricted in production to specific origins (set via `ALLOW_ORIGINS` env var).
  - Recommendations to terminate SSL at proxy/load balancer and use HTTPS in client-server communication.

### 13. Future Improvements & Roadmap
- **Containerization & Deployment**
  - Dockerfiles for backend and frontend for consistent environments.
  - Kubernetes manifests or Docker Compose for local development.
- **Enhanced Indexing & Retrieval**
  - Evaluate HNSW and PQ indexes in FAISS for faster large-scale retrieval.
  - Implement approximate nearest neighbor with `faiss.IndexHNSWFlat`.
- **Advanced OCR & ML Models**
  - Replace Tesseract with fine-tuned Vision API or custom transformer-based OCR.
  - Integrate document layout analysis with LayoutLM.
- **Plugin Architecture**
  - Modularize pipelines: allow adding new extraction modules via entry points.
  - Use `pluggy` for dynamic discovery of analysis plugins.
- **Monitoring & Logging**
  - Integrate Sentry for error tracking in production.
  - Centralized logging with ELK stack or Grafana Loki.
