# AegisAI — Backup Run Plan (No Docker)

If Docker or Kafka fail during the live environment, you can run the platform in a completely offline/fallback mode using native Python and Node processes. The system is designed to gracefully fall back to generating **1,000 realistic dummy rows** if Kafka streams or dataset files are unavailable.

## Step 1: Start the FastAPI Backend
Open your first terminal and run:
```bash
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*Note: You will see warning logs that Kafka failed to connect, but the backend will gracefully suppress them and continue serving REST endpoints and WebSockets via the mock data generator fallback.*

## Step 2: Start the React Frontend
Open your second terminal and run:
```bash
cd frontend
npm install
npm run dev
```

## Step 3: Open the Dashboard
Navigate to `http://localhost:5173`. 
The frontend will connect directly to `ws://localhost:8000/ws/logs`. Since Kafka is down, the fallback logic inside `backend/services/ml_pipeline.py` ensures localized network logs loop into the feed seamlessly. Llama/Grok API connections will continue to function flawlessly as they are abstracted REST calls.
