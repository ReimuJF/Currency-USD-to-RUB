from django.shortcuts import render
from django.http import JsonResponse
import asyncio
import aiohttp
import datetime

rates = []


class LastRate:
    date = None

    @staticmethod
    def update():
        LastRate.date = datetime.datetime.now()


async def update_exchange_rate():
    if LastRate.date and (datetime.datetime.now() - LastRate.date).seconds < 10:
        return
    async with aiohttp.ClientSession() as session:
        LastRate.update()
        async with session.get('https://api.exchangerate-api.com/v4/latest/USD') as response:
            data = await response.json()
            rate = data['rates']['RUB']
            rates.append(rate)
            if len(rates) > 10:
                rates.pop(0)


async def get_current_usd(request):
    await asyncio.create_task(update_exchange_rate())
    while not rates:
        await asyncio.sleep(0.5)
    latest_rate = rates[-1]
    return JsonResponse({ 'USD_to_RUB': latest_rate,
                          'last_update': LastRate.date.strftime('%H:%M:%S'),
                          'last_10_rates': rates })
