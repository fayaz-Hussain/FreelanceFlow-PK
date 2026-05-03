# FreelanceFlow PK ⚡

An AI-powered toolkit tailored for Pakistani freelancers on Upwork and Fiverr.
Built with Streamlit, Google Gemini 2.5 Flash, and Tavily.

## Features
1. **Proposal Generator**: Write personalized, high-converting proposals.
2. **Rate Advisor**: Get competitive rate recommendations based on local and global market data.
3. **Contract Drafter**: Generate professional freelance contracts and export to `.docx`.
4. **Profile Optimizer**: Benchmark against top profiles and optimize your Upwork/Fiverr bio.

## Setup Instructions

1. Clone or download the repository.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   SQLITE_DB_PATH=./data/freelanceflow.db
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Tech Stack
- **UI**: Streamlit
- **AI**: Google Generative AI (Gemini 2.5 Flash)
- **Web Search**: Tavily API
- **Database**: SQLite3
- **Document Export**: python-docx
