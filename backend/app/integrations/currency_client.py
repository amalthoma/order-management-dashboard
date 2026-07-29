import logging
import httpx
from fastapi import HTTPException, status
from app.core.settings import settings

logger = logging.getLogger(__name__)

class CurrencyClient:
    """Client for interacting with the external Currency Exchange API."""
    
    _client: httpx.AsyncClient | None = None
    
    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        """Returns a reused AsyncClient instance."""
        if cls._client is None:
            cls._client = httpx.AsyncClient(timeout=10.0)
        return cls._client
    
    async def get_latest_rates(self, base: str) -> dict:
        """
        Fetches the latest currency exchange rates for a given base currency.
        
        Args:
            base (str): The base currency code.
            
        Returns:
            dict: The JSON response containing the rates.
            
        Raises:
            HTTPException: If the external API fails (502 Bad Gateway).
        """
        url = f"{settings.CURRENCY_API_URL}/{base.upper()}"
        client = self.get_client()
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
                
        except httpx.TimeoutException as e:
            logger.error(f"Currency API timeout for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Currency exchange service timeout."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Currency API HTTP error for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Currency exchange service returned an error."
            )
        except httpx.RequestError as e:
            logger.error(f"Currency API request error for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to connect to currency exchange service."
            )
        except Exception as e:
            logger.error(f"Unexpected error calling Currency API: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="An unexpected error occurred while fetching exchange rates."
            )
