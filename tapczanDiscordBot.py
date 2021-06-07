# This example requires the 'members' privileged intents

import discord
from discord.ext import commands
import random
import asyncio
import requests
import base64
import os
import http.client
import json
from decouple import config

description = '''Trackmania-oauth2 bot discord.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!',
                   description=description, intents=intents)

# global variables
variable = 'test'
boolean = True
stop = ''
level2Token = ''
level2RefreshToken = ''

''' Nadeo access tokens:
    Level 0 - uplay access token. Used for: login to trackmania API.
    Level 1 - nadeo access token. Used for: to get access to API endpoints
    Level 2 - nadeo access token. Used for: access to trackmania APIs'''


def level0_uplay_token():
    conn = http.client.HTTPSConnection("public-ubiservices.ubi.com")
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        # 'Basic base64.b64encode(b'email:password').decode()',
        'Authorization': 'Basic ' + config('BASE64_AUTH'),
        # Trackmania ID
        'Ubi-AppId': '86263886-327a-4328-ac69-527f0d20a237'
    }
    conn.request("POST", "/v3/profiles/sessions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")
    response = json.loads(decoded_data)
    return response['ticket']


def level1_nadeo_token(token):
    headers = {
        "Authorization": "ubi_v1 t=" + token
    }
    nadeo_accesstoken = requests.post(
        "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices", headers=headers
    )
    return nadeo_accesstoken.json()


def level2_nadeo_token(token):
    payload = {
        'audience': 'NadeoClubServices'
    }
    headers = {
        "Authorization": "nadeo_v1 t=" + token,
    }
    nadeo_services = requests.post(
        "https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices", headers=headers, data=payload
    )
    return nadeo_services.json()


def get_users_from_oauth2_api():
    url = config('OAUTH2_API_URL')

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


@bot.command()
async def get_token(ctx):
    global level2Token
    global level2RefreshToken
    uplay_token = level0_uplay_token()
    nadeo_API_access_token = level1_nadeo_token(uplay_token)
    nadeo_token = level2_nadeo_token(nadeo_API_access_token['accessToken'])
    level2Token = nadeo_token['accessToken']
    level2RefreshToken = nadeo_token['refreshToken']
    if bool(level2Token):
        await ctx.send('Access token granted')


@bot.command()
async def get_refresh_token(ctx):
    global level2RefreshToken
    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
    headers = {
        'Authorization': 'nadeo_v1 t=' + level2RefreshToken
    }
    while True:
        refresh_token = requests.post(url, headers=headers)
        json_response = refresh_token.json()
        message = json_response
        await ctx.send(message)
        await asyncio.sleep(600)
        if bool(stop):
            await ctx.send('Tomek kazał mi przestać pracowac :(')
            break


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def test5sec(ctx, content='bede spamowac to, co 5 sekund'):
    global stop
    stop = ''
    while True:
        await ctx.send(content)
        await asyncio.sleep(5)
        if bool(stop):
            break


@bot.command()
async def stop_spam(ctx, message):
    global stop
    stop = message


@bot.command()
async def print_global_variable(ctx):
    global variable
    await ctx.send(variable)


@bot.command()
async def print_token(ctx):
    global level2Token
    await ctx.send(level2Token)


@bot.command()
async def print_refresh_token(ctx):
    global level2RefreshToken
    await ctx.send(level2RefreshToken)


@bot.command()
async def change_nickname(ctx, member: discord.Member, nickname):
    await member.edit(nick=nickname)


@bot.command()
async def get_user(ctx, user_id):
    guild = bot.get_guild(config('GUILD_ID'))
    user = bot.get_user(int(user_id))
    member = guild.get_member(int(user_id))
    await ctx.send(user.name)
    await ctx.send(member.name)
    print(type(user))
    print(type(member))


@bot.command(pass_context=True)
# This must be exactly the name of the appropriate role
@commands.has_role("Admin")
async def addrole(ctx):
    member = ctx.message.author
    role = get(member.server.roles, name="Test")
    await bot.add_roles(member, role)


@bot.command()
async def check_rank(ctx, id):
    url = "https://matchmaking.trackmania.nadeo.club/api/matchmaking/2/leaderboard/players?players[]=" + id

    payload = {}
    headers = {
        'Authorization': 'nadeo_v1 t=' + level2Token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    resp = response.json()
    rank = resp['results'][0]['rank']
    score = resp['results'][0]['score']
    context = " - " + str(score)
    await ctx.send(context)


@bot.command()
async def set_nick_and_roles(ctx):
    guild = bot.get_guild(config('GUILD_ID'))
    response = get_users_from_oauth2_api()
    response = json.loads(response.text)

    if response:
        for user in response:
            if user['linked_discord'] == config('SKIP_ID'):
                print('I was here', user['linked_discord'])
                continue
            member = guild.get_member(user['linked_discord'])
            if member:
                await member.edit(nick=str(user['display_name']))


bot.run(config('BOT_SECRET_KEY'))
