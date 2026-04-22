from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal
from app.schemas import BookAndLogCreate, LogResponse, BookResponse
from app import crud

app = FastAPI(title="Reading Logs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/readinglogs/", response_model=LogResponse)
def add_reading_log(data: BookAndLogCreate, db: Session = Depends(get_db)):
    new_log = crud.create_book_and_log(db, data)
    return new_log


@app.delete("/readinglogs/{log_id}")
def delete_reading_log(log_id: int, db: Session = Depends(get_db)):
    success = crud.delete_book_log(db, log_id)
    if success:
        return {f"message": "Log with id {log_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Log not found")

@app.get("/readinglogs/", response_model=list[LogResponse])
def get_all_logs(db: Session = Depends(get_db)):
    return crud.get_all_logs(db)