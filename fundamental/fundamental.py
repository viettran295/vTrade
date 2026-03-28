import aiohttp
from enum import Enum
from loguru import logger
from .financial_report import *


class Period(Enum):
    ANNUALLY = "annually"
    QUARLY = "quarly"


class FinancialStatement:
    def __init__(self):
        self.url = "http://localhost:3000"

    async def fetch_financial_statment(
        self, stock: str, period: Period = Period.ANNUALLY
    ):
        endpoint = self.url + "/" + stock + "/" + period.value
        response = await self._fetch_data(endpoint)
        if response is not None:
            return response
        else:
            return None

    async def _fetch_data(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                endpoint, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Received response from {endpoint}")
                    return data
                else:
                    logger.debug(f"Failed to fetch data from {endpoint}")
                    return None
