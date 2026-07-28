from datetime import datetime, timedelta

time = datetime.now()

def actual_hour():
    actual_hour = time.strftime('%H:%M:%S')
    s = actual_hour[:2]
    return int(s)
if __name__ == '__main__':
    times = actual_hour()
    if times >= 6 and times <= 12:
        msg = 'Bom Dia!'
    elif times >= 13:
        msg = 'Boa Tarde!'
    print(times > 12)
    print(msg)