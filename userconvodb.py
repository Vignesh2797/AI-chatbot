import psycopg2
from datetime import date, datetime


def getConn(*dblist):
    connStr = "host='localhost' \
               dbname= 'userinfo' user='postgres' password = '12345'"
    conn = psycopg2.connect(connStr)
    cur = conn.cursor()

    for x in dblist:
        print("inside database", x)

    if x["service"] == "book":
        a = x["isReturn"]
        ddate = x["departDate"]
        departdate = ddate[-2:] + ddate[2:4] + ddate[0:2]
        if a == "false":
            cur.execute('SET SEARCH_PATH TO chats')
            cur.execute(
                "insert into book values (%s, %s, %s, %s, %s, %s, %s)",
                [
                    x["name"],
                    x["service"],
                    x["fromLocation"],
                    x["toLocation"],
                    departdate,
                    x["departTime"],
                    x["isReturn"],
                ],
            )
            conn.commit()
        elif a == "true":
            rdate = x["returnDate"]
            returndate = rdate[-2:] + rdate[2:4] + rdate[0:2]
            cur.execute('SET SEARCH_PATH TO chats')
            cur.execute(
                "insert into book values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    x["name"],
                    x["service"],
                    x["fromLocation"],
                    x["toLocation"],
                    departdate,
                    x["departTime"],
                    x["isReturn"],
                    returndate,
                    x["returnTime"],
                ],
            )
            conn.commit()
    elif x["service"] == "predict":
        cur.execute('SET SEARCH_PATH TO chats')
        cur.execute(
            "insert into delay (name, service, currentstation, delay) values (%s, %s, %s, %s)",
            [
                x["name"],
                x["service"],
                x["currentStation"],
                x["expectedDelay"],
            ],
        )
        conn.commit()
    elif x["service"] == "contingency":
        cur.execute('SET SEARCH_PATH TO chats')
        cur.execute(
            "insert into contingency (confromLocation, contoLocation, eventType, contingencyTime, severity, name, service) values (%s, %s, %s, %s, %s, %s, %s)",
            [
                x["confromLocation"],
                x["contoLocation"],
                x["eventType"],
                x["contingencyTime"],
                x["severity"],
                x["name"],
                x["service"],
            ],
        )
        conn.commit()
    elif x["service"] == "disruption":
        cur.execute('SET SEARCH_PATH TO chats')
        cur.execute(
            "insert into disruption (name, service, disruptionstation) values (%s, %s, %s)",
            [x["name"], x["service"], x["disruptionStation"]],
        )
        conn.commit()
    conn.close()
