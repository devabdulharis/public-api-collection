import httpx

BMKG_AUTOGEMPA_JSON = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"


async def fetch_bmkg_autogempa(client: httpx.AsyncClient) -> dict:
    r = await client.get(BMKG_AUTOGEMPA_JSON)
    r.raise_for_status()
    return r.json()