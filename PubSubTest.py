import asyncio

import aiohttp
import nest_asyncio
from aiohttp import web
from bs4 import BeautifulSoup as bs
from pyngrok import ngrok

nest_asyncio.apply()

link = "https://pubsubhubbub.appspot.com/"

class PubSub():
    def __init__(self, port: int, subs: list, loop: asyncio.AbstractEventLoop) -> None:
        self.subs = subs
        asyncio.set_event_loop(loop)
        self.loop = asyncio.get_event_loop()
        self.application = web.Application()
        self.tunnel = ngrok.connect(port) # Will open the localhost to the public web
        self.port = port

    async def start_app(self): # Starts the app
        self.session = aiohttp.ClientSession(loop=self.loop)
        print(self.tunnel.public_url)
        self.application.router.add_get("/", self.handle_sub)
        self.application.router.add_post("/", self.handle_pub)
        self.application.on_shutdown.append(self.shutdown)
        self.application.on_startup.append(self.on_startup)
        web.run_app(self.application, port=self.port, loop=self.loop) # Runs the localhost

    async def on_startup(self, _):
        print("Starting")
        for sub in self.subs:
            await self.subscribe(sub)

    async def shutdown(self, _):
        print("Shutting down")
        for sub in self.subs:
            await self.unsubscribe(sub)
        print("Done")

    async def handle_sub(self, request: aiohttp.web.BaseRequest): # This will activate when we try to subscribe
        print("Sub")
        print(request)
        print(request.query)
        resp = web.StreamResponse()
        resp.status_code = 200
        await resp.prepare(request)
        msg = request.query.get('hub.challenge', '') # A security challenge that we have to return
        print(msg)
        await resp.write(bytes(msg, 'utf-8'))
        return resp

    async def handle_pub(self, request: aiohttp.web.BaseRequest): # This will run when a YouTube video gets published that the app is subbed to
        print("pub")
        resp = web.StreamResponse() # creates the response
        resp.status_code = 200 # makes the status code as 200: OK
        await resp.prepare(request)
        print(request.url)
        text = await request.text() #gets the html text
        soup = bs(text, "lxml-xml")
        if "https://pubsubhubbub.appspot.com" != soup.find("link")['href']: # Security stuff
            print(f"Misinformation recieved:\n***\n{text}\n***\b")
            resp.status_code = 406 # changes the status code to 406: Not Acceptable
            return resp
        entry = (soup.find("feed")).find("entry") # Goes into the entry class 
        channel_id = entry.find("yt:channelId") # ID of the channel
        print(channel_id.text)
        video_id = entry.find("yt:videoId") # ID of the video
        print(video_id.text)
        title = entry.find("title") # Title of the video
        print(title.text)
        link = entry.find("link") # Link to the video
        print(link['href'])
        author = entry.find("author")
        print(author.find("name").text) # Name of the YT channel
        print(author.find("uri").text) # URL to the YT channel
        return resp

    async def subscribe(self, url): 
        print(f"Subbing to {url}")
        headers = {
            'hub.callback': self.tunnel.public_url,
            'hub.mode': "subscribe",
            'hub.topic': url,
            'hub.verify': 'async'
        }
        res = await self.session.post(link, data=headers) # Tells pubsubhubbub to send us notifcations
        print(res.ok)
    
    async def unsubscribe(self, url):
        print(f"Unsubbing to {url}")
        headers = {
            'hub.callback': self.tunnel.public_url,
            'hub.mode': "unsubscribe",
            'hub.topic': url,
            'hub.verify': 'async'
        }
        res = await self.session.post(link, data=headers) # Tells pubsubhubbub to stop sending us notifcations
        print(res.ok)

loop = asyncio.get_event_loop()
subs = ["https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCuyLAsq7sOBrARgGnGJbNgw"]
pubsub = PubSub(4040, subs, loop)
asyncio.run(pubsub.start_app())