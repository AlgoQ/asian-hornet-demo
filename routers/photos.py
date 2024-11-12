from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from models import Photo
from database import engine


router = APIRouter()

@router.post("/photo", response_model=Photo)
def post_photo(photo: Photo):
    with Session(engine) as session:
        session.add(photo)
        session.commit()
        session.refresh(photo)
        return photo
    
@router.post("/photos", response_model=list[Photo])
def post_photos(photos: list[Photo]):
    with Session(engine) as session:
        for photo in photos:
            if not photo.observation_id:
                raise HTTPException(status_code=400, detail="Photo must have an observation_id")
        session.add_all(photos)
        session.commit()
        for photo in photos:
            session.refresh(photo)
        return photos

@router.put("/photo/{photo_id}", response_model=Photo)
def update_photo(photo_id: int, photo: Photo):
    with Session(engine) as session:
        db_photo = session.get(Photo, photo_id)
        if not db_photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        photo_data = photo.model_dump(exclude_unset=True)
        for key, value in photo_data.items():
            setattr(db_photo, key, value)
        session.add(db_photo)
        session.commit()
        session.refresh(db_photo)
        return db_photo

@router.delete("/photo/{photo_id}", response_model=Photo)
def delete_photo(photo_id: int):
    with Session(engine) as session:
        photo = session.get(Photo, photo_id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        session.delete(photo)
        session.commit()
        return photo
