import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            # JSON 파싱
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "")

            # 응답 전송
            await self.send(text_data=json.dumps({"message": message, "status": "received"}))
        except Exception as e:
            # 에러 발생 시 에러 메시지 전송
            await self.send(text_data=json.dumps({"error": str(e), "status": "error"}))
