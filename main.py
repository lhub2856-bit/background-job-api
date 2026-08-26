import asyncio
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import inngest
import inngest.fast_api

# Initialize FastAPI app
app = FastAPI()

# In-memory database to store report statuses
reports_db = {}

# Initialize Inngest client for local dev
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False
)

class ReportRequest(BaseModel):
    topic: str

# 1. Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 2. POST /reports endpoint (Returns 202 instantly & triggers background job)
@app.post("/reports", status_code=202)
async def create_report(req: ReportRequest):
    report_id = str(int(time.time() * 1000))
    reports_db[report_id] = {"id": report_id, "topic": req.topic, "status": "pending"}

    # Send event to Inngest background worker
    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": req.topic}
        )
    )

    return {"id": report_id, "status": "pending"}

# 3. GET /reports/{report_id} status check endpoint
@app.get("/reports/{report_id}")
def get_report(report_id: str):
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports_db[report_id]

# 4. Inngest Background Function with Error Handling & Retries
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=3,  # Agar fail ho jaye toh maximum 3 baar dobara koshish karega
)
async def make_report(ctx: inngest.Context, step: inngest.Step):
    data = ctx.event.data
    report_id = data["id"]
    topic = data["topic"]

    try:
        # Step 1: Slow work simulation (8 seconds sleep)
        @step.run("do-the-slow-work")
        async def slow_work():
            await asyncio.sleep(8)
            return True

        await slow_work()

        # Step 2: Build report and update memory store as 'done'
        @step.run("build-report")
        def build_report():
            reports_db[report_id] = {
                "id": report_id,
                "topic": topic,
                "status": "done",
                "result": f"Report for '{topic}' generated successfully!"
            }

        build_report()

    except Exception as e:
        # Step 3: Agar koi error aaye toh status ko 'failed' mark kar dein
        @step.run("mark-failed")
        def mark_failed():
            reports_db[report_id] = {
                "id": report_id,
                "topic": topic,
                "status": "failed",
                "error": str(e)
            }
        mark_failed()
        raise e  # Inngest ko notify karne ke liye ke retry trigger kare

# Serve Inngest endpoints via FastAPI
inngest.fast_api.serve(app, inngest_client, [make_report])