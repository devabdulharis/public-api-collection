from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.islamic import islamic_service

router = APIRouter(
    prefix="/api/islamic",
    tags=["Islamic Tools"],
    responses={404: {"description": "Not found"}},
)

@router.get("/quran")
async def get_surahs():
    """Get list of all Surahs."""
    return await islamic_service.get_all_surahs()

@router.get("/quran/{nomor}")
async def get_surah_detail(nomor: int):
    """Get specific Surah details."""
    return await islamic_service.get_surah_detail(nomor)

@router.get("/hadith")
async def get_hadith_books():
    """Get available Hadith books/editions."""
    return await islamic_service.get_hadith_books()

@router.get("/hadith/{book}")
async def get_hadith_by_book(book: str):
    """
    Get Hadiths from a specific book.
    Example book: 'eng-bukhari'
    """
    return await islamic_service.get_hadith_by_book(book)

@router.get("/imsak")
async def get_imsak(lat: float, long: float, date: Optional[str] = Query(None, description="dd-mm-yyyy")):
    """
    Get Imsak and prayer times.
    """
    return await islamic_service.get_prayer_times(lat, long, date)

@router.get("/tahlil")
async def get_tahlil():
    """Get Tahlil reading."""
    return islamic_service.get_tahlil()
