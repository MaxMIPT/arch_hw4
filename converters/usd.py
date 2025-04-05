from typing import Optional

from .base import CurrencyConverter

from services import ExchangeService


class UsdConverter(CurrencyConverter):
    def __init__(
        self,
        currency: str,
        service: ExchangeService
    ):
        self.currency = currency
        self.service = service

    def convert(self, amount: float) -> Optional[float]:
        rates = self.service.get_rates()
        if self.currency not in rates.keys():
            return None

        return amount * rates[self.currency]
