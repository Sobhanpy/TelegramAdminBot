import aiohttp

# async def get_weather(city: str):
#     API_KEY = "YOUR_OPENWEATHERMAP_KEY"
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             data = await resp.json()
#             if data.get("main"):
#                 temp = data["main"]["temp"]
#                 desc = data["weather"][0]["description"]
#                 return f"آب و هوا در {city}: {temp}°C, {desc}"
#             return "شهر پیدا نشد"
