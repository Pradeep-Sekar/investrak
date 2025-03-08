import uvicorn
from investrak.web.main import app

def main():
    """Run the InvesTrak web interface."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()