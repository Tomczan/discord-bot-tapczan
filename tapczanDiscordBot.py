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


async def remove_old_roles(guild, member, id):
    roles_id_list = [851584115665141780, 843466461547593748, 843466786489499659,
                     843466934623928330, 843466667308089344, 843467019575885824,
                     843467061564145685, 843467109229002773, 843467151277031426,
                     843467389282287648, 851583674196819968, 851583682132181022,
                     851583859559628801, 843467443242270740]
    roles_id_list.remove(id)
    member_roles = member.roles
    member_roles_id = []
    for role in member_roles:
        member_roles_id.append(role.id)

    roles_to_delete = set(member_roles_id) & set(roles_id_list)

    for role_id in roles_to_delete:
        await member.remove_roles(guild.get_role(role_id))


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
                member = guild.get_member(user['linked_discord'])
                if member:
                    try:
                        print(user['account_id'])
                        player_info = api.get_player_info(user['account_id'])
                        print(player_info)
                        score = player_info['results'][0]['score']
                        print("Score:", score)
                        rank = player_info['results'][0]['rank']
                        print("Rank:", rank)
                    except:
                        score = 0
                        rank = 101
                    try:
                        await member.edit(nick=str(user['display_name']) + ' - ' + str(score))
                    except discord.errors.Forbidden:
                        continue

                    # TOP 100
                    if rank <= 100:
                        await member.add_roles(guild.get_role(851589599871762433))
                    else:
                        try:
                            await member.remove_roles(guild.get_role(851589599871762433))
                        except:
                            print("Member was not in top 100")
                    # Bronze 1
                    if 1 <= score <= 299:
                        await remove_old_roles(guild, member, 843466461547593748)
                        await member.add_roles(guild.get_role(843466461547593748))
                    # Bronze 2
                    elif 300 <= score <= 599:
                        await remove_old_roles(guild, member, 843466786489499659)
                        await member.add_roles(guild.get_role(843466786489499659))
                    # Bronze 3
                    elif 600 <= score <= 999:
                        await remove_old_roles(guild, member, 843466934623928330)
                        await member.add_roles(guild.get_role(843466934623928330))
                    # Silver 1
                    elif 1000 <= score <= 1299:
                        await remove_old_roles(guild, member, 843466667308089344)
                        await member.add_roles(guild.get_role(843466667308089344))
                    # Silver 2
                    elif 1300 <= score <= 1599:
                        await remove_old_roles(guild, member, 843467019575885824)
                        await member.add_roles(guild.get_role(843467019575885824))
                    # Silver 3
                    elif 1600 <= score <= 1999:
                        await remove_old_roles(guild, member, 843467061564145685)
                        await member.add_roles(guild.get_role(843467061564145685))
                    # Gold 1
                    elif 2000 <= score <= 2299:
                        await remove_old_roles(guild, member, 843467109229002773)
                        await member.add_roles(guild.get_role(843467109229002773))
                    # Gold 2
                    elif 2300 <= score <= 2599:
                        await remove_old_roles(guild, member, 843467151277031426)
                        await member.add_roles(guild.get_role(843467151277031426))
                    # Gold 3
                    elif 2600 <= score <= 2999:
                        await remove_old_roles(guild, member, 843467389282287648)
                        await member.add_roles(guild.get_role(843467389282287648))
                    # Master 1
                    elif 3000 <= score <= 3299:
                        await remove_old_roles(guild, member, 851583674196819968)
                        await member.add_roles(guild.get_role(851583674196819968))
                    # Master 2
                    elif 3300 <= score <= 3599:
                        await remove_old_roles(guild, member, 851583682132181022)
                        await member.add_roles(guild.get_role(851583682132181022))
                    # Master 3
                    elif 3600 <= score <= 3999:
                        await remove_old_roles(guild, member, 851583859559628801)
                        await member.add_roles(guild.get_role(851583859559628801))
                    # Trackmaster
                    elif 4000 <= score:
                        await remove_old_roles(guild, member, 843467443242270740)
                        await member.add_roles(guild.get_role(843467443242270740))
                    else:
                        # Unranked
                        await remove_old_roles(guild, member, 851584115665141780)
                        await member.add_roles(guild.get_role(851584115665141780))

        await asyncio.sleep(300)
    await ctx.send("The command has been stopped.")


@bot.command()
async def get_guild_token(ctx):
    await ctx.send(ctx.message.guild.id)


bot.run(config('BOT_SECRET_KEY'))
