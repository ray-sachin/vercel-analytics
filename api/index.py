from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['POST'],
    allow_headers=['*'],
)

# Load the data once at startup
with open(os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json'), 'r') as f:
    entries = json.load(f)

@app.post("/")
async def analytics(request: Request):
    data = await request.json()
    regions = data['regions']
    threshold = data['threshold_ms']
    result = {}
    for region in regions:
        region_data = [item for item in entries if item['region'] == region]
        if region_data:
            latencies = [item['latency_ms'] for item in region_data]
            uptimes = [item['uptime_pct'] for item in region_data]
            breaches = sum(1 for item in region_data if item['latency_ms'] > threshold)
            result[region] = {
                'avg_latency': float(np.mean(latencies)),
                'p95_latency': float(np.percentile(latencies, 95)),
                'avg_uptime': float(np.mean(uptimes)),
                'breaches': breaches
            }

    return result
