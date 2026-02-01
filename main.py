import os
import sys
import uvicorn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Get port from environment variable (for cloud deployment) or use default
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("Starting Unicode to KrutiDev Converter (Web Mode)...")
    print(f"Server running on http://{host}:{port}")
    
    try:
        uvicorn.run(
            "ui.web_app:app", 
            host=host, 
            port=port, 
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()