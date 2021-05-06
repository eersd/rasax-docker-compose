import logging
import warnings
import uuid
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from socketio import AsyncServer
from typing import Optional, Text, Any, List, Dict, Iterable, Callable, Awaitable
import time
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage, OutputChannel

logger = logging.getLogger(__name__)


class SocketBlueprint(Blueprint):
    def __init__(self, sio: AsyncServer, socketio_path, *args, **kwargs):
        self.sio = sio
        self.socketio_path = socketio_path
        super().__init__(*args, **kwargs)

    def register(self, app, options):
        self.sio.attach(app, self.socketio_path)
        super().register(app, options)


class SocketIOOutput(OutputChannel):
    @classmethod
    def name(cls):
        return "socketio"

    def __init__(self, sio, sid, bot_message_evt):
        self.sio = sio
        self.sid = sid
        self.bot_message_evt = bot_message_evt

    async def _send_message(self, socket_id: Text, response: Any) -> None:
        """Sends a message to the recipient using the bot event."""
        await self.sio.emit(self.bot_message_evt, response, room=socket_id)
        time.sleep(response["delay"])

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send a message through this channel."""
        message = {"text": text, "delay": 2, "allowTyping": True}
        #await self.send_custom_json(recipient_id, message)
        if (text):
            await self._send_message(self.sid, message)

    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image to the output"""

        message = {"attachment": {"type": "image", "payload": {"src": image}}}
        await self._send_message(self.sid, message)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""

        message = {"text": text, "quick_replies": [], "delay": 0}

        for button in buttons:
            message["quick_replies"].append(
                {
                    "content_type": "text",
                    "title": button["title"],
                    "payload": button["payload"],
                }
            )
        

        await self._send_message(self.sid, message)

    async def send_elements(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Sends elements to the output."""

        for element in elements:
            message = {
                "attachment": {
                    "type": "template",
                    "payload": {"template_type": "generic", "elements": element},
                }
            }

            await self._send_message(self.sid, message)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends custom json to the output"""
        try:
            json_message.setdefault("room", self.sid)
            json_message.setdefault("text", "")
            json_message.setdefault("type", "text")
            json_message.setdefault("items", [])
            json_message.setdefault("links", [])
            json_message.setdefault("buttons",[])
            json_message.setdefault("delay", 0)
            json_message.setdefault("img", "")
            json_message.setdefault("video", "")
            json_message.setdefault("contact", False)
            json_message.setdefault("withGoBack", False)
            json_message.setdefault("feedback", False)
            json_message.setdefault("allowTyping", True)
            json_message.setdefault("sphereTextContent", "")
            json_message.setdefault("sphereImageContent", "")
            json_message.setdefault("sphereColor", "")
            json_message.setdefault("backgroundImage", "")
            json_message.setdefault("lottieImage", "")
            json_message.setdefault("dateSelection", False)
            json_message.setdefault("dateInput", "")
            json_message.setdefault("inputContact", "")
            json_message.setdefault("timer", "")
            json_message.setdefault("submitForm", False)
            json_message.setdefault("quote", {})
            json_message.setdefault("compare", False)
            json_message.setdefault("modal", {})
            json_message.setdefault("slider", {})
            json_message.setdefault("interval", [])
            json_message.setdefault("intro", {})
            json_message.setdefault("subtitle", "")

            message = {
                "text":json_message["text"],
                "delay":json_message["delay"],
                "links": [], "quick_replies": [],
                "contact": json_message["contact"],
                "img": json_message["img"],
                "video": json_message["video"],
                "withGoBack": json_message["withGoBack"],
                "allowTyping": json_message["allowTyping"],
                "feedback": json_message["feedback"],
                "type": json_message["type"],
                "items": json_message["items"],
                "sphereTextContent": json_message["sphereTextContent"],
                "sphereImageContent": json_message["sphereImageContent"],
                "sphereColor": json_message["sphereColor"],
                "backgroundImage": json_message["backgroundImage"],
                "lottieImage": json_message["lottieImage"],
                "dateSelection": json_message["dateSelection"],
                "dateInput": json_message["dateInput"],
                "inputContact": json_message["inputContact"],
                "submitForm": json_message["submitForm"],
                "timer": json_message["timer"],
                "compare": json_message["compare"],
                "interval": json_message["interval"],
                "subtitle": json_message["subtitle"],
                }

            modal = json_message["modal"][0] if len(json_message["modal"]) > 0  else None
            if (modal is not None):
                message["modal"] = {
                    "title": modal["title"],
                    "img": modal["img"],
                    "subtitle": modal["subtitle"],
                }

            intro = json_message["intro"][0] if len(json_message["intro"]) > 0  else None
            if (intro is not None):
                message["intro"] = {
                    "text": intro["text"],
                    "img": intro["img"],
                    "subtitle": intro["subtitle"],
                }
            
            slider = json_message["slider"][0] if len(json_message["slider"]) > 0  else None
            if (slider is not None):
                message["slider"] = {
                    "min": slider["min"],
                    "max": slider["max"],
                    "interval": slider["interval"],
                    "unit": slider["unit"],
                    "mode": slider["mode"],
                    "solution": slider["solution"],
                    "solution_min": slider["solution_min"],
                    "solution_max": slider["solution_max"],
                }
            
            quote = json_message["quote"][0] if len(json_message["quote"]) > 0  else None
            if (quote is not None):
                message["quote"] = {
                    "quotetext": quote["quotetext"],
                    "quoteimage": quote["quoteimage"],
                    "author": quote["author"],
                    "subtitle": quote["subtitle"],
                }
            
            for link in json_message["links"]:
                message["links"].append({
                        "content_type": link["type"] if "type" in link else "link",
                        "title": link["title"],
                        "description": link["description"] if "description" in link else "",
                        "payload": link["payload"]
                    })

            for button in json_message["buttons"]:
                message["quick_replies"].append(
                    {
                        "content_type": "text",
                        "title": button["title"],
                        "payload": button["payload"],
                    }
                )

            await self._send_message(self.sid, message)

        except Exception as err:
            print(err)

    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends an attachment to the user."""
        await self._send_message(self.sid, {"attachment": attachment})


class SocketIOInput(InputChannel):
    """A socket.io input channel."""

    @classmethod
    def name(cls) -> Text:
        return "socketio"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        credentials = credentials or {}
        return cls(
            credentials.get("user_message_evt", "user_uttered"),
            credentials.get("bot_message_evt", "bot_uttered"),
            credentials.get("namespace"),
            credentials.get("session_persistence", False),
            credentials.get("socketio_path", "/socket.io"),
        )

    def __init__(
        self,
        user_message_evt: Text = "user_uttered",
        bot_message_evt: Text = "bot_uttered",
        namespace: Optional[Text] = None,
        session_persistence: bool = False,
        socketio_path: Optional[Text] = "/socket.io",
    ):
        self.bot_message_evt = bot_message_evt
        self.session_persistence = session_persistence
        self.user_message_evt = user_message_evt
        self.namespace = namespace
        self.socketio_path = socketio_path

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        # Workaround so that socketio works with requests from other origins.
        # https://github.com/miguelgrinberg/python-socketio/issues/205#issuecomment-493769183
        sio = AsyncServer(async_mode="sanic", cors_allowed_origins="*")
        socketio_webhook = SocketBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        @socketio_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @sio.on("connect", namespace=self.namespace)
        async def connect(sid: Text, _) -> None:
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.on("disconnect", namespace=self.namespace)
        async def disconnect(sid: Text) -> None:
            logger.debug(f"User {sid} disconnected from socketIO endpoint.")

        @sio.on("session_request", namespace=self.namespace)
        async def session_request(sid: Text, data: Optional[Dict]):
            if data is None:
                data = {}
            if "session_id" not in data or data["session_id"] is None:
                data["session_id"] = uuid.uuid4().hex
            await sio.emit("session_confirm", data["session_id"], room=sid)
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.on(self.user_message_evt, namespace=self.namespace)
        async def handle_message(sid: Text, data: Dict) -> Any:
            output_channel = SocketIOOutput(sio, sid, self.bot_message_evt)

            if self.session_persistence:
                if not data.get("session_id"):
                    warnings.warn(
                        "A message without a valid sender_id "
                        "was received. This message will be "
                        "ignored. Make sure to set a proper "
                        "session id using the "
                        "`session_request` socketIO event."
                    )
                    return
                sender_id = data["session_id"]
            else:
                sender_id = sid

            message = UserMessage(
                data["message"], output_channel, sender_id, input_channel=self.name()
            )
            await on_new_message(message)

        return socketio_webhook