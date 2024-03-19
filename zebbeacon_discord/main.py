import discord
import logging
import json
import os

import paho.mqtt.publish as publish

logging.basicConfig(level=logging.DEBUG)

DEVICE = os.environ.get('PLUG_DEVICE_ID')
BROKER_HOST = os.environ.get('MQTT_BROKER_HOST')
USER = os.environ.get('MQTT_USER')
PASS = os.environ.get('MQTT_PASS')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
DISCORD_LISTEN_CHANNEL = int(os.environ.get('DISCORD_LISTEN_CHANNEL'))

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
        logging.error(f'Sending MQTT failed, because: {e}')


def print_env():
    logging.info(f'DEVICE: {DEVICE}')
    logging.info(f'BROKER_HOST: {BROKER_HOST}')
    logging.info(f'USER: {USER}')
    logging.info(f'PASS: {PASS}')
    logging.info(f'DISCORD_TOKEN: {DISCORD_TOKEN}')
    logging.info(f'DISCORD_LISTEN_CHANNEL: {DISCORD_LISTEN_CHANNEL}')


@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        if (message.channel.id == DISCORD_LISTEN_CHANNEL and
           'light' in message.content.lower()):
            if message.author.nick:
                caller = message.author.nick
            else:
                caller = message.author.name
            logging.info(f'Lamp on from {message.author.name}')
            lamp_on()
            msg = f'{caller} calls for aid!'
            await message.channel.send(msg)

print_env()  # Debug outputs
client.run(DISCORD_TOKEN)
