from abc import ABC, abstractmethod
import aiohttp

from loguru import logger

class CommunicationInterface(ABC):
    @abstractmethod
    async def get(endpoint: str):
        pass

class HttpComm(CommunicationInterface):
    @staticmethod
    async def get(endpoint: str):
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