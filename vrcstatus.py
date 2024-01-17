import time
import psutil
from win32gui import GetWindowText, GetForegroundWindow
import win32api
import threading
from pythonosc import udp_client
from pynput.keyboard import Listener
import asyncio

import function_library

ON_MEDIA_PLAYING = 'Now playing {title} by {artists} {timeline_current}/{timeline_end}'
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
wtime = 4

def on_press(key):
    global afk 
    global afktimer
    afktimer = 0
    afk = False

def keylistener_function():
 with Listener(on_press=on_press) as listener:
    listener.join()

x = threading.Thread(target=keylistener_function,)
x.start()


def convert_to_preferred_format(sec):
   sec = sec % (24 * 3600)
   hour = sec // 3600
   sec %= 3600
   min = sec // 60
   sec %= 60
   return "%02d:%02d:%02d" % (hour, min, sec) 


async def spotifyinfo():
   try:
    song_info, timeline_current, timeline_end, media_state = await function_library.get_media_info()
   except:
     client.send_message("/chatbox/input",["Nothing playing now", True])
     time.sleep(wtime)
     return
   title = song_info['title']
   artists = song_info['artist']
   timeline_current, timeline_end = function_library.format_timestamp(timeline_current, timeline_end)
   if title != '' and artists != '':
      if function_library.is_media_playing(media_state):
            message = f"{ON_MEDIA_PLAYING.format(title=title, artists=artists, timeline_current=timeline_current, timeline_end=timeline_end)}"
            message = function_library.format_string_if_too_long(message)
            client.send_message("/chatbox/input",["||"+message+"||", True])
            time.sleep(wtime)

def byte(a:int):
   b = "Byte"
   if a>1024:
    a = a/1024
    b = "KB"
   if a>1024:
    a = a/1024
    b = "MB"
   if a>1024:
    a = a/1024
    b = "GB"
   return str(int(a))+b

async def main():
 savedpos = win32api.GetCursorPos()
 afk = False
 afktimer = 0
 afksec = 0
 aftertime = 0
 while True:
    focus = GetWindowText(GetForegroundWindow())
    if focus == "Program Manager":
     focus = "Desktop"
    elif focus.find("YouTube —") != -1:
     focus = "YouTube"
    elif focus.find("- Discord") != -1:
      focus = "Discord"
    elif focus == "":
     focus = "Taskbar"
    curpos = win32api.GetCursorPos()
    if savedpos == curpos and afktimer/60 > 5:
       afk = True
    elif savedpos != curpos:
       afktimer = 0
       afk = False
    savedpos = curpos

    if not afk:
     afksec = 0
     aftertime = aftertime+1
     
     if aftertime == 4:
      aftertime = 0
      await spotifyinfo()
     else:
      client.send_message("/chatbox/input",[f"CPU:{psutil.cpu_percent()}% RAM:{byte(psutil.virtual_memory()[3])}/{byte(psutil.virtual_memory()[0])}       Focused on: {focus}", True])
    else:
      afksec += wtime
      client.send_message("/chatbox/input",[f"I fell asleep 😴 like {convert_to_preferred_format(afksec)} ⏰ ", True])
    afktimer += wtime
    time.sleep(wtime)


if __name__ == "__main__":
    asyncio.run(main())