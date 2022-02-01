from flask import Flask, render_template, redirect, url_for, json
from flask_socketio import SocketIO
import random
from datetime import datetime
from experta import *
from experta.watchers import RULES, AGENDA
from experta.fact import Fact
from experta.rule import Rule
from experta import DefFacts
from experta import NOT, MATCH, W
import dateutil.parser
from datetime import datetime
import pandas as pd


app = Flask(__name__)
socketio = SocketIO(app)


def config_data(filename):
    with app.open_resource("static/assets/configuration/" + filename + ".json") as f:
        return json.load(f)


class Knowledge(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        if "reset" in self.data:
            if self.data.get("reset") == "true":
                self.chatbotKnowledge = {}
                self.data["service"] = "chat"

        service = self.data.get("service")
        if "service" in self.chatbotKnowledge:
            if service != "chat":
                name = self.chatbotKnowledge.get("name")
                self.chatbotKnowledge = {}
                self.chatbotKnowledge["name"] = name
                self.chatbotKnowledge["service"] = service
        else:
            self.chatbotKnowledge["service"] = service
        yield Fact(service=self.chatbotKnowledge.get("service"))

        if not "question" in self.chatbotKnowledge:
            self.chatbotKnowledge["question"] = str()

        if "name" in self.chatbotKnowledge:
            yield Fact(name=self.chatbotKnowledge.get("name"))
        if "isReturn" in self.chatbotKnowledge:
            yield Fact(isReturn=self.chatbotKnowledge.get("isReturn"))
        if "fromLocation" in self.chatbotKnowledge:
            yield Fact(fromLocation=self.chatbotKnowledge.get("fromLocation"))
        if "toLocation" in self.chatbotKnowledge:
            yield Fact(toLocation=self.chatbotKnowledge.get("toLocation"))

        if "departDate" in self.chatbotKnowledge:
            yield Fact(departDate=self.chatbotKnowledge.get("departDate"))
        if "departTime" in self.chatbotKnowledge:
            yield Fact(departTime=self.chatbotKnowledge.get("departTime"))
        if "returnDate" in self.chatbotKnowledge:
            yield Fact(returnDate=self.chatbotKnowledge.get("returnDate"))
        if "returnTime" in self.chatbotKnowledge:
            yield Fact(returnTime=self.chatbotKnowledge.get("returnTime"))

        if "predictFromLocation" in self.chatbotKnowledge:
            yield Fact(
                predictFromLocation=self.chatbotKnowledge.get("predictFromLocation")
            )
        if "predictToLocation" in self.chatbotKnowledge:
            yield Fact(predictToLocation=self.chatbotKnowledge.get("predictToLocation"))

        if "predictDelay" in self.chatbotKnowledge:
            yield Fact(predictDelay=self.chatbotKnowledge.get("predictDelay"))
        if "currentStation" in self.chatbotKnowledge:
            yield Fact(currentStation=self.chatbotKnowledge.get("currentStation"))
        if "informationGiven" in self.chatbotKnowledge:
            yield Fact(informationGiven=self.chatbotKnowledge.get("informationGiven"))

        if "confromLocation" in self.chatbotKnowledge:
            yield Fact(confromLocation=self.chatbotKnowledge.get("confromLocation"))
        if "contoLocation" in self.chatbotKnowledge:
            yield Fact(contoLocation=self.chatbotKnowledge.get("contoLocation"))
        if "eventType" in self.chatbotKnowledge:
            yield Fact(eventType=self.chatbotKnowledge.get("eventType"))
        if "contingencyTime" in self.chatbotKnowledge:
            yield Fact(contingencyTime=self.chatbotKnowledge.get("contingencyTime"))
        if "severity" in self.chatbotKnowledge:
            yield Fact(severity=self.chatbotKnowledge.get("severity"))

        if "disruptionStation" in self.chatbotKnowledge:
            yield Fact(disruptionStation=self.chatbotKnowledge.get("disruptionStation"))

    @Rule(salience=50)
    def greeting(self):
        if "greeting" in self.data:
            pass

    @Rule(Fact(service="chat"), NOT(Fact(name=W())), salience=49)
    def username(self):
        if "name" in self.data:
            name = self.data.get("name")
            self.declare(Fact(name=name))
            self.chatbotKnowledge["name"] = name
        else:
            if self.chatbotKnowledge["question"] == "username":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "username"
            Message.select_response("bot_response", "username")

    @Rule(Fact(service="chat"), Fact(name=MATCH.name), salience=48)
    def service_type(self, name):
        if self.chatbotKnowledge["question"] == "service_type":
            Message.select_response("bot_response", "error")
        else:
            self.chatbotKnowledge["question"] = "service_type"
        Message.select_response("bot_response", "service_type", name)

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(fromLocation=W())),
        NOT(Fact(toLocation=W())),
        salience=47,
    )
    def location(self):
        error = False
        if "location" in self.data and len(self.data.get("location")) > 1:
            location = self.data.get("location")
            self.declare(Fact(fromLocation=location[0]))
            self.chatbotKnowledge["fromLocation"] = location[0]
            self.declare(Fact(toLocation=location[1]))
            self.chatbotKnowledge["toLocation"] = location[1]
        else:
            if self.chatbotKnowledge["question"] == "location":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "location"
            Message.select_response("bot_response", "location")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(departDate=W())),
        salience=46,
    )
    def departdate(self):
        departDate = "false"
        error = False
        if "dates" in self.data:
            departDate = self.data.get("dates")[0]
            if dateutil.parser.parse(departDate) < datetime.now():
                Message.select_response("bot_response", "past_date")
                error = True
            else:
                self.declare(Fact(departDate=departDate))
                self.chatbotKnowledge["departDate"] = departDate

        if (
            self.chatbotKnowledge["question"] == "departdate"
            and departDate == "false"
            and not error
        ):
            Message.select_response("bot_response", "wrong_date")
        else:
            self.chatbotKnowledge["question"] = "departdate"

        if departDate == "false" or error:
            Message.select_response("bot_response", "departdate")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(departTime=W())),
        salience=45,
    )
    def departtime(self):
        if "times" in self.data:
            departTime = self.data.get("times")
            self.declare(Fact(departTime=departTime[0]))
            self.chatbotKnowledge["departTime"] = departTime[0]
            del self.data["times"]
        else:
            if self.chatbotKnowledge["question"] == "departtime":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "departtime"
            Message.select_response("bot_response", "departtime")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(isReturn=W())),
        salience=44,
    )
    def if_return(self):
        if "return" in self.data:
            self.declare(Fact(isReturn="true"))
            self.chatbotKnowledge["isReturn"] = "true"
        elif "answer" in self.data:
            answer = self.data.get("answer")
            self.declare(Fact(isReturn=answer))
            self.chatbotKnowledge["isReturn"] = answer
            del self.data["answer"]
            if self.chatbotKnowledge["isReturn"] == "false":
                dblist = self.chatbotKnowledge.copy()
                getConn(dblist)
        else:
            if self.chatbotKnowledge["question"] == "if_return":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "if_return"
            Message.select_response("bot_response", "if_return")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        Fact(isReturn="true"),
        NOT(Fact(returnDate=W())),
        salience=43,
    )
    def returndate(self):
        returnDate = "false"
        error = False
        if "dates" in self.data:
            returnDate = self.data.get("dates")
            returnDate = returnDate[1] if len(returnDate) > 1 else returnDate[0]
            if dateutil.parser.parse(returnDate) < dateutil.parser.parse(
                self.chatbotKnowledge.get("departDate")
            ):
                Message.select_response("bot_response", "past_depart_date")
                error = True
            else:
                self.declare(Fact(returnDate=returnDate))
                self.chatbotKnowledge["returnDate"] = returnDate

        if (
            self.chatbotKnowledge["question"] == "returndate"
            and returnDate == "false"
            and not error
        ):
            Message.select_response("bot_response", "wrong_date")
        else:
            self.chatbotKnowledge["question"] = "returndate"

        if returnDate == "false" or error:
            Message.select_response("bot_response", "returndate")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(isQuestion=W())),
        Fact(isReturn="true"),
        NOT(Fact(returnTime=W())),
        salience=42,
    )
    def returntime(self):
        if "times" in self.data:
            returnTime = self.data.get("times")
            returnTime = returnTime[1] if len(returnTime) > 1 else returnTime[0]
            self.declare(Fact(returnTime=returnTime))
            self.chatbotKnowledge["returnTime"] = returnTime
            dblist = self.chatbotKnowledge.copy()
            getConn(dblist)
        else:
            if self.chatbotKnowledge["question"] == "returntime":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "returntime"
            Message.select_response("bot_response", "returntime")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="book"),
        NOT(Fact(givenTicket=W())),
        Fact(isReturn="false"),
        Fact(fromLocation=MATCH.fromLocation),
        Fact(toLocation=MATCH.toLocation),
        Fact(departDate=MATCH.departDate),
        Fact(departTime=MATCH.departTime),
        salience=41,
    )
    def show_single_ticket(self, fromLocation, toLocation, departDate, departTime):
        if not "givenTicket" in self.chatbotKnowledge:
            ticket = Ticket.get_ticket_single(
                fromLocation, toLocation, departDate, departTime
            )
            if not ticket:
                Message.select_response("bot_response", "ticket_error")
                Message.select_response("bot_response", "make_another_booking")
                self.declare(Fact(givenTicket=False))
                self.chatbotKnowledge["givenTicket"] = False
            else:
                Message.select_response("bot_response", "single_ticket")
                Message.ticket_info("display ticket", ticket)
                self.chatbotKnowledge["url"] = ticket.get("url")
                self.declare(Fact(givenTicket=True))
                self.chatbotKnowledge["givenTicket"] = True
                Message.select_response("bot_response", "make_another_booking")

    @Rule(
        Fact(service="book"),
        NOT(Fact(givenTicket=W())),
        Fact(isReturn="true"),
        Fact(fromLocation=MATCH.fromLocation),
        Fact(toLocation=MATCH.toLocation),
        Fact(departDate=MATCH.departDate),
        Fact(departTime=MATCH.departTime),
        Fact(returnDate=MATCH.returnDate),
        Fact(returnTime=MATCH.returnTime),
        salience=40,
    )
    def show_return_ticket(
        self, fromLocation, toLocation, departDate, departTime, returnDate, returnTime
    ):
        if not "givenTicket" in self.chatbotKnowledge:
            ticket = Ticket.get_ticket_return(
                fromLocation, toLocation, departDate, departTime, returnDate, returnTime
            )
            if not ticket:
                Message.select_response("bot_response", "ticket_error")
                Message.select_response("bot_response", "make_another_booking")
                self.declare(Fact(givenTicket=False))
                self.chatbotKnowledge["givenTicket"] = False
            else:
                Message.select_response("bot_response", "return_ticket")
                Message.ticket_info("display ticket", ticket)
                self.chatbotKnowledge["url"] = ticket.get("url")
                self.declare(Fact(givenTicket=True))
                self.chatbotKnowledge["givenTicket"] = True
                Message.select_response("bot_response", "make_another_booking")

    @Rule(
        Fact(service="predict"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(currentStation=W())),
        salience=39,
    )
    def ask_current_station(self):
        if "name" in self.data and self.data.get("name") != "delay":
            name = self.data.get("name")
            self.declare(Fact(currentStation=name))
            tiploc = get_tiploc(name)
            self.chatbotKnowledge["currentStation"] = tiploc
        else:
            if self.chatbotKnowledge["question"] == "ask_current_station":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_current_station"

            Message.select_response("bot_response", "ask_current_station")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="predict"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(predictDelay=W())),
        salience=38,
    )
    def ask_predict_delay(self):
        if "minutes" in self.data:
            minutes = self.data.get("minutes")[0]
            self.declare(Fact(predictDelay=minutes))
            self.chatbotKnowledge["predictDelay"] = minutes
            self.declare(Fact(informationGiven=False))
            self.chatbotKnowledge["informationGiven"] = False
            del self.data["minutes"]
        else:
            if self.chatbotKnowledge["question"] == "ask_predict_delay":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_predict_delay"
            Message.select_response("bot_response", "ask_predict_delay")
            self.declare(Fact(isQuestion=True))

    @Rule(Fact(service="predict"), Fact(informationGiven=False), salience=37)
    def predict_delay(self):
        expected_delay = get_data(self.chatbotKnowledge)
        self.chatbotKnowledge["expectedDelay"] = expected_delay
        dblist = self.chatbotKnowledge.copy()
        getConn(dblist)
        Message.show_delay("show delay", expected_delay)
        self.chatbotKnowledge["informationGiven"] = True
        self.declare(Fact(whatsNext=True))
        self.chatbotKnowledge["whatsNext"] = True

    @Rule(
        Fact(service="contingency"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(confromLocation=W())),
        NOT(Fact(contoLocation=W())),
        salience=36,
    )
    def ask_contingency_location(self):
        if "location" in self.data:
            location = self.data.get("location")
            self.declare(Fact(confromLocation=location[0]))
            self.chatbotKnowledge["confromLocation"] = location[0]
            self.declare(Fact(contoLocation=location[1]))
            self.chatbotKnowledge["contoLocation"] = location[1]
            del self.data["location"]
        else:
            if self.chatbotKnowledge["question"] == "ask_contingency_location":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_contingency_location"
            Message.select_response("bot_response", "ask_contingency_location")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="contingency"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(eventType=W())),
        salience=35,
    )
    def ask_eventType(self):
        if "eventType" in self.data:
            event = self.data.get("eventType")
            self.declare(Fact(eventType=event))
            self.chatbotKnowledge["eventType"] = event
        else:
            if self.chatbotKnowledge["question"] == "ask_eventType":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_eventType"
            data = get_rawdata()
            df = data.loc[(data["Station"] == self.chatbotKnowledge["confromLocation"])]
            event = ""
            for i in df.Status:
                if event != "":
                    event = event + ", " + i
                else:
                    event = event + i

            Message.send_response("bot_response", get_event(event))
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="contingency"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(contingencyTime=W())),
        salience=34,
    )
    def ask_contingency_time(self):
        if "times" in self.data:
            ctime = self.data.get("times")
            ctime = ctime[1] if len(ctime) > 1 else ctime[0]
            self.declare(Fact(contingencyTime=ctime))
            self.chatbotKnowledge["contingencyTime"] = ctime
        else:
            if self.chatbotKnowledge["question"] == "ask_contingency_time":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_contingency_time"
            Message.select_response("bot_response", "ask_contingency_time")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="contingency"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(severity=W())),
        salience=33,
    )
    def ask_severity(self):
        if "severity" in self.data:
            value = self.data.get("severity")
            self.declare(Fact(severity=value))
            self.chatbotKnowledge["severity"] = value
            self.declare(Fact(informationGiven=False))
            self.chatbotKnowledge["informationGiven"] = False
            dblist = self.chatbotKnowledge.copy()
            getConn(dblist)
        else:
            if self.chatbotKnowledge["question"] == "ask_severity":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_severity"
            Message.select_response("bot_response", "ask_severity")
            self.declare(Fact(isQuestion=True))

    @Rule(
        Fact(service="contingency"),
        NOT(Fact(isQuestion=W())),
        Fact(informationGiven=False),
        salience=32,
    )
    def show_contingency_plans(self):
        info = get_contingency_plan(
            self.chatbotKnowledge["confromLocation"], self.chatbotKnowledge["eventType"]
        )
        socketio.emit("contingency plans", info)
        self.declare(Fact(whatsNext=True))
        self.chatbotKnowledge["whatsNext"] = True

    @Rule(
        Fact(service="disruption"),
        NOT(Fact(isQuestion=W())),
        NOT(Fact(disruptionStation=W())),
        salience=31,
    )
    def ask_disruption_station(self):
        if "name" in self.data and (self.data.get("name") != "disruption"):
            station = self.data.get("name")
            self.declare(Fact(disruptionStation=station))
            self.chatbotKnowledge["disruptionStation"] = station
            dblist = self.chatbotKnowledge.copy()
            getConn(dblist)
            info = get_disruption_plan(station)
            socketio.emit("disruption plans", info)
            self.declare(Fact(whatsNext=True))
            self.chatbotKnowledge["whatsNext"] = True
        else:
            if self.chatbotKnowledge["question"] == "ask_disruption_station":
                Message.select_response("bot_response", "error")
            else:
                self.chatbotKnowledge["question"] = "ask_disruption_station"
            Message.select_response("bot_response", "ask_disruption_station")
            self.declare(Fact(isQuestion=True))

    @Rule(Fact(whatsNext=True), salience=30)
    def whats_next(self):
        if self.chatbotKnowledge["question"] == "whats_next":
            Message.select_response("bot_response", "error")
        else:
            self.chatbotKnowledge["question"] = "whats_next"
        Message.select_response("bot_response", "whats_next")


