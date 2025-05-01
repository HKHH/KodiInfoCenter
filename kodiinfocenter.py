#!/usr/bin/env python3
import sys
import os
import json
import datetime
import xbmc
import xbmcaddon
import base64
from urllib.parse import quote

from PyQt5.QtCore import Qt, QTimer, QUrl, QByteArray
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedLayout, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
#Pfad zum Bild
image_dir = os.path.dirname(os.path.abspath(__file__))

#Einstellung Einlesen
addon = xbmcaddon.Addon()
PORT = addon.getSetting("hostport")
USER = addon.getSetting("user")
PASSWORD = addon.getSetting("password")

REFRESHRATE = int(addon.getSetting("refreshrate")) * 1000
IDLETITLEFONTSIZE = int(addon.getSetting("idletitlefontsize"))
kodisystimeformat = int(addon.getSetting("systimeformat"))
if kodisystimeformat == 0:
   SYSTEMTIMEFORMAT = "%H:%M"
elif kodisystimeformat == 1:
   SYSTEMTIMEFORMAT = "%I:%M %p"
elif kodisystimeformat == 2:
   SYSTEMTIMEFORMAT = "%Y-%m-%d %H:%M"
elif kodisystimeformat == 3:
   SYSTEMTIMEFORMAT = "%A %H:%M"

# Wetterdaten: COUNTRY, CITY und POSTAL_CODE
SHOWWEATHERINFO = addon.getSetting("showweatherinfo")
COUNTRY = addon.getSetting("country")
LANG = addon.getSetting("lang")
CITY = addon.getSetting("city")
POSTAL_CODE = addon.getSetting("postcode")
WEATHERURL = addon.getSetting("weatherurl")
WEATHER_URL = f"{WEATHERURL}".format(CITY=CITY, POSTAL_CODE=POSTAL_CODE, COUNTRY=COUNTRY, LANG=LANG)
WEATHERREFRESH = int(addon.getSetting("weatherrefresh"))*60000
WEATHERFONTSIZE = int(addon.getSetting("weatherfontsize"))

#Player:
AWTITLEFONTSIZE = int(addon.getSetting("awtitlefontsize"))
AWTOTALTIMEFONTSIZE = int(addon.getSetting("awtotaltimefontsize"))
AUDIO_RAW1 = int(addon.getSetting("audioformattop"))
if AUDIO_RAW1 == 0:
   AUDIOFORMAT1 = "{artist}"
elif AUDIO_RAW1 == 1:
   AUDIOFORMAT1 = "{title}"
elif AUDIO_RAW1 == 2:
   AUDIOFORMAT1 = "{album}"
elif AUDIORAW1 == 3:
   AUDIOFORMAT1 = os.path.basename("{file}")
elif AUDIO_RAW1 == 4:
   AUDIOFORMAT1 = ""

AUDIO_RAW2 = int(addon.getSetting("audioformatmiddle"))
if AUDIO_RAW2 == 0:
   AUDIOFORMAT2 = "{artist}"
elif AUDIO_RAW2 == 1:
   AUDIOFORMAT2 = "{title}"
elif AUDIO_RAW2 == 2:
   AUDIOFORMAT2 = "{album}"
elif AUDIORAW2 == 3:
   AUDIOFORMAT2 = os.path.basename("{file}")
elif AUDIO_RAW2 == 4:
   AUDIOFORMAT2 = ""

AUDIO_RAW3 = int(addon.getSetting("audioformatbottom"))
if AUDIO_RAW3 == 0:
   AUDIOFORMAT3 = "{artist}"
elif AUDIO_RAW3 == 1:
   AUDIOFORMAT3 = "{title}"
elif AUDIO_RAW3 == 2:
   AUDIOFORMAT3 = "{album}"
elif AUDIO_RAW3 == 3:
   AUDIOFORMAT3 = os.path.basename("{file}")
elif AUDIO_RAW3 == 4:
   AUDIOFORMAT3 = ""

VIDEO_RAW1 = int(addon.getSetting("videoformattop"))
if VIDEO_RAW1 == 0:
   VIDEOFORMAT1 = "{artist}"
elif VIDEO_RAW1 == 1:
   VIDEOFORMAT1 = "{title}"
elif VIDEO_RAW1 == 2:
   VIDEOFORMAT1 = "{album}"
elif VIDEO_RAW1 == 3:
   VIDEOFORMAT1 = os.path.basename("{file}")
elif VIDEO_RAW1 == 4:
   VIDEOFORMAT1 = ""

VIDEO_RAW2 = int(addon.getSetting("videoformatmiddle"))
if VIDEO_RAW2 == 0:
   VIDEOFORMAT2 = "{artist}"
elif VIDEO_RAW2 == 1:
   VIDEOFORMAT2 = "{title}"
