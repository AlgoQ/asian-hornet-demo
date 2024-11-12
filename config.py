from fastapi.middleware.cors import CORSMiddleware

BASE_URL = "http://localhost:8000"

# TODO: update CORS to allow only the frontend
def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
