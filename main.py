from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from Holder.GraphHolder import GraphHolder
from Holder.PathRquest import PathRequest
from Service.Navigation import (
    shortest_path_by_wheelchair,
    shortest_path_by_walking,
    alternative_paths_by_walking,
    alternative_paths_by_wheelchair
)
from time import time

# FastAPI app initialization
app = FastAPI()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:63342",
]
g = GraphHolder.get_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # enable for any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get-path/")
async def get_path(request: PathRequest):
    print(f"Request received: {request}")
    print(f"alpha={request.alpha}, gamma={request.gamma}, epsilon={request.epsilon}")

    try:
        start = time()  # ⏱ Start timer

        if request.isShortestPath:
            result = await process_shortest_path(request)
        else:
            result = await process_alternative_path(request)

        end = time()  # ⏱ End timer
        runtime = round(end - start, 3)
        print(f"⏱️ Path computation runtime: {runtime} seconds")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Process shortest path requests
async def process_shortest_path(request: PathRequest):
    try:
        if request.isWheelChair:
            return shortest_path_by_wheelchair(request)
        else:
            return shortest_path_by_walking(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Updated: Pass alpha, gamma, epsilon explicitly to use user input
async def process_alternative_path(request: PathRequest):
    try:
        if request.isWheelChair:
            return alternative_paths_by_wheelchair(
                request,
                alpha=request.alpha,
                gamma=request.gamma,
                epsilon=request.epsilon
            )
        else:
            return alternative_paths_by_walking(
                request,
                alpha=request.alpha,
                gamma=request.gamma,
                epsilon=request.epsilon
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
