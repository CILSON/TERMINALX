# TerminalX

A sleek, Bloomberg-inspired financial terminal built with Next.js (React) and Python (FastAPI).

TerminalX provides real-time market snapshots, an AI intelligence panel, economic calendars, and breaking financial news. It is designed to feel like a high-end trading workstation with a custom grid layout, retro-tech aesthetic, and keyboard-driven navigation.

---

## 📊 State of the Project

TerminalX is currently a **working prototype** intended to demonstrate modern web design applied to complex financial interfaces.

### Data Sources (Real vs. Mock Data)
The system is built to seamlessly transition between live data and mock data so that the UI always remains fully functional for demonstration purposes.

- **Market Data (Prices, Changes, Ticker)**
  - **Live:** The Python backend uses the `yfinance` library to fetch real-time and historical market data from Yahoo Finance.
  - **Mock:** If `yfinance` fails (due to rate limits or network issues), the backend automatically falls back to a simulated data generator that randomly ticks prices up and down.
  - **Where it's used:** Asset Detail, Heatmap, Market Overview, Market Snapshot, and the scrolling Quote Ticker at the top of the screen.

- **AI Analysis & Intelligence**
  - **Live:** If a `GEMINI_API_KEY` is provided in the backend `.env` file, the AI panel queries Google's Gemini LLM to generate sentiment analysis, confidence scores, and summaries of news articles.
  - **Mock:** If no API key is provided, the backend returns simulated, predefined AI insights.
  - **Where it's used:** The Right Panel (AI Intelligence) and when reading News Articles.

- **News Feed**
  - **Mock:** Currently, the news feed uses a localized mock data service generating financial headlines. 
  - **Where it's used:** The News tab (Side Nav -> NWS).

- **Economic Calendar**
  - **Mock:** The economic calendar currently relies on simulated data.
  - **Where it's used:** The Calendar tab (Side Nav -> CAL) and the Bottom Panel (Economic Calendar Mini).

---

## ✨ Features

- **Market Overview**: View real-time prices for indices, forex, commodities, and crypto in a dense tabular format.
- **AI Panel**: Displays sentiment analysis (Bullish/Bearish) and key takeaways on market events.
- **Economic Calendar**: Track upcoming high-impact economic data releases.
- **Financial News**: A scrolling ticker and news feed for the latest headlines.
- **Command Palette**: Press `Cmd/Ctrl + K` to bring up a quick navigation menu.
- **Bloomberg-style Aesthetics**: High contrast dark mode, custom monospace fonts, status bars, and a dense, data-rich interface.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- *(Optional)* Gemini API Key for live AI insights

### Installation & Running

1. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The application will be available at `http://localhost:3000`.

2. **Start the Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Optional: Add your API key for live AI analysis
   # echo "GEMINI_API_KEY=your_key_here" > .env
   
   uvicorn app.main:app --reload
   ```
   The backend API will run on `http://localhost:8000`.

---

## 🏗 Architecture
- **`frontend/app/`**: Next.js pages and global styles (`globals.css`).
- **`frontend/components/`**: Reusable React components organized by feature (market, news, layout, calendar, ai).
- **`frontend/stores/`**: Zustand stores for global state (`commandStore`, `marketStore`, `newsStore`).
- **`backend/app/routers/`**: FastAPI endpoints.
- **`backend/app/services/`**: Services handling external data fetching, mock data generation, and Gemini AI integration.

---

## 🔮 Roadmap / Coming Soon
- **Live News Integration**: Integrating a real-time financial news API (e.g., NewsAPI or AlphaVantage).
- **Live Economic Calendar**: Pulling live economic events from public data sources.
- **Settings Panel**: Allow users to customize their grid layout, color themes, and default watchlists.
- **Portfolio Tracking**: Add paper trading or connection to broker APIs for real-time portfolio tracking.
- **Expanded Hotkeys**: Full keyboard navigability mimicking legacy mainframe financial systems.
