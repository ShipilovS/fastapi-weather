from fastapi import FastAPI, Request, Form
from typing import List
import requests
from fastapi.templating import Jinja2Templates # пакет для шаблонов
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import datetime
from dotenv import load_dotenv
import os

load_dotenv()


token = os.environ.get('TOKEN') # Your api token
app = FastAPI(title="Example")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_info(city):
    try:
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}")
        date = r.json()
        # print(date)
        # print(date['main']['temp'] - 273)
        current_time = datetime.datetime.now()+datetime.timedelta(hours=3)
        context = {
            'exception' : True,
            'city' : city,
            'temp' : int(date['main']['temp'] - 273),
            'pressure' : int(date['main']['pressure'] / 1.333),
            'humidity' : int(date['main']['humidity']),
            'speed' : int(date['wind']['speed']),
            'icon' : date['weather'][0]['icon'],
            'date_update' : f"{current_time.hour}:{datetime.datetime.now().minute}",
        }
    except:
        context = {
            'exception' : False,
            'text' : 'Не найдено. Проверьте написание ввода',
        }
    return context

def generate_start_cities(start_cities):
    dict_start_request = [i for i in start_cities]
    d = []
    for i in range(len(start_cities)):
        d.append(get_info(start_cities[i]))
    return d

# ---

@app.post('/')
@app.get("/")
async def home(request: Request):
    start_cities = ['Лондон', 'Канада', 'Китай', 'Дубаи', 'Турция', 'Москва']
    template = 'base.html'
    d = generate_start_cities(start_cities)
    context = {
        'request': request,
        'start_request': d,
    }
    return templates.TemplateResponse(template, context)

@app.post('/info/')
async def information(cityname : str = Form(None)):
    if cityname == None or get_info(cityname)['exception'] == False or type(cityname) == int:
        return RedirectResponse("/")
    
    template = 'get_info.html'
    context = {'request': get_info(cityname)}
    return templates.TemplateResponse(template, context)