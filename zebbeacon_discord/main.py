import discord
import json
import os

import paho.mqtt.publish as publish


DEVICE = os.environ.get('PLUG_DEVICE_ID')
BROKER_HOST = os.environ.get('MQTT_BROKER_HOST')
USER = os.environ.get('MQTT_USER')
PASS = os.environ.get('MQTT_PASS')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
DISCORD_LISTEN_CHANNEL = os.environ.get('DISCORD_LISTEN_CHANNEL')

PAYLOAD = {"id": 0,
           'src': f'shellies/{DEVICE}/rpc',
           'method': 'Switch.Set',
           'params': {'id': 0, 'on': True}}
TOPIC = f'{DEVICE}/rpc'
CLIENT_ID = 'python-mqtt-beacon'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def lamp_on():
    try:
        publish.single(TOPIC,
                       payload=json.dumps(PAYLOAD),
                       hostname=BROKER_HOST,
                       port=8883,
                       client_id=CLIENT_ID,
                       tls={'insecure': True},
                       auth={'username': USER, 'password': PASS},
                       transport="tcp")
        return None
    except Exception as e:
        print(f'Sending MQTT failed, because: {e}')


def print_env():
    print(f'DEVICE: {DEVICE}')
    print(f'BROKER_HOST: {BROKER_HOST}')
    print(f'USER: {USER}')
    print(f'PASS: {PASS}')
    print(f'DISCORD_TOKEN: {DISCORD_TOKEN}')
    print(f'DISCORD_LISTEN_CHANNEL: {DISCORD_LISTEN_CHANNEL}')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        if (message.channel.id == DISCORD_LISTEN_CHANNEL and
           'light' in message.content.lower()):
            print(f'Lamp on from {message.author.username}')
            lamp_on()
            msg = '{} calls for aid!'.format(message.author.nick)
            await message.channel.send(msg)

print_env()  # Debug outputs
client.run(DISCORD_TOKEN)
