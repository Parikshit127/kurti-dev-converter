import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(
        "ui.web_app:app", 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=120,  # Keep connections alive for 2 minutes
        limit_max_requests=100,  # Restart worker after 100 requests to prevent memory leaks
    )
