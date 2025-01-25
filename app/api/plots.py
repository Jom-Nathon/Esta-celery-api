from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from app.db.database import get_session, create_db_and_tables
from app.models.plot import Plot, PlotRead, PlotCreate
from app.celery_worker import getPlotInfo

from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select, delete

router = APIRouter()

session = next(get_session())

@router.post("/delete/{province}")
def deletePlot(province: str):
    try:
        statement = select(Plot).where(Plot.province == province)
        plots = session.exec(statement).all()
        
        delete_statement = delete(Plot).where(Plot.province == province)
        session.exec(delete_statement)
        session.commit()

        return {
            "message": f"Successfully deleted {len(plots)} plots from {province}",
            "count": len(plots)
        }
        
    except Exception as e:
        print(e)

@router.post("/scrape/{province}")
async def scrape(province: str):
    """Start scraping plots for a given area"""
    try:
        task = getPlotInfo(province)
        return {
            "message": "Scraping Done!",
            "area": province
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"{str(e)}"
        )

@router.get("/all_plots/")
def read_plots(
    offset: int = 0,
    limit: int = 100,
) -> list[Plot]:
    allPlot = session.exec(select(Plot).offset(offset).limit(limit)).all()
    return allPlot

@router.get("/plots/{plot_id}")
def read_plot(plot_id: int):
    plot = session.add(Plot).filter(Plot.id == plot_id).first()
    if plot is None:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot