import httpx
from fastapi import HTTPException
from typing import List, Dict, Any, Optional

class IslamicService:
    def __init__(self):
        self.quran_base_url = "https://equran.id/api/v2"
        self.hadith_base_url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"
        self.imsak_base_url = "https://api.aladhan.com/v1"
        
        # Static Tahlil Data (simplified for brevity)
        self.tahlil_data = [
            {"id": 1, "title": "Pengantar Al-Fatihah", "arabic": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "translation": "Dengan menyebut nama Allah Yang Maha Pengasih lagi Maha Penyayang."},
            {"id": 2, "title": "Surat Al-Ikhlas", "arabic": "قُلْ هُوَ ٱللَّهُ أَحَدٌ", "translation": "Katakanlah: Dialah Allah, Yang Maha Esa."},
            {"id": 3, "title": "Surat Al-Falaq", "arabic": "قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ", "translation": "Katakanlah: Aku berlindung kepada Tuhan Yang Menguasai subuh."},
            {"id": 4, "title": "Surat An-Nas", "arabic": "قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ", "translation": "Katakanlah: Aku berlindung kepada Tuhan (yang memelihara dan menguasai) manusia."},
            # Add more tahlil readings as needed
        ]

    async def get_all_surahs(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.quran_base_url}/surat")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Surahs")
            return resp.json()

    async def get_surah_detail(self, nomor: int):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.quran_base_url}/surat/{nomor}")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Surah detail")
            return resp.json()

    async def get_hadith_books(self):
        # Using a reliable endpoint or static list. Using fawazahmed0/hadith-api typically requires knowing the book structure or checking their editions.json
        # For simplicity, we can fetch editions and filter or return a static known list if the API is complex.
        # Let's try fetching editions.json from the CDN
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.hadith_base_url}/editions.json")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Hadith books")
            
            # Filter for some major collections to return a clean list
            raw_data = resp.json()
            # This API returns a huge list. Let's return a subset or manageable structure if possible.
            # Or just return raw data if user wants exploring.
            # Better approach: Return major books
            return raw_data

    async def get_hadith_by_book(self, book: str, limit: int = 50, page: int = 1):
        # NOTE: This CDN API splits by numbered JSON files (e.g. bukhari/1.json).
        # Implementing full pagination is tricky without index.
        # We will attempt to fetch the first chunk/section.
        
        # A safer pattern with this specific API is usually /editions/{edition_name}.json or subsections.
        # For this task, strict implementation might be complex. Let's try a direct simple fetch if possible,
        # or warn the user this is a basic implementation.
        
        # Let's interpret 'book' as the edition name (e.g., 'eng-bukhari').
        async with httpx.AsyncClient() as client:
            # Try fetching the whole book index if available, or the first section
            # The structure is often: /editions/{edition}/sections.json or similar.
            # Let's return the sections first.
            resp = await client.get(f"{self.hadith_base_url}/editions/{book}/sections.json")
            if resp.status_code == 200:
                return resp.json()
            
            # If not found, maybe they wanted specific hadiths.
            # Fallback handling can be improved later.
            raise HTTPException(status_code=404, detail="Book/Edition not found or API structure mismatch")

    async def get_prayer_times(self, lat: float, long: float, date: Optional[str] = None):
        # Date format DD-MM-YYYY. If None, use current timestamp/today by default
        import datetime
        if not date:
            date = datetime.date.today().strftime("%d-%m-%Y")
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.imsak_base_url}/timings/{date}",
                params={"latitude": lat, "longitude": long, "method": 3} # Method 3: Muslim World League
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch prayer times")
            return resp.json()

    def get_tahlil(self):
        return {"data": self.tahlil_data}

islamic_service = IslamicService()
