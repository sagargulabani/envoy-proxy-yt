from fastapi import FastAPI, Response
import uvicorn
import os
import random
from prometheus_fastapi_instrumentator import Instrumentator

SERVICE_LETTER = os.getenv("SERVICE_LETTER", "A")

app = FastAPI()

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

@app.get("/pathA")
async def root():
    return {"message": f"Welcome to Service {SERVICE_LETTER}", "service": SERVICE_LETTER, "path" : "A"}

@app.get("/pathB")
async def health():
    return {"message": f"Welcome to Service {SERVICE_LETTER}", "service": SERVICE_LETTER, "path" : "B"}

@app.get("/error400")
async def error_400(response: Response):
    response.status_code = 400
    return {"error": "Bad Request", "service": SERVICE_LETTER, "status_code": 400}

@app.get("/error500")
async def error_500(response: Response):
    response.status_code = 500
    return {"error": "Internal Server Error", "service": SERVICE_LETTER, "status_code": 500}

@app.get("/flaky")
async def flaky(response: Response):
    if random.random() < 0.5:
        response.status_code = 500
        return {"error": "Internal Server Error", "service": SERVICE_LETTER, "status_code": 500, "flaky": True}
    return {"message": f"Success from Service {SERVICE_LETTER}", "service": SERVICE_LETTER, "status_code": 200, "flaky": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
