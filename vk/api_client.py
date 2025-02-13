import aiohttp
import logging

class APIClient:
    def __init__(self, api_url: str, logger: logging.Logger):
        self.api_url = api_url
        self.logger = logger

    async def post(self, endpoint: str, data: dict):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.api_url}{endpoint}", json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API request failed: {response.status}, {await response.text()}")
                        return None
            except aiohttp.ClientError as e:
                self.logger.error(f"API request error: {str(e)}")
                return None

    async def get(self, endpoint: str, params: dict = None):
        self.logger.debug(f"API GET request: {self.api_url}{endpoint}, params: {params}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}{endpoint}", params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.debug(f"API response: {result}")
                        return result
                    elif response.status == 404:
                        self.logger.warning(f"Resource not found at {endpoint}")
                        return None
                    else:
                        self.logger.error(f"API request failed: {response.status}")
                        return None
            except aiohttp.ClientError as e:
                self.logger.error(f"API request error: {str(e)}")
                return None