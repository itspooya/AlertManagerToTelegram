from time import sleep

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, List
import os
import telegram
from emoji import emojize
from telegram import Bot
from dotenv import load_dotenv
import datetime
import pytz
import sqlite3
from telegram.error import RetryAfter, TimedOut

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
chat = os.getenv("CHAT_ID")
whitelist_ip = os.getenv("WHITELIST_IP")
admin_id = os.getenv("ADMIN_ID")
timezone = os.getenv("TIMEZONE")
conn = sqlite3.connect("alert.db")
cur = conn.cursor()
cur.execute(
    """CREATE TABLE  IF NOT EXISTS alerts(
ID INTEGER PRIMARY KEY AUTOINCREMENT,
FINGERPRINT VARCHAR(255),
MESSAGE_ID VARCHAR(255),
MESSAGE_TEXT TEXT)
"""
)
conn.commit()
conn.close()
app = FastAPI()


class Annotations(BaseModel):
    description: str
    summary: str


class commonLabels_type(BaseModel):
    alertname: str
    instance: str
    job: str
    severity: str


class commonAnnotations_type(BaseModel):
    description: str
    summary: str


class Labels(BaseModel):
    alertname: str
    instance: str
    job: str
    severity: str


class Alert(BaseModel):
    status: str
    labels: Labels
    startsAt: datetime.datetime
    endsAt: datetime.datetime
    annotations: Annotations
    generatorURL: Optional[str] = None
    fingerprint: str


class MainAlert(BaseModel):
    receiver: str
    status: str
    alerts: List[Alert]
    commonAnnotations: Optional[commonAnnotations_type] = None
    commonLabels: Optional[commonLabels_type] = None


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Error: {exc.errors()}")
    print(f"Body {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/")
async def root():
    return "Working"


@app.post("/sendalert")
async def sendalert(alert: MainAlert):
    conn = sqlite3.connect("alert.db")
    bot = Bot(token)
    kb = [
        [telegram.InlineKeyboardButton(text="Resolved", callback_data="/resolved")],
        [telegram.InlineKeyboardButton(text="Check", callback_data="/check")],
        [telegram.InlineKeyboardButton(text="Delete", callback_data="/delete")],
        [telegram.InlineKeyboardButton(text="False", callback_data="/false")],
    ]
    kb_markup = telegram.InlineKeyboardMarkup(kb, one_time_keyboard=True)
    if alert.status == "firing":
        i = 0
        while i < 11:
            try:
                result = bot.sendMessage(
                    chat_id=chat,
                    text=emojize(
                        f":red_circle: Alert: {alert.alerts[0].labels.alertname}\n\nSummary:{alert.alerts[0].annotations.summary}\n\nDescription:{alert.alerts[0].annotations.description}\n\nState: {alert.status}\n\nStartTime:{alert.alerts[0].startsAt}\n",
                        use_aliases=True,
                    ),
                    reply_markup=kb_markup,
                )
                # tmp_dict = {"message_id": result.message_id, "fingerprint": data["alerts"]["fingerprint"],
                #             "text": result.text}
                # fingerprint_message_list.append(tmp_dict)
                cur = conn.cursor()

                cur.execute(
                    """INSERT INTO alerts (FINGERPRINT,MESSAGE_ID,MESSAGE_TEXT) VALUES (?,?,?)""",
                    (alert.alerts[0].fingerprint, result.message_id, result.text),
                )
                conn.commit()
                conn.close()
            except RetryAfter as retry:
                sleep(int(retry.retry_after))
                i += 1
            except TimedOut:
                sleep(1)
                i += 1

            except Exception as e:
                bot.sendMessage(
                    chat_id=chat,
                    text=emojize(
                        f":red_circle: Alert: Problem With Bot\n\nState: alerting\n\n@{admin_id}\n\nLOG: {e}\n\nStartTIme:{datetime.datetime.now(pytz.timezone(timezone))}\n",
                        use_aliases=True,
                    ),
                    reply_markup=kb_markup,
                )
                break
            finally:
                break
        return "OK"
    elif alert.status == "resolved":

        cur = conn.cursor()
        finger_print_string = alert.alerts[0].fingerprint
        cur.execute(
            "SELECT * FROM alerts where FINGERPRINT = ?", (finger_print_string,)
        )
        records = cur.fetchall()

        for item in records:
            if item[1] == finger_print_string:
                tries = 0
                while tries < 11:
                    try:
                        bot.editMessageText(
                            chat_id=chat,
                            text=emojize(
                                f":white_check_mark: Resolved\n\n{item[3]}\n\nEndTime: {datetime.datetime.now(pytz.timezone(timezone))}\n\n",
                                use_aliases=True,
                            ),
                            message_id=item[2],
                        )
                        break
                    except TimedOut:
                        sleep(1)
                        tries += 1
                    except RetryAfter as retry:
                        sleep(int(retry.retry_after))
                        tries += 1
                    except Exception as e:
                        bot.sendMessage(
                            chat_id=chat,
                            text=emojize(
                                f":red_circle: Alert: Problem With Bot\n\nState: alerting\n\n@{admin_id}\n\nLOG: {e}\n\nStartTIme:{datetime.datetime.now(pytz.timezone(timezone))}\n",
                                use_aliases=True,
                            ),
                            reply_markup=kb_markup,
                        )
                        break
                    finally:
                        break

        return "OK"

    print(alert)
    return alert
