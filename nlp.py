import spacy, re, json, dateutil.parser, en_core_web_sm
from spacy.lang.en import English as english
from itertools import tee, islice, chain
import re
import datetime

parser = english()
nlp = en_core_web_sm.load()


greeting = re.compile(r"\b(?i)(hello|hey|hi|yo)\b")
false = re.compile(r"\b(?i)(false|no|nah)\b")
true = re.compile(r"\b(?i)(true|yes|yeah|yh)\b")
fromTo = re.compile("((?<=from)(.*)(?<=to)(.*))|((?<=is)(.*)(?<=is)(.*))")
toFrom = re.compile(r"(?i)(.*) from (.*)")
time = re.compile(r"^(([01]\d|2[0-3]):([0-5]\d)|24:00)$")
eventType = re.compile(
    r"\b(?i)(UMSL blocked|DMSL blocked|DMFL blocked|UMFL blocked|DMFL or UMFL blocked|DMSL or UMSL blocked|DMSL & DMFL blocked|UMSL & UMFL blocked|All lines blocked|Both lines blocked|One line blocked|Down line blocked|One or both lines blocked|All lines blocked or both lines blocked in one direction|One line available through Southampton Tunnel)\b"
)
severity = re.compile(r"\b(?i)(full|full blockage|partial|partial blockage)\b")


def get_nlp_data(json):
    message = json["message"]
    message = nlp(message)
    results = {}
    results["service"] = "chat"

    if greeting.search(str(message)):
        results["greeting"] = "true"

    hasName = False
    for entity in message.ents:
        if entity.label_ == "PERSON":
            results["name"] = entity.text
            hasName = True
    if not hasName and len(str(message).split()) == 1 and not ("greeting" in results):
        results["name"] = str(message)

    if false.search(str(message)):
        results["answer"] = "false"
    if true.search(str(message)):
        results["answer"] = "true"

    def fromto_pattern(txt):
        x = re.findall("(?<=from)(.*)(?<= to)(.*)", txt)
        y = re.findall("(?<=is)(.*)(?<=is)(.*)", txt)
        if x != []:
            for i in x:
                first_split = i[0]
                first_split = str(first_split)

                if first_split.__contains__("Hampton") or first_split.__contains__(
                    "Surbiton"
                ):
                    print("no need to replace with to")
                    cleaned_from_stat = first_split[:-3]
                elif first_split[-2:] == "to":
                    cleaned_from_stat = first_split[:-3]
                else:
                    cleaned_from_stat = first_split.replace("to", "")
                print("clean", cleaned_from_stat)
        if y != []:
            for i in y:
                first_split = i[0]
                first_split = str(first_split)
                cleaned_from_stat = first_split.replace("and destination is", "")
        return (cleaned_from_stat.strip(), i[1].strip())

    locations = []
    toMatch = toFrom.search(str(message))
    if toMatch:
        locations.append(toMatch[0].split()[0])
        locations.append(toMatch[0].split()[2])
    fromMatch = fromTo.search(str(message))
    if fromMatch:
        location_result = fromto_pattern(str(message))
        locations = []
        locations.append(location_result[0])
        locations.append(location_result[1])
    if len(locations) > 0:
        results["location"] = locations

    minutes = []
    dates = []
    times = []
    for entity in message.ents:
        if entity.text.isdigit():
            minutes.append(entity.text)

        
        if entity.label_ == "DATE" or entity.label_ == "CARDINAL":
            try:
                if entity.label_ == "CARDINAL":
                    date = message
                    date_time_str = date
                    date_time_str = str(date_time_str).replace("-", "")
                    date_time_obj = datetime.datetime.strptime(date_time_str, "%d%m%Y")
                    date = date_time_obj
                    date = (
                        str(date.day).zfill(2)
                        + str(date.month).zfill(2)
                        + (str(date.year)[2:])
                    )
                    dates.append(date)
                else:
                    date = dateutil.parser.parse(entity.text)
                    date = (
                        str(date.day).zfill(2)
                        + str(date.month).zfill(2)
                        + (str(date.year)[2:])
                    )
                    dates.append(date)
            except:
                Message.emit_feedback("display received message", "wrong_date")

        if entity.label_ == "TIME":
            date = dateutil.parser.parse(entity.text)
            times.append(str(date.hour).zfill(2) + str(date.minute).zfill(2))

    if time.search(str(message)):
        date = dateutil.parser.parse(str(message))
        times.append(str(date.hour).zfill(2) + str(date.minute).zfill(2))

    if len(minutes) > 0:
        results["minutes"] = minutes
    if len(dates) > 0:
        results["dates"] = dates
    if len(times) > 0:
        results["times"] = times

    for token in message:
        token = str(token).lower()

        if token in {"predict", "prediction", "delay", "delays"}:
            results["service"] = "predict"

        if token in {"travel", "travels", "book", "booking", "bookings"}:
            results["service"] = "book"

        if token in {"return", "returns"}:
            results["return"] = "true"

        if token in {"contingency", "Contingency"}:
            results["service"] = "contingency"

        if token in {"disruption", "Disruption"}:
            results["service"] = "disruption"

    if "come back" in str(message):
        results["return"] = "true"

    event = eventType.search(str(message))
    if event:
        results["eventType"] = str(message)

    val = severity.search(str(message).lower())
    if val:
        results["severity"] = str(message)

    return results


from app import Message