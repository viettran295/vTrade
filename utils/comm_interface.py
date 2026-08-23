from abc import ABC, abstractmethod
import aiohttp
import asyncio

from loguru import logger


class CommunicationInterface(ABC):
    @abstractmethod
    async def get(endpoint: str):
        pass


class HttpComm(CommunicationInterface):
    @staticmethod
    async def get(endpoint: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Received response from {endpoint}")
                        return data
                    else:
                        logger.warning(f"Failed to fetch data from {endpoint}")
                        return None
        except asyncio.TimeoutError:
            logger.error(f"Request to {endpoint} timed out.")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"{endpoint}: {e}")
            return None
        except Exception as e:
            logger.exception(f"{endpoint}: {e}")
            return None