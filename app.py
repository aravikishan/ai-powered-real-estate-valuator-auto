from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import os

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
DATABASE_URL = "sqlite:///./realestate.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
def create_database():
    Base.metadata.create_all(bind=engine)

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    features = Column(JSON)
    price = Column(Float)
    valuation = Column(Float)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Pydantic models
class PropertyCreate(BaseModel):
    location: str
    features: dict
    price: float

class PropertyUpdate(BaseModel):
    location: str
    features: dict
    price: float

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed data
@app.on_event("startup")
async def startup_event():
    create_database()
    db = SessionLocal()
    if not db.query(Property).first():
        seed_properties = [
            Property(location="123 Main St", features={"bedrooms": 3, "bathrooms": 2}, price=250000, valuation=260000),
            Property(location="456 Elm St", features={"bedrooms": 4, "bathrooms": 3}, price=350000, valuation=360000)
        ]
        db.add_all(seed_properties)
        db.commit()
    db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html") as f:
        return f.read()

@app.get("/valuation", response_class=HTMLResponse)
async def valuation_page():
    with open("templates/valuation.html") as f:
        return f.read()

@app.get("/properties", response_class=HTMLResponse)
async def properties_page():
    with open("templates/properties.html") as f:
        return f.read()

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    with open("templates/about.html") as f:
        return f.read()

@app.get("/contact", response_class=HTMLResponse)
async def contact_page():
    with open("templates/contact.html") as f:
        return f.read()

@app.get("/api/properties")
async def get_properties(db: Session = Depends(get_db)):
    properties = db.query(Property).all()
    return properties

@app.post("/api/properties")
async def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    new_property = Property(
        location=property.location,
        features=property.features,
        price=property.price,
        valuation=property.price * 1.05  # Mock valuation logic
    )
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property

@app.get("/api/properties/{id}")
async def get_property(id: int, db: Session = Depends(get_db)):
    property = db.query(Property).filter(Property.id == id).first()
    if property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@app.put("/api/properties/{id}")
async def update_property(id: int, property: PropertyUpdate, db: Session = Depends(get_db)):
    db_property = db.query(Property).filter(Property.id == id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    db_property.location = property.location
    db_property.features = property.features
    db_property.price = property.price
    db_property.valuation = property.price * 1.05  # Mock valuation logic
    db.commit()
    db.refresh(db_property)
    return db_property

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