elif VIDEO_RAW2 == 2:
   VIDEOFORMAT2 = "{album}"
elif VIDEO_RAW2 == 3:
   VIDEOFORMAT2 = os.path.basename("{file}")
elif VIDEO_RAW2 == 4:
   VIDEOFORMAT2 = ""

VIDEO_RAW3 = int(addon.getSetting("videoformatbottom"))
if VIDEO_RAW3 == 0:
   VIDEOFORMAT3 = "{artist}"
elif VIDEO_RAW3 == 1:
   VIDEOFORMAT3 = "{title}"
elif VIDEO_RAW3 == 2:
   VIDEOFORMAT3 = "{album}"
elif VIDEO_RAW3 == 3:
   VIDEOFORMAT3 = os.path.basename("{file}")
elif VIDEO_RAW3 == 4:
   VIDEOFORMAT3 = ""


# Wert in die Kodi-Logdatei schreiben
xbmc.log(f"Der Schalter für Wetterdaten staht auf: {SHOWWEATHERINFO}", xbmc.LOGINFO)
xbmc.log(f"Der Wert der Einstellung für Frequenz ist: {REFRESHRATE}", xbmc.LOGINFO)
xbmc.log(f"Der Wert der Einstellung für Land ist: {COUNTRY}", xbmc.LOGINFO)
xbmc.log(f"Der Wert der Einstellung für Sprache ist: {LANG}", xbmc.LOGINFO)
xbmc.log(f"Der Wert der Einstellung für Stadt ist: {CITY}", xbmc.LOGINFO)
xbmc.log(f"Der Wert der Einstellung für Postleitzahl ist: {POSTAL_CODE}", xbmc.LOGINFO)
#xbmc.log(f"Der Wert der Einstellung für URL ist: {WEATHERURL}", xbmc.LOGINFO)

# Kodi-Konfiguration – bitte ggf. anpassen
kodi_url = "http://localhost:" + PORT + "/jsonrpc"
kodi_user = USER         # Kodi-Benutzername
kodi_password = PASSWORD     # Kodi-Passwort

# Berechne den HTTP-Auth-Header (Basic Authentication)
auth_string = f"{kodi_user}:{kodi_password}"
auth_b64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
auth_header_value = "Basic " + auth_b64

app = QApplication(sys.argv)

# Hauptfenster: 800x480, rahmenlos, schwarzer Hintergrund
main_widget = QWidget()
main_widget.setFixedSize(800, 480)
main_widget.setWindowFlags(Qt.FramelessWindowHint)
main_widget.setStyleSheet("background-color: black;")

# QStackedLayout:
#    Index 0 = Aktiv-Modus (Kodi läuft)
#    Index 1 = Idle-Modus (kein aktiver Player)
#    Index 2 = Fehler-Modus (Verbindung zu Kodi nicht möglich)
stack = QStackedLayout(main_widget)

# -------------------------
# Aktiv-Modus (Kodi spielt)
# -------------------------
active_widget = QWidget()
active_grid = QGridLayout(active_widget)
active_grid.setContentsMargins(0, 0, 0, 0)

# Mittig: Anzeige von Titelinformationen (Artist/Title oder Dateiname)
active_center_label = QLabel("")
active_center_label.setAlignment(Qt.AlignCenter)
active_center_font = QFont("Arial", AWTITLEFONTSIZE)
active_center_label.setFont(active_center_font)
active_center_label.setStyleSheet("color: white;")
active_grid.addWidget(active_center_label, 0, 0)

# Rechts unten: Anzeige der Gesamtdauer (totaltime) im Format HH:MM:SS, Arial 24
active_bottom_label = QLabel("")
active_bottom_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
active_bottom_font = QFont("Arial", AWTOTALTIMEFONTSIZE)
active_bottom_label.setFont(active_bottom_font)
active_bottom_label.setStyleSheet("color: white;")
active_grid.addWidget(active_bottom_label, 0, 0, alignment=Qt.AlignRight | Qt.AlignBottom)

stack.addWidget(active_widget)

# -------------------------
# Idle-Modus (kein aktiver Player)
# -------------------------
idle_widget = QWidget()
idle_layout = QVBoxLayout(idle_widget)
idle_layout.setContentsMargins(0, 0, 0, 0)
idle_layout.setSpacing(0)

# Obere Zeile: Wetterinformationen oben rechts
weather_layout = QHBoxLayout()
weather_layout.setContentsMargins(0, 0, 0, 0)
weather_layout.addStretch()
weather_label = QLabel("")
weather_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
weather_font = QFont("Arial", WEATHERFONTSIZE)
weather_label.setFont(weather_font)
weather_label.setStyleSheet("color: white; margin: 0px;")
weather_layout.addWidget(weather_label)
idle_layout.addLayout(weather_layout)

