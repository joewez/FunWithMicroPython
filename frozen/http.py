#
# Simple HTTP server based on the uasyncio example script
# by J.G. Wezensky (joewez@gmail.com)
#

import uasyncio
import uos
import network
#import logging

webroot = '/wwwroot'

# Breaks an HTTP request into its parts and boils it down to a physical file (if possible)
def decode_path(req):
    global webroot
    cmd, headers = req.decode("utf-8").split('\r\n', 1)
    parts = cmd.split(' ')
    method, path = parts[0], parts[1]
    # remove any query string
    query = ''
    r = path.find('?')
    if r > 0:
        query = path[r:]
        path = path[:r]
    # check for use of default document
    if path == '/':
        path = 'index.html'
    else:
        path = path[1:].replace('%20', ' ')
    # return the physical path of the response file
    return webroot + '/' + path

mime_types = {
    "html": "text/html",
    "css": "text/css",
    "js": "text/javascript",
    "png": "image/png",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "pdf": "application/pdf",
    "ico": "image/x-icon"
}

# Looks up the content-type based on the file extension
def get_mime_type(file):
    mime = "text/plain"
    cache = False
    extention = file.split(".")[-1]
    if extention in mime_types:
        mime = mime_types[extention]
        cache = (extention != "html")
    return mime, cache

# Quick check if a file exists
def exists(file):
    try:
        s = uos.stat(file)
        return True
    except:
        return False    

def get_address():
    addr = ""
    wlan = network.WLAN(network.STA_IF)
    if wlan.active():
        addr = wlan.ifconfig()[0]
    else:
        wlan = network.WLAN(network.AP_IF)
        if wlan.active():
            addr = wlan.ifconfig()[0]
    return addr

@uasyncio.coroutine
def serve_content(reader, writer):
    #log = logging.getLogger("uasyncio")
    try:
        file = decode_path((yield from reader.read()))
        #print("File Requested: " + file)
        if exists(file):
            mime_type, cacheable = get_mime_type(file)
            yield from writer.awrite("HTTP/1.0 200 OK\r\n")
            yield from writer.awrite("Content-Type: {}\r\n".format(mime_type))
            if cacheable:
                yield from writer.awrite("Cache-Control: max-age=86400\r\n")
            yield from writer.awrite("\r\n")

            buffer = bytearray(512)
            f = open(file, "rb")
            count = f.readinto(buffer)
            while count > 0:
                yield from writer.awrite(buffer, off=0, sz=count)
                count = f.readinto(buffer)
            f.close()
        else:
            yield from writer.awrite("HTTP/1.0 404 NA\r\n\r\n")
    except:
        #log.error("Exception in serve_content()")
        raise
    finally:
        yield from writer.aclose()

@uasyncio.coroutine
def heartbeat(wdt, led):
    while True:
        wdt.feed()
        led.value(not led.value())
        await uasyncio.sleep_ms(250)

def httpserver(fromcard = False, rootpath = '', watchdog = False):
    global webroot
    #logging.basicConfig(level=logging.ERROR)

    addr = get_address()

    if fromcard:
        from shields import microsd_shield
        sdcard = microsd_shield.MicroSD_Shield()
        sdcard.mount()
        webroot = '/sd/wwwroot'

    if rootpath:
        webroot = rootpath

    #uasyncio.set_debug(1)
    loop = uasyncio.get_event_loop()

    loop.create_task(uasyncio.start_server(serve_content, addr, 80, 20))

    if watchdog:
        from machine import Pin, WDT
        wdt = WDT()
        wdt.feed()
        led = Pin(2, Pin.OUT)
        loop.create_task(heartbeat(wdt, led))
    
    loop.run_forever()
    loop.close()

    if fromcard:
        sdcard.unmount()

#httpserver()