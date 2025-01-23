from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_session, create_db_and_tables
from app.models.plot import Plot
from app.celery_worker import getPlotInfo

from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

router = APIRouter()

Sessiondep = Annotated[Session, Depends(get_session)]

@router.post("/scrape/")
async def start_scraping(db: Sessiondep, plot: str):
    plot = db.add(Plot).filter(Plot.province == plot).first()
    if plot is not None:
        #delete all previous plot then scrape
        print("deleteus")
    task = getPlotInfo.delay(plot)
    return {"message": "Scraping started", "task_id": task.id}

@router.get("/all_plots/")
def read_plots(
    session: Sessiondep,
    offset: int = 0,
    limit: int = 100,
) -> list[Plot]:
    allPlot = session.exec(select(Plot).offset(offset).limit(limit)).all()
    return allPlot

@router.get("/plots/{plot_id}")
def read_plot(db: Sessiondep, plot_id: int):
    plot = db.add(Plot).filter(Plot.id == plot_id).first()
    if plot is None:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot