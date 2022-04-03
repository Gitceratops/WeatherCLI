import argparse
import json
import os
import sys

from configparser import ConfigParser
from typing import Dict, Final, Iterable, List, Tuple
from urllib import error, parse, request

import weather_app.style as style


BASE_WEATHER_API_URL: Final[str] = 'http://api.openweathermap.org/data/2.5/weather'

# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM: Final[Iterable[int]] = range(200, 300)
DRIZZLE: Final[Iterable[int]] = range(300, 400)
RAIN: Final[Iterable[int]] = range(500, 600)
SNOW: Final[Iterable[int]] = range(600, 700)
ATMOSPHERE: Final[Iterable[int]] = range(700, 800)
CLEAR: Final[Iterable[int]] = range(800, 801)
CLOUDY: Final[Iterable[int]] = range(801, 900)


def _get_api_key(filename: str = 'secrets.ini') -> str:
  """
  Fetch the API key from the configuration file.

  Expects a configuration file named 'secrets.ini' by default with structure:

    [openweather]
    api_key = <YOUR_OPENWEATHER_API_KEY>

  Arguments:
    filename (str, optional): The configuration file's name to read the API key from

  Returns:
    str: The OpenWeather API key to get
  
  """

  config = ConfigParser()
  config.read(os.path.join('weather_app', filename))

  return config['openweather']['api_key']


def read_user_cli_args() -> argparse.Namespace:
  """
  Handles the CLI user interactions.

  Returns:
    argparse.Namespace: The populated namespace object to get
  """

  parser = argparse.ArgumentParser(
    description = 'Gets weather and temperature information for a city'
  )
  parser.add_argument(
    'city', 
    nargs = '+', 
    type = str, 
    help = 'enter the city name'
  )
  parser.add_argument(
    '-i',
    '--imperial',
    action = 'store_true',
    help = 'display the temperature in imperial units'
  )

  return parser.parse_args()


def build_weather_query(city_input: List[str], imperial: bool = False) -> str:
  """
  Builds the URL for an API request top OpenWeather's weather API.

  Arguments:
    city_input (List[str]): The name of a city as collected by 'argparse'
    imperial (bool, optional): A flag indicating whether or not to use imperial units for 
      temperature

  Returns:
    str: The URL to get, formatted for a call to OpenWeather's city name endpoint
  """

  api_key: str = _get_api_key()

  city_name: str = ' '.join(city_input)
  units: str = 'imperial' if imperial else 'metric'

  url_encoded_city_name: str = parse.quote_plus(city_name)

  url: str = (
    f'{BASE_WEATHER_API_URL}?q={url_encoded_city_name}'
    f'&units={units}&appid={api_key}'
  )

  return url


def get_weather_data(query_url: str) -> Dict:
  """
  Maes an API request to an URL and returns the data as a Python object.

  Arguments:
    query_url (str): The URL formatted for OpenWeather's city name endpoint

  Returns:
    Dict: The weather information to get for a specific city
  """

  try:
    response = request.urlopen(query_url)
  
  except error.HTTPError as http_error:

    if http_error.code == 401: # 401 - Unauthorized
      sys.exit('Exit: Access denied. Check your API key.')

    elif http_error == 404: # 404 - Not Found
      sys.exit('Exit: Can\'t find weather data for the provided city name.')

    else:
      sys.exit(f'Exit: Something went wrong ... ({http_error.code})')

  data = response.read()

  try:    
    return json.loads(data)

  except json.JSONDecodeError:
    sys.exit('Exit: Couldn\'t read the server response.')


def _select_weather_display_params(weather_id: str) -> Tuple[str]:
  """
  """

  if weather_id in THUNDERSTORM:
    display_params = ("💥", style.RED)

  elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)

  elif weather_id in RAIN:
    display_params = ("💦", style.BLUE)

  elif weather_id in SNOW:
    display_params = ("⛄️", style.WHITE)

  elif weather_id in ATMOSPHERE:
    display_params = ("🌀", style.BLUE)

  elif weather_id in CLEAR:
    display_params = ("🔆", style.YELLOW)

  elif weather_id in CLOUDY:
    display_params = ("💨", style.WHITE)

  else:  # In case the API adds new weather codes
    display_params = ("🌈", style.RESET)

  return display_params


def display_weather_info(weather_data: Dict, imperial: bool = False) -> None:
  """
  Prints formatted weather information about a city.

  Arguments:
    weather_data (Dict): The API response from OpenWeather by city name
    imperial (bool, optional): A flag indicating whether or not to use imperial units for 
      temperature

  More informatio at https://openweathermap.org/current#name
  """

  city: str = weather_data.get('name')
  weather_id = weather_data.get('weather')[0].get('id')
  weather_description: str = weather_data.get('weather')[0].get('description')
  temperature: str = weather_data.get('main').get('temp')

  style.change_color(style.REVERSE)
  print (f"{city:^{style.STRING_PADDING}}", end = "")
  style.change_color(style.RESET)

  symbol, color = _select_weather_display_params(weather_id)

  style.change_color(color)
  print (f"\t{symbol}", end = "")
  print (f"\t{weather_description.capitalize():^{style.STRING_PADDING}}", end = " ")
  style.change_color(style.RESET)
  
  print (f"({temperature}°{'F' if imperial else 'C'})")
  