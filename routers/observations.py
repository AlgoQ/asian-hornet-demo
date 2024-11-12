from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from models import Observation
from database import engine

router = APIRouter()

@router.get("/observations", response_model=list[Observation])
def read_observations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    with Session(engine) as session:
        skip = (page - 1) * per_page
        statement = select(Observation).order_by(Observation.posted_on).offset(skip).limit(per_page)
        results = session.exec(statement)
        observations = results.all()
    return observations

@router.get("/observation/{observation_id}", response_model=Observation)
def read_observation(observation_id: int):
    with Session(engine) as session:
        observation = session.get(Observation, observation_id)
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        return observation

@router.post("/observation", response_model=int)
def post_observation(observation: Observation):
    with Session(engine) as session:
        session.add(observation)
        session.commit()
        session.refresh(observation)
        return observation.id

@router.post("/observations", response_model=list[int])
def post_observations(observations: list[Observation]):
    with Session(engine) as session:
        try:
            session.add_all(observations)
            session.commit()
            observation_ids = []
            for observation in observations:
                session.refresh(observation)
                observation_ids.append(observation.id)
                for photo in observation.photos:
                    photo.observation_id = observation.id
                    session.add(photo)
                    session.refresh(photo)
            session.commit()
            return observation_ids
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create observations: {e}")

@router.put("/observations/{observation_id}", response_model=int)
def update_observation(observation_id: int, observation: Observation):
    with Session(engine) as session:
        db_observation = session.get(Observation, observation_id)
        if not db_observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        observation_data = observation.model_dump(exclude_unset=True)
        for key, value in observation_data.items():
            setattr(db_observation, key, value)
        session.add(db_observation)
        session.commit()
        session.refresh(db_observation)
        return db_observation.id

@router.delete("/observations/{observation_id}", response_model=int)
def delete_observation(observation_id: int):
    with Session(engine) as session:
        observation = session.get(Observation, observation_id)
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        deleted_id = observation.id
        session.delete(observation)
        session.commit()
        return deleted_id
