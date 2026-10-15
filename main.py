import time, uuid
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "25ds3000071@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-7c24a8.example.com"

app = FastAPI()

# CORS added first (inner layer): only the one assigned origin, never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    allow_credentials=False,
)

# Added last = outermost, so it stamps EVERY response (incl. preflights and errors).
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    rid = str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception:
        response = Response("Internal Server Error", status_code=500)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response

@app.options("/stats")
async def stats_options():
    return Response(status_code=200)

@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    s = sum(nums)
    return {"email": EMAIL, "count": len(nums), "sum": s,
            "min": min(nums), "max": max(nums), "mean": s / len(nums)}

@app.get("/")
async def root():
    return {"ok": True}