# Vertikaler Spacer, damit der mittlere Bereich zentral positioniert ist.
idle_layout.addStretch()

# Mittlerer Bereich: Überschrift, Bild und Uhrzeit
center_widget = QWidget()
center_layout = QVBoxLayout(center_widget)
center_layout.setContentsMargins(0, 0, 0, 0)
center_layout.setSpacing(10)
center_layout.setAlignment(Qt.AlignCenter)

idle_title_label = QLabel("KODI Infocenter")
idle_title_label.setAlignment(Qt.AlignCenter)
idle_title_font = QFont("Arial", IDLETITLEFONTSIZE)
idle_title_label.setFont(idle_title_font)
idle_title_label.setStyleSheet("color: white;")
center_layout.addWidget(idle_title_label)

idle_image_label = QLabel()
idle_image_label.setAlignment(Qt.AlignCenter)
#image_dir = os.path.dirname(os.path.abspath(__file__))
pixmap = QPixmap(image_dir + "/kodi.png")
if not pixmap.isNull():
    idle_image_label.setPixmap(pixmap.scaledToWidth(150, Qt.SmoothTransformation))
center_layout.addWidget(idle_image_label)

idle_time_label = QLabel("")
idle_time_label.setAlignment(Qt.AlignCenter)
idle_time_font = QFont("Arial", IDLETITLEFONTSIZE)
idle_time_label.setFont(idle_time_font)
idle_time_label.setStyleSheet("color: white;")
center_layout.addWidget(idle_time_label)

idle_layout.addWidget(center_widget)
idle_layout.addStretch()

stack.addWidget(idle_widget)

# -------------------------
# Fehler-Modus (Verbindung zu Kodi nicht möglich)
# -------------------------
error_widget = QWidget()
error_layout = QVBoxLayout(error_widget)
error_layout.setContentsMargins(0, 0, 0, 0)
error_layout.addStretch()
error_label = QLabel("FEHLER: Connection refused")
error_label.setAlignment(Qt.AlignCenter)
error_font = QFont("Arial", 30)
error_label.setFont(error_font)
error_label.setStyleSheet("color: red;")
error_layout.addWidget(error_label)
error_layout.addStretch()
stack.addWidget(error_widget)

# -------------------------
# QNetworkAccessManager (für asynchrone Anfragen)
# -------------------------
network_manager = QNetworkAccessManager(main_widget)

# Hilfsfunktion: Sende eine Kodi-JSON-Anfrage asynchron (mit Auth-Header)
def send_kodi_request(payload, callback):
    req = QNetworkRequest(QUrl(kodi_url))
    req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
    req.setRawHeader(b"Authorization", auth_header_value.encode("utf-8"))
    data = QByteArray(json.dumps(payload).encode("utf-8"))
    reply = network_manager.post(req, data)
    reply.finished.connect(lambda: callback(reply))

# Hilfsfunktion: Setzt den Idle-Modus mit aktueller Uhrzeitanzeige.
def setIdleModeWithTime():
    stack.setCurrentIndex(1)
    current_time = datetime.datetime.now().strftime(SYSTEMTIMEFORMAT)
    idle_time_label.setText(current_time)

# -------------------------
# Asynchrone Rückruf-Funktionen zur Verarbeitung der Kodi-Antworten
# -------------------------
def process_active_reply(reply):
    if reply.error() != QNetworkReply.NoError:
        error_label.setText("FEHLER: " + reply.errorString())
        stack.setCurrentIndex(2)
        reply.deleteLater()
        return
    try:
        data_str = bytes(reply.readAll()).decode("utf-8")
        data = json.loads(data_str)
    except Exception as e:
        print("Fehler beim Lesen der Antwort (Player.GetActivePlayers):", e)
        setIdleModeWithTime()
        reply.deleteLater()
        return

    if not data.get("result"):
        setIdleModeWithTime()
    else:
        player = data["result"][0]
        player_id = player["playerid"]
        player_type = player.get("type", "")
        payload_item = {
            "jsonrpc": "2.0",
            "method": "Player.GetItem",
            "params": {
                "playerid": player_id,
                "properties": ["artist", "title", "album", "thumbnail", "file"]
            },
            "id": 1
        }
        send_kodi_request(payload_item, lambda rep: process_item_reply(rep, player_id, player_type))
    reply.deleteLater()

