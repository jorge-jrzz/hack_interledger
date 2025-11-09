import os

from pywa_async import WhatsApp, filters
from pywa.types import FlowCategory, Message, FlowButton, Button, ChatOpened, CallbackButton, URLButton, SectionList, Section, SectionRow, CallbackSelection
from pywa.types.flows import (
    FlowJSON,
    Screen,
    Layout,
    TextInput,
    InputType,
    OptIn,
    OpenURLAction,
    Footer,
    CompleteAction,
    FlowStatus,
    FlowActionType
)
from dotenv import load_dotenv
from fastapi import FastAPI
# import httpx


load_dotenv()
CALLBACK_URL = "https://4b0ca75fffaf.ngrok-free.app"
fastapi_app = FastAPI()
wa = WhatsApp(
    phone_id=os.getenv('META_PHONE_ID'),
    token=os.getenv('META_ACCESS_TOKEN'),
    server=fastapi_app,
    callback_url=CALLBACK_URL,
    verify_token=os.getenv('META_VERIFY_TOKEN'),
    app_id=os.getenv('META_APP_ID'),
    app_secret=os.getenv('META_APP_SECRET')
)


# llm_client = httpx.AsyncClient()
POPULAR_ACTIONS = {
    "transfer": ("Transfer money to another account", "💸"),
    "tickets": ("Pay for services", "🏦"),
    "check": ("Check transactions", "🥸")
}

POPULAR_LANGUAGES = {
    "en": ("English", "🇺🇸"),
    "es": ("Español", "🇪🇸"),
    "fr": ("Français", "🇫🇷")
}
OTHER_LANGUAGES = {
    "ar": ("العربية", "🇸🇦"),
    "ru": ("Русский", "🇷🇺"),
    "it": ("Italiano", "🇮🇹"),
    "pt": ("Português", "🇵🇹"),
    "ja": ("日本語", "🇯🇵"),
}

@wa.on_message(filters.contains("Hello", "Hi", "Hola", ignore_case=True))
async def hello(_: WhatsApp, msg: Message):
    await msg.react("👋")
    await msg.reply_text(
        text="Hi, I'm *Paguito*. A payment service via WhatsApp. To get started, choose your preferred language.",
        buttons=SectionList(
            button_title='🌐 Choose Language',
            sections=[
                Section(
                    title="🌟 Popular languages",
                    rows=[
                        SectionRow(
                            title=f"{flag} {name}",
                            callback_data=f"language:{code}",
                        )
                        for code, (name, flag) in POPULAR_LANGUAGES.items()
                    ],
                ),
                Section(
                    title="🌐 Other languages",
                    rows=[
                        SectionRow(
                            title=f"{flag} {name}",
                            callback_data=f"language:{code}",
                        )
                        for code, (name, flag) in OTHER_LANGUAGES.items()
                    ],
                ),
            ]
        )
    )

@wa.on_callback_selection(filters.startswith('language:'))
async def select_action(_: WhatsApp, sel: CallbackSelection):
    await sel.reply_text(
        text="Great! Now, please select the action you would like to perform:",
        buttons=[
            Button(
                title="Transfer money 💸",
                callback_data="action:transfer"
            ),
            Button(
                title="Pay for services 🏦",
                callback_data="action:tickets"
            ),
            Button(
                title="Check transactions 🔍",
                callback_data="action:check"
            )
        ]
    )

@wa.on_callback_button(filters.startswith('action:'))
async def perform_action(_: WhatsApp, clb: CallbackButton):
    action = clb.data.split(':')[-1]
    if action == "transfer":
        await clb.reply_text(text="Transfer Action")
    elif action == "tickets":
        await clb.reply_text(text="Pay for services action")
    elif action == "check":
        await clb.reply_text(text="Check transactions action")
    else:
        await clb.reply_text(text="contesta bien tontito")

# @wa.on_callback_button(filters.matches("translate"))
# async def translate(_: WhatsApp, clb: CallbackButton):
#     await clb.reply_text("Please provide the text you want to translate:")

# @wa.on_message
# async def hello(_: WhatsApp, msg: Message):
#     print("Received a message!")
#     print(msg)
#     msg.reply("Hello from Paguito!")
    # if msg.type == "image":
    #     await msg.react("❤️")
    #     await msg.download_media(filepath="downloads/", filename="yopo.jpg")
    #     await msg.reply("Nice image!")
    # elif msg.type == "text":
    #     await msg.react("👋")
    #     print(f"Message from {msg.from_user}: {msg.text} \n Metadata: {msg.metadata} \n ID: {msg.id}")
    #     await msg.reply("Hello from Paguito!")
    #     response = await llm_client.get("http://localhost:8001/chat")
    #     data = response.json()
    #     await msg.reply(f"LLM says: {data['response']}")



# def greeting_filter(_: WhatsApp, msg: Message) -> bool:
#     return msg.text and "Hi" not in msg.text

# @wa.on_message
# async def send_buttons(_: WhatsApp, msg: Message):
#     await msg.reply(
#         text="Hi, You need to finish your sign up!",
#         buttons=[
#             Button(title="Menu", callback_data="menu"),
#             Button(title="Help", callback_data="help")
#         ]
#     )

# @wa.on_message(filters.image & filters.has_caption)
# async def reply_filter(_: WhatsApp, msg: Message):
#     await msg.reply("imagen con caption recibida")

# Register callback to handle incoming messages
# @wa.on_message(filters.matches("Hello", "Hi")) # Filter to match text messages that contain "Hello" or "Hi"
# # @wa.on_message(filters.) # Filter to match text messages that contain "Hello" or "Hi"
# async def hello(client: WhatsApp, msg: Message):
#     await msg.react("👋") # React to the message with a wave emoji
#     await msg.reply_text( # Short reply to the message
#         text=f"Hello {msg.from_user.name}!", # Greet the user
#         buttons=[
#             Button(
#                 title="About me",
#                 callback_data="about_me"
#             )
#         ]
#     )
#     # Use the `wait_for_reply` listener to wait for a reply from the user
#     sent_age_prompt = await msg.reply(text="What's your age?")  # Send the prompt and await the sent message
#     age_reply = await sent_age_prompt.wait_for_reply(timeout=60)  # Wait for a reply for up to 60 seconds
#     await msg.reply_text(f"Your age is {age_reply.text}.")

# # Register another callback to handle incoming button clicks
# @wa.on_callback_button(filters.matches("about_me")) # Filter to match the button click
# async def click_me(client: WhatsApp, clb: CallbackButton):
#     await clb.reply_text(f"Hello {clb.from_user.name}, I am a WhatsApp bot built with PyWa!") # Reply to the button click

# @wa.on_message(filters.matches("link")) # Filter to match text messages that contain "Hello" or "Hi"
# async def link(_: WhatsApp, msg: Message):

#     await msg.reply_text( # Short reply to the message
#         text=f"Hello {msg.from_user.name}!", # Greet the user
#         buttons=URLButton(
#                 title="Open AI Website",
#                 url="https://www.openai.com"
#             )
#     )