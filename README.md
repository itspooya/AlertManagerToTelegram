# Telegramolert

## Goal? TLDR
This project aims to integrate Prometheus-Alert-Manager with Telegram

### Tech Stack: Python3, Prometheus, AlertManager, FastAPI, Python-Telegram-Bot

## Why?

One of the problems with prometheus alert manager is that you can't integrate it with Telegram messanger, due to Large community of telegram users and popularity of
, I have created integration of Prometheus Alert Manager with telegram

## How to run it

1. Create .env inside TelegramReceiver folder and fill it with TELEGRAM_TOKEN, TIMEZONE(Asia/Tehran for example)

2. Create .env inside FastAPI folder and fill it with TELEGRAM_TOKEN(Same as first one), CHAT_ID(chat id of telegram group),
WHITELIST_IP(default setting 127.0.0.1), ADMIN_ID(admin username in telegram to send failure logs and exceptions), TIMEZONE(Same As first one)

3. Install Docker and docker-compose

4. run ```docker-compose up -d --build```

5. Fill alert-manager receiver with following config
```
receivers:
- name: 'webhook'
  webhook_configs:
  - url: "http://flaskappalert:6000/sendalert"
    send_resolved: true
    max_alerts: 1
```
