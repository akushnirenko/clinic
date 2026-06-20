from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth  #, patients, appointments

app = FastAPI(title="Family Clinic API v1")

# Enable CORS so your VueJS frontend can make requests from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain/port in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core functional routers
app.include_router(auth.router)
#app.include_router(patients.router)
#app.include_router(appointments.router)

@app.get("/")
def root():
    return {"status": "healthy", "service": "clinic-api"}
