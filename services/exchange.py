import json
import logging
import os
import requests
import time

from typing import Optional


class ExchangeService:

    def __init__(
        self,
        api_url: str = "https://api.exchangerate-api.com/v4/latest/USD",
        cache_file: str = "services/_static/exchange_rates.json",
        cache_expiry: int = 3600,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        self.api_url = api_url
        self.cache_file = cache_file
        self.cache_expiry = cache_expiry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def _load_from_cache(self) -> Optional[dict]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_expiry:
                        return data['rates']

            except (json.JSONDecodeError, KeyError):
                self.logger.error("Invalid cache file. Fetching from API.")
                return None

        return None

    def _save_to_cache(self, rates: dict) -> None:
        try:
            data = {'timestamp': time.time(), 'rates': rates}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)

        except IOError as e:
            self.logger.error(f"Error saving to cache: {e}")

    def get_rates(self) -> Optional[dict]:
        rates = self._load_from_cache()
        if rates:
            return rates

        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.api_url, timeout=5)
                response.raise_for_status()
                data = response.json()
                rates = data['rates']
                self._save_to_cache(rates)
                return rates

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error("Max retries reached.  Unable to fetch rates.")
                    return None

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Error processing JSON response: {e}")
                return None

        return None
