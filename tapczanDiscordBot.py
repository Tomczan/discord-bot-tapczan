import discord
from discord.ext import commands
import random
import asyncio
import requests
import base64
import os
import http.client
import json
import trackmaniaAPI
from decouple import config

description = '''Trackmania-oauth2 bot discord.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!',
                   description=description, intents=intents)

# URLs

url_matchmaking = "https://matchmaking.trackmania.nadeo.club/api/matchmaking/2/leaderboard/players?players[]="

bot.loop_active = True


def get_users_from_oauth2_api():
    url = config('OAUTH2_API_URL')

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


@bot.command()
async def get_token(ctx):
    get_token = trackmaniaAPI.TmApi()
    tickets = get_token.get_tickets()
    await ctx.send(tickets)


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
async def start_loop(ctx):
    bot.loop_active = True


@bot.command()
async def stop_loop(ctx):
    bot.loop_active = False


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
    url = url_matchmaking + id

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
    guild = bot.get_guild(ctx.message.guild.id)

    api = trackmaniaAPI.TmApi()
    api.get_tickets()

    print(type(config('GUILD_ID')))
    print(api.ticket)

    while bot.loop_active:
        if not(api.ticket):
            api.get_tickets()
        else:
            api.get_new_refresh_ticket()

        response_oauth2 = get_users_from_oauth2_api()
        response_oauth2 = json.loads(response_oauth2.text)
        if response_oauth2:
            for user in response_oauth2:
                if user['linked_discord'] == int(config('SKIP_ID')):
                    print('I was here', user['linked_discord'])
                    continue
                member = guild.get_member(user['linked_discord'])
                if member:
                    try:
                        print(user['account_id'])
                        player_info = api.get_player_info(user['account_id'])
                        print(player_info)
                        score = player_info['results'][0]['score']
                        print(score)
                    except:
                        score = 0
                    if score > 3000:
                        await member.add_roles(guild.get_role(851579810874261587))
                    else:
                        await member.add_roles(guild.get_role(851579865579651092))
                    await member.edit(nick=str(user['display_name']) + ' - ' + str(score))
        await ctx.send("Ill wait 30sec")
        await asyncio.sleep(30)
    await ctx.send("While loop stopped")


@bot.command()
async def get_guild_token(ctx):
    await ctx.send(ctx.message.guild.id)


bot.run(config('BOT_SECRET_KEY'))
