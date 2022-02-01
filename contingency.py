
from database import getConn
import re


def get_contingency_plan(location, event):
    principle_service = []
    alt_passenger_journey = []
    station_staff_info = []
    signaller_info = []
    passenger_info = []
    location = location + " "
    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to chatbot")
    cur.execute('SELECT * FROM ContingencyPlan WHERE first_station=%s AND blockage_type=%s', [location, event])
    row = cur.fetchone()
    id = row[0]
    subplan = row[1]
    image = row[6]

    with open("./static/assets/task3/image.png", "wb") as f:
        f.write(image)

    cur.execute('SELECT * FROM servicealteration WHERE cplan_id=%s AND subplan=%s', [id, subplan])
    row = cur.fetchone()
    for i in row[3].split(","):
        i = "".join(re.sub(r"[^A-Za-z 1-9 : . , ()]+", "", i))
        principle_service.append(i)
        
    print(principle_service)

    cur.execute('SELECT * FROM altpassengerjourney WHERE cplan_id=%s AND subplan=%s', [id, subplan])
    row = cur.fetchone()
    for i in row[3].split(","):
        i = "".join(re.sub(r"[^A-Za-z 1-9 : . , ()]+", "", i))
        alt_passenger_journey.append(i)

    cur.execute('SELECT * FROM stationstaffinfo WHERE cplan_id=%s AND subplan=%s', [id, subplan])
    row = cur.fetchone()
    for i in row[3].split(","):
        i = "".join(re.sub(r"[^A-Za-z 1-9 : . , ()]+", "", i))
        station_staff_info.append(i)

    cur.execute('SELECT * FROM signallerinfo WHERE cplan_id=%s AND subplan=%s', [id, subplan])
    row = cur.fetchone()
    for i in row[3].split(","):
        i = "".join(re.sub(r"[^A-Za-z 1-9 : . , ()]+", "", i))
        signaller_info.append(i)

    cur.execute('SELECT * FROM passengerinfo WHERE cplan_id=%s AND subplan=%s', [id, subplan])
    row = cur.fetchone()
    for i in row[3].split(","):
        i = "".join(re.sub(r"[^A-Za-z 1-9 : . , ()]+", "", i))
        passenger_info.append(i)

    conn.close() 

    info = [principle_service, alt_passenger_journey, signaller_info, station_staff_info, passenger_info]

    return info