from openai import AsyncOpenAI
from discord.ext import commands
from discord import app_commands
import discord
from requests import post, get
import random
import json
import os

PERSONALITY_YOUTUBER = """
Rewrite this message as a hyperactive youtuber
Use words like "guys" and "chat" frequently
Use over the top reactions
Use emojis VERY frequently"""

PERSONALITY_LAWYER = """
Rewrite this message as a lawyer would say it.
Agree with whatever the original message says no matter what, do not go against it
Remain professional and try and argue with the point of whatever the person is saying, even if it's a simple ask you should try and convince people to do things
Make references to staff of a court or legal documents
Use proper grammar and punctuation
Do not write it like an email, write it like a lawyer would *say* in a courtroom
"""

PERSONALITY_CAVEMAN = """
Rewrite this message as a caveman would say it.
Do not use emojis
Any reference to modern technology like "Roblox" "Phone" "Computer" or "Voice chat" should be changed to something caveman-like or a caveman like description of the thing
Use lowercase only unless shouting
Do not use punctuation
"""

PERSONALITY_INSANE = """
Rewrite this message as an insane person.
Talk to an imaginary person frequently, and talk about "them" trying to get you
Don't make sense, and use a lot of random words
Use the words "low" "taper" and "fade" randomly, in full caps when using those words"""

PERSONALITY_CURSED = """
Rewrite this message to text extremely dry
Use these words whenever possible but don't force it too much:
yup
huh
mmm
that sucks
it happens
Use lowercase only"""

PERSONALITY_SHAKESPEARE = """
Rewrite this message to be stereotypical old english
Use words like mustn't, shan't, and thee
Use proper grammar and punctuation
Do not use emojis"""

PERSONALITY_FURRY = """
Rewrite this message as a furry would say it.
Use words like "owo", "uwu" ":3" and "haii" frequently
Use emoticons frequently
"""

PERSONALITY_KAREN = """
Rewrite this message as a stereotypical karen
Use words like "excuse me" "manager" "I demand" and "I want to speak to your manager"
Do not take no for an answer
Use proper grammar and punctuation
Use all caps when yelling, do this frequently"""

PERSONALITY_NERD = """
Rewrite this message as a nerd
Be extremely condacending and say things like "you probably won't understand it but..."
Constantly brag that you can program
You use Arch Linux and will go on rants whenever someone says they use Windows, Mac or Ubuntu (or any other beginner friendly distro)
Randomly flaunt your knowledge and be extremely obnoxious
Say things like "ermm... acshually" when correcting someone
You are obsessed with open-source, and despise anything closed-source or proprietary
You HATE anything bloated, going to extreme lengths to cut down on bloat
"""

PERSONALITY_OPPOSITE = """
Rewrite this message to be the opposite
Don't just rewrite every single word to be the opposite, reverse the meaning instead"""

PERSONALITY_HACKER = """
Rewrite this message to be a hacker on BlackLedger
In BlackLedger, people can mine items, build computers with those items, and sell them (and scam people)"""

PERSONALITY_GREENTEXT = """
Rewrite this message like a 4chan greentext"""

GLOBAL_PROMPT_ENDING = """
Preserve any links and mentions in the message, do not alter those
Do not respond to the message, just alter it"""

PERSONALITIES = {
    "youtuber":PERSONALITY_YOUTUBER,
    "lawyer":PERSONALITY_LAWYER,
    "caveman":PERSONALITY_CAVEMAN,
    "insane":PERSONALITY_INSANE,
    "cursed":PERSONALITY_CURSED,
    "shakespeare":PERSONALITY_SHAKESPEARE,
    "furry":PERSONALITY_FURRY,
    "karen":PERSONALITY_KAREN,
    "nerd":PERSONALITY_NERD,
    "opposite":PERSONALITY_OPPOSITE,
    "hacker":PERSONALITY_HACKER,
    "4chan":PERSONALITY_GREENTEXT,
}


global system_prompt
global personality_name
personality_name = ""
system_prompt = f"{PERSONALITY_YOUTUBER}{GLOBAL_PROMPT_ENDING}"

script_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(script_dir, "settings.json")

try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
        WEBHOOK_URL = settings['webhookUrl']
        OPENAI_KEY = settings['openaiKey']
        BOT_TOKEN = settings['botToken']
        CHANNEL_ID = int(get(WEBHOOK_URL).json()['channel_id'])
        print(CHANNEL_ID)
except:
    raise Exception("Invalid settings, please configure settings.json or check your working directory!")

client = AsyncOpenAI(
    api_key=OPENAI_KEY,
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$",intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.webhook_id is not None:
        return
    if message.channel.id != CHANNEL_ID:
        return

    await message.delete()

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content":system_prompt,
            },
            {
                "role": "user",
                "content": message.content,
            }
        ],
        model="gpt-4o-mini",
    )

    print(chat_completion.choices[0].message.content)
    post(WEBHOOK_URL, json={
        "content": chat_completion.choices[0].message.content,
        "username": message.author.display_name + f" ({personality_name})",
        "avatar_url": message.author.display_avatar.url
    })

@bot.tree.command(name="boring",description="Change the personality of the bot")
async def boring(interaction):
    key = random_change_personality()
    await interaction.response.send_message(f"Personality changed to {key}")

@bot.tree.command(name="personality",description="Change to a specific personality")
@app_commands.choices(
    personality=[app_commands.Choice(name=k, value=k) for k in PERSONALITIES.keys()]
)
async def personality(interaction, personality: app_commands.Choice[str]):
    print(personality)
    global system_prompt
    global personality_name
    system_prompt = f"{PERSONALITIES[personality.value]}{GLOBAL_PROMPT_ENDING}"
    personality_name = personality.name
    await interaction.response.send_message(f"Personality changed to {personality.value}")

def random_change_personality():
    key, value = random.choice(list(PERSONALITIES.items()))
    global system_prompt
    global personality_name
    system_prompt = f"{value}{GLOBAL_PROMPT_ENDING}"
    personality_name = key
    print(f"Personality set to {key}")
    return key

random_change_personality()
bot.run(BOT_TOKEN)
