# Lit-Miner Streamlit UI

This directory contains the Streamlit-based user interface for Lit-Miner.

## Structure

```
streamlit_app/
├── Home.py                    # Landing page
├── pages/
│   ├── 1_🔍_Search.py         # Literature search
│   ├── 2_✍️_Write.py          # AI review generation
│   └── 3_📖_Read.py           # Full-text reading
└── utils/
    ├── backend.py             # Backend integration
    └── ui_components.py       # Reusable UI components
```

## Running the App

1. **Install dependencies** (from project root):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (create `.env` in project root):
   ```env
   DEEPSEEK_API_KEY=your_api_key_here
   ```

3. **Run Streamlit**:
   ```bash
   cd streamlit_app
   streamlit run Home.py
   ```

4. **Open browser**: The app will open at `http://localhost:8501`

## Features

### 🔍 Search
- Smart query expansion (Chinese → English, synonyms)
- Rubric-based scoring (journal impact, recency, data quality)
- Automatic categorization and ChromaDB storage
- Real-time logging and progress tracking

### ✍️ Write
- AI-powered literature review generation
- Auto-topic generation from papers
- RAG-enhanced synthesis using DeepSeek
- Markdown export

### 📖 Read
- PDF fetching from Pismin/SciHub
- Smart DOI repair via CrossRef
- Markdown conversion
- Figure extraction with captions

## Configuration

Settings are available in the sidebar:
- **PubMed Email**: Required for PubMed API access
- **DeepSeek API Key**: Can be set in `.env` or entered in sidebar

## Notes

- The UI directly calls backend Python modules (no FastAPI server needed)
- Session state is used for cross-page data sharing
- All data is stored in `data/` directory at project root
