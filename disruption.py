from database import getConn
import re
import os
import shutil



def get_image(station, source, destination):
    for filename in os.listdir(source):
        f = os.path.join(source, filename)
        if f.__contains__(station):
            shutil.copy(source+'/'+station+'.png',destination)


def get_disruption_plan(station):
    other_station_list = []
    alt_transport_list = []
    station_tips_list = []
    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to chatbot")
    cur.execute("SELECT * FROM StationDisruptionPlan WHERE station_name=%s", [station])
    row = cur.fetchone()
    id = row[0]

    cur.execute("SELECT * FROM OtherStationSupport WHERE dplan_id=%s", [id])
    rows = cur.fetchall()
    for i in rows:
        for j, val in enumerate(i):
            if (j == 2):
                if(val):
                    other_station_list.append(i)

    


    cur.execute("SELECT * FROM StationTips WHERE dplan_id=%s", [id])
    rows = cur.fetchall()
    for i in rows:
        for j, val in enumerate(i):
            if (j == 2):
                if(val):
                    station_tips_list.append(i)

    


    cur.execute("SELECT * FROM AltTransportInfo WHERE dplan_id=%s", [id])
    rows = cur.fetchall()
    for i in rows:
        for j, val in enumerate(i):
            if (j == 3):
                val = "".join(re.sub(r"[^A-Za-z 1-9 . ,]+", "", val))
                if(val):
                    alt_transport_list.append(i)

    conn.close()

    source_directory = './static/assets/data/rmcentral_imgs'
    destination_directory = './static/assets/data/selected_image'
    get_image(station, source_directory, destination_directory)

    info = [other_station_list, alt_transport_list, station_tips_list, station]

    return info