class Message(object):
    def ticket_info(event_name, ticket_info):
        socketio.emit(event_name, ticket_info)

    def show_delay(event_name, delay):
        message = {"message": delay, "time_sent": datetime.now().strftime("%H:%M")}
        socketio.emit(event_name, message)

    def send_response(event_name, message):
        message = {"message": message, "time_sent": datetime.now().strftime("%H:%M")}
        socketio.emit(event_name, message)

    def select_response(event_name, feedback_name, string=str()):
        feedbacks = config_data("feedback")[feedback_name]
        feedback = random.choice(feedbacks)
        feedback = feedback.replace("%s", string)
        Message.send_response(event_name, feedback)


def suffix(day):
    return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def custom_strftime(date, type_format):
    return date.strftime(type_format).replace("{S}", str(date.day) + suffix(date.day))


def get_strptime(string):
    return datetime.strptime(string, "%d%m%y")


def to_date(string):
    return str(custom_strftime(get_strptime(string), "{S} %B %Y"))


def custom_to_date(string, type_format):
    return str(datetime.strftime(get_strptime(string), type_format))


def get_tiploc(name):
    data_path = "./static/assets/configuration/stations.csv"
    data = pd.read_csv(data_path)
    selected_row = data.loc[data["name"] == name]
    selected_row = selected_row.reset_index()
    tpl_value = selected_row.tpl[0]
    return tpl_value


def get_rawdata():
    data_path = "./static/assets/configuration/Bournemouthline.csv"
    data = pd.read_csv(data_path)
    return data


def get_event(event):
    a = "Select the type of event"
    val = a + " " + event
    return val


def set_data(entities):
    engine.data = entities
    engine.reset()
    engine.run()


@app.route("/")
@app.route("/chatbot")
def index():
    return render_template("/index.html")


from nlp import get_nlp_data
from web_scrape import Ticket
from model import *

# from contingency_data import *
# from disruption_data import *
from contingency import get_contingency_plan
from disruption import get_disruption_plan
from userconvodb import getConn


@socketio.on("connect")
def connect():
    Message.select_response("bot_response", "greeting")


@socketio.on("client_message")
def handle_message(data, methods=["GET", "POST"]):
    Message.send_response("user_response", data["message"])
    set_data(get_nlp_data(data))


if __name__ == "__main__":
    engine = Knowledge()
    engine.chatbotKnowledge = {}
    socketio.run(app)
