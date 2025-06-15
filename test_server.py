"""
Simple test server to verify installation
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head>
            <title>Hedge Intelligence</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    background: #0a0a0a;
                    color: #fff;
                }
                h1 { color: #00ff41; }
                a { color: #00ff41; }
            </style>
        </head>
        <body>
            <h1>🚀 Hedge Intelligence is Running!</h1>
            <p>FastAPI server is working correctly.</p>
            <p>API Health: <a href="/api/health">/api/health</a></p>
            <p>Docs: <a href="/docs">/docs</a></p>
        </body>
    </html>
    """)

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Server is running", "time": "2025-06-14 15:35:19"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
