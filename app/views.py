from django.shortcuts import render
import requests

import geocoder
from datetime import datetime, timedelta
from decouple import config

# Create your views here.
def home(request):

    try:
        key=(config('API_KEY'))
        query = request.GET.get('q') #Declaramos la variable query la cual es quien va contener el valor ingresado por el usuario en el campo de búsqueda del formulario (barra de busqueda).
        g = geocoder.ip('me') #Usamos geocoder.ip('me') para acceder a nuestra ubicacion en base a nuestra direccion IP
        ubicacion_actual = g.address
        url = f'https://api.openweathermap.org/data/2.5/weather?q={query}&appid={key}&units=metric'
        res = requests.get(url)
        #Lo necesario para acceder a los modulos json y obtener caracteristicas del clima buscado
        data = res.json()

        #Si al iniciar por primera vez no hay un valor introducido
        if query == None:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={ubicacion_actual}&appid={key}&units=metric'
            res = requests.get(url)
            data = res.json() 
        else:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={query}&appid={key}&units=metric'
            
        #creando un historial reciente de busquedas
        search_history = request.session.get('search_history', [])

        # Añadir la consulta actual al historial, si no está vacía y no está en el historial
        if query and query not in search_history:
            search_history.append(query)
            request.session['search_history'] = search_history

        # Elimina el elemento más antiguo del historial si su longitud es mayor que 4
        if len(search_history) > 4:
            search_history.pop(0)
            request.session['search_history'] = search_history

        #si el lugar a buscar no existe
        try:
            temp = data['main']['temp']
        except KeyError:
            return render(request,'proyectoclimaApp/not_found.html')
        
        #Accedemos a los demas modulos json para mostrar en la plantilla

        fells_like = data['main']['feels_like']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        wind_speed = data['wind']['speed']
        latitude = data['coord']['lat']
        longitude = data['coord']['lon']
        base = data['weather'][0]['main']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        clouds = data['clouds']['all']
        wind_direction = data['wind']['deg']
        pressure = data['main']['pressure']

        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']

        #Convertimos la marca de tiempo en objetos de fecha y hora

        dt_sunrise = datetime.fromtimestamp(sunrise)
        dt_sunset = datetime.fromtimestamp(sunset)

        # Formateamos las horas en formato legible
         
        timesunrise = dt_sunrise.strftime("%H:%M")
        timesunset = dt_sunset.strftime("%H:%M")

        try:
            rain = data['rain']['1h']
        except KeyError:
            rain = '0'

        #Icono de clima dependiendo de la condicion atmosferica
        icon = data['weather'][0]['icon']
        icon_url = f'http://openweathermap.org/img/w/{icon}.png'    

        #Forma en que varia las horas dependiendo del lugar buscado
        timezone = data['timezone']
        now_utc = datetime.utcnow()
        now_local = now_utc + timedelta(seconds=timezone)
        time_format = "%H:%M --- %d/%m/%Y"
        local_time_string = now_local.strftime(time_format)

        #Cambio de fondo dependiendo la hora
        now_utc = datetime.utcnow()
        now_local = now_utc + timedelta(seconds=timezone)
        hour_local = now_local.hour
        is_night = hour_local
 
        is_night = 19 <= now_local.hour or now_local.hour <= 5
        is_afternoon = 17 <= now_local.hour < 19
        is_day = 6 <= now_local.hour < 17
    
        return render(request,'proyectoclimaApp/home.html',{'data':data,'query':query,'temp':temp, 'feels_like':fells_like ,'temp_min':
                                                            temp_min,'temp_max':temp_max,'wind_speed':wind_speed,'latitude':latitude,
                                                            'longitude':longitude,'description':description,'current_time': local_time_string,
                                                            'humidity':humidity, 'rain':rain, 'clouds':clouds ,'base':base,
                                                            'icon_url':icon_url,'is_night':is_night, 'is_afternoon':is_afternoon, 'is_day':is_day 
                                                            ,'searched':search_history, 'sunrise':timesunrise, 'sunset':timesunset, 'ubicacion_actual':ubicacion_actual,
                                                            'wind_direction':wind_direction,'pressure':pressure})
    #Lo que arroja cuando no hay conexion a internet
    except requests.exceptions.RequestException as e:
        error_message = str(e) 
        return render(request,'proyectoclimaApp/error.html',{'error_message': error_message})

def handler404(request):
    return render(request, 'proyectoclimaApp/404.html', status=404)