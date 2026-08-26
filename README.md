# background-job-api
backened Ai engineering assignment
# my First Background Job (FastAPI + Inngest)

An asynchronous backend task processing system built with Python (FastAPI) and Inngest to handle slow operations smoothly.

---

## 🚀 How to Run It

1. **Start the FastAPI Server:**
   ```bash
   uvicorn main:app --reload --port 8000
   Start the Inngest Dev Server:

Bash
npx inngest-cli@latest dev --url http://localhost:8000/api/inngest
 Endpoints & Inngest FunctionsTypePath / NameMethodDescriptionEndpoint/healthGETServer health check.  Endpoint/reportsPOSTAccepts topic, returns 202 Accepted instantly, and triggers an event.  Endpoint/reports/{id}GETPolls report status (pending, done, or failed).  Functionmake-reportInngest EventBackground worker simulating an 8-second task with retries.  FunctionheartbeatInngest CronScheduled task running every minute.  
 Stage 3 (Validation vs Retries): Bad input (missing topic) is rejected immediately at the door with a 400 Bad Request because retrying invalid data will never fix it. Temporary system glitches deserve automatic retries since they can succeed on subsequent attempts.  Stage 4 (Cron Expressions):Every day at 08:00: 0 8 * * *  Every Sunday at 22:00: 0 22 * * 0[cite: 1]
