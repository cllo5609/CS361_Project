# Clinton Lohr
# CS 361-400: Software Engineering I
# Weather Data Microservice
"""
This microservice is used to gather weather data by calling a weather API. Requests are made in the form of a text
file and returned to a user using another text file. Input for this program is in the form of a string and must be
as follows: "city name (required), state abbreviation, country code, units of measurement". The returned weather data
is filtered to only include necessary information before being returned to the user in the form of a string.
"""

import requests

# read key from text file and store as a variable
file = open("weather_api_key.txt", "r")
api_key = file.readline()


def extract_request_contents():
    """
    Extracts and stores contents of .txt file
    """

    file = open("weather_request.txt", "r")
    location = file.readline()
    open("weather_request.txt", "w").close()       # erases contents of .txt file

    return location


def call_api(location):
    """
    Formats input and makes a GET request to the weather API
    """

    url = "https://api.openweathermap.org/data/2.5/weather?q=" + str(location) + ",CO,US&appid=" + str(api_key) + \
          "&units=Imperial"

    api_response = requests.get(url)
    list_response_data = api_response.json()  # store response data as a variable

    return list_response_data


def extract_weather_data(list_data):
    """
    Creates a list containing only relevant weather data
    """

    data = [
        str(list_data['name']),                 # city name
        str(list_data['sys']['country']),       # country
        str(list_data['main']['temp']),         # temperature
        str(list_data['weather'][0]['main']),   # weather conditions
        str(list_data['main']['humidity'])      # humidity
    ]

    return data


def write_weather_data(weather_data):
    """
    Writes each element in the data list to the .txt file
    """

    file = open("weather_response.txt", "w")
    for ele in weather_data:
        file.write(ele)
        file.write(",")
    file.close()

    return


while True:                                         # runs continuously waiting for reqeust
    file = open("weather_request.txt", "r")
    check_request = file.readline()
    if check_request:                               # runs if request found in .txt request file
        location = extract_request_contents()
        api_response = call_api(location)
        if api_response['cod'] != 200:              # checks if request was valid
            print('Error: Invalid Search Request')
        else:
            weather_data = extract_weather_data(api_response)
            write_weather_data(weather_data)