def process_item_reply(reply, player_id, player_type):
    if reply.error() != QNetworkReply.NoError:
        error_label.setText("FEHLER: " + reply.errorString())
        stack.setCurrentIndex(2)
        reply.deleteLater()
        return
    try:
        data_str = bytes(reply.readAll()).decode("utf-8")
        data_item = json.loads(data_str)
        item = data_item.get("result", {}).get("item", {})
    except Exception as e:
        print("Fehler beim Lesen der Antwort (Player.GetItem):", e)
        setIdleModeWithTime()
        reply.deleteLater()
        return

    payload_props = {
        "jsonrpc": "2.0",
        "method": "Player.GetProperties",
        "params": {
            "playerid": player_id,
            "properties": ["totaltime"]
        },
        "id": 1
    }
    send_kodi_request(payload_props, lambda rep: process_props_reply(rep, item, player_type))
    reply.deleteLater()

def process_props_reply(reply, item, player_type):
    if reply.error() != QNetworkReply.NoError:
        error_label.setText("FEHLER: " + reply.errorString())
        stack.setCurrentIndex(2)
        reply.deleteLater()
        return
    try:
        data_str = bytes(reply.readAll()).decode("utf-8")
        data_props = json.loads(data_str)
        totaltime = data_props.get("result", {}).get("totaltime", {})
        t_hours   = totaltime.get("hours", 0)
        t_minutes = totaltime.get("minutes", 0)
        t_seconds = totaltime.get("seconds", 0)
        # Gesamtdauer im Format HH:MM:SS
        total_time_str = f"{t_hours:02}:{t_minutes:02}:{t_seconds:02}"
    except Exception as e:
        print("Fehler beim Lesen der Antwort (Player.GetProperties):", e)
        setIdleModeWithTime()
        reply.deleteLater()
        return

    if player_type == "audio":
        artists = item.get("artist", [])
        artist = ", ".join(artists) if artists else ""
        title = item.get("title", "")
        album = item.get("album", "")   
        file = item.get("file", "")   
        display_text1 = f"{AUDIOFORMAT1}".format(artist=artist, title=title, album=album, file=file, nothing="")
        display_text2 = f"{AUDIOFORMAT2}".format(artist=artist, title=title, album=album, file=file, nothing="")
        display_text3 = f"{AUDIOFORMAT3}".format(artist=artist, title=title, album=album, file=file, nothing="")
    elif player_type == "video":
        artists = item.get("artist", [])
        artist = ", ".join(artists) if artists else ""
        title = item.get("title", "")
        album = "" #item.get("album", "") if album else ""  
        file_path = item.get("file", "")
        file = os.path.basename(file_path) if file_path else "Video"
        display_text1 = f"{VIDEOFORMAT1}".format(artist=artist, title=title, album=album, file=file,  nothing="")
        display_text2 = f"{VIDEOFORMAT2}".format(artist=artist, title=title, album=album, file=file,  nothing="")
        display_text3 = f"{VIDEOFORMAT3}".format(artist=artist, title=title, album=album, file=file,  nothing="")
    else:
        display_text1 = ""
        display_text2 = ""
        display_text3 = ""

    active_center_label.setText(display_text1 + "\n" + display_text2 + "\n" + display_text3)
    active_bottom_label.setText(total_time_str)
    stack.setCurrentIndex(0)
    reply.deleteLater()

# -------------------------
# Asynchrone Wetterabfrage mit QNetworkAccessManager
# -------------------------
def update_weather():
    req = QNetworkRequest(QUrl(WEATHER_URL))
    req.setRawHeader(b"User-Agent", b"Mozilla/5.0")
    reply = network_manager.get(req)
    reply.finished.connect(lambda: process_weather_reply(reply))

def process_weather_reply(reply):
    if reply.error() != QNetworkReply.NoError:
        print("Wetterupdate Fehler:", reply.errorString())
        weather_label.setText("Wetterinfo Fehler")
        reply.deleteLater()
        return
    try:
        text = bytes(reply.readAll()).decode("utf-8").strip().replace("\n", " ")
        weather_label.setText(text)
    except Exception as e:
        print("Fehler bei Wetterverarbeitung:", e)
        weather_label.setText("Wetterinfo Fehler")
    reply.deleteLater()

# -------------------------
# Update-Funktionen per Timer (Kodi alle 2000 ms, Wetter alle 5 Minuten)
# -------------------------
def update_info_async():
    payload_active = {
        "jsonrpc": "2.0",
        "method": "Player.GetActivePlayers",
        "params": {},
        "id": 1
    }
    send_kodi_request(payload_active, process_active_reply)

info_timer = QTimer()
info_timer.timeout.connect(update_info_async)
info_timer.start(REFRESHRATE) #2000 Millisekunden = 2 Sekunden

weather_timer = QTimer()
weather_timer.timeout.connect(update_weather)
weather_timer.start(WEATHERREFRESH) #300000 Millisekunden = 300 Sekunden = 5 Minuten
if SHOWWEATHERINFO == "true":
   update_weather()  # Initialer Abruf
else:
   text=""
   weather_label.setText(text)

# Fenster anzeigen
main_widget.show()
sys.exit(app.exec_())
