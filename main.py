from converters import UsdConverter
from services import ExchangeService


currencies = [
    "RUB", "EUR",
    "GBP", "CNY"
]

def main():    
    amount = int(input('Введите значение в USD: \n'))
    service = ExchangeService(
        api_url="https://api.exchangerate-api.com/v4/latest/USD"
    )
    for curr in currencies:
        converter = UsdConverter(currency=curr, service=service)
        print(f"{amount} USD to {curr}: {converter.convert(amount=amount)}")

if __name__ == "__main__":
    main()
