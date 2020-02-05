
from datetime import datetime

def generate_datetime(date, hour):
    #Generate a datetime from a date and a time
    date = datetime.strptime(date, "%Y-%m-%d")
    hour = datetime.strptime(hour, '%H:%M')

    #Combine the date and the hour
    datetime_tempo = datetime.combine(date, hour.time())

    #Return a string format of the datetime
    return str(datetime_tempo)
