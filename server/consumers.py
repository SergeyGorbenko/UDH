import json
from utils.logger import log
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from server.models import Object


class MapConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        log.info(event)

        self.chat_room = 'public'
        await self.channel_layer.group_add(
            self.chat_room,
            self.channel_name
        )
        log.debug("add channel layer")

        await self.send({
            "type": "websocket.accept"
        })
        log.debug("websocket.accept")

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(
                {
                    "data": list(Object.objects.all().values('lat', 'lng', 'symbolCode'))
                })
        })
        log.debug(f"websocket.send data from db, {Object.objects.count()} object(s)")

    async def websocket_receive(self, event):
        log.info(event['type'])

        text = event.get('text', None)
        if text is not None:
            json_data = json.loads(text)
            log.debug(json_data['type'] + ' object')
            if json_data['type'] == 'add':
                await self.add_object(json_data['symbol'])
            elif json_data['type'] == 'delete':
                await self.del_object(json_data['symbol'])
            elif json_data['type'] == 'position':
                await self.move_object(json_data['symbol'])

            response = {"data": list([json_data])}

            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": response
                }
            )

    async def chat_message(self, event):

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event['text'])
        })

    async def websocket_disconnect(self, event):
        log.info(event)

    @database_sync_to_async
    def add_object(self, text):
        try:
            Object.objects.create(lat=text['lat'], lng=text['lng'], symbolCode=text['symbolCode'])
            log.info("add to db")
        except Exception as e:
            log.error(e)

    @database_sync_to_async
    def del_object(self, text):
        try:
            Object.objects.get(lat=text['lat'], lng=text['lng'], symbolCode=text['symbolCode']).delete()
            log.info("delete from db: ")
        except Exception as e:
            log.error(e)

    @database_sync_to_async
    def move_object(self, text):
        try:
            o = Object.objects.get(lat=text['lat'], lng=text['lng'])
            o.lat = text['newLat']
            o.lng = text['newLng']
            o.save()
            log.info("move in db: ")
        except Exception as e:
            log.error(e)
