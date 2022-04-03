from weather_app.weather import *


if __name__ == '__main__':
  
  user_args = read_user_cli_args()
  query_url: str = build_weather_query(user_args.city, user_args.imperial)
  
  weather_data = get_weather_data(query_url)
  
  display_weather_info(weather_data, user_args.imperial)
  