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
from webserver import keep_alive
import math
from collections import defaultdict

MAX_IDS_PER_REQUEST = 150

description = '''Trackmania-oauth2 bot discord.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!',
                   description=description, intents=intents)

# URLs

url_matchmaking = "https://matchmaking.trackmania.nadeo.club/api/matchmaking/2/leaderboard/players?players[]="

bot.loop_active = True

OAUTH2_API_URL = os.environ['OAUTH2_API_URL']


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
    await nick_and_roles()


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
    guild = bot.get_guild(ctx.message.guild.id)
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
async def set_nick_and_roles(ctx):
    await nick_and_roles()


async def nick_and_roles():
    guild_id = int(os.environ['GUILD_ID'])
    guild = bot.get_guild(guild_id)

    api = trackmaniaAPI.TmApi()
    api.get_tickets()

    channel = bot.get_channel(854002990112571422)
    await channel.send("""Logged in, starting to work""")

    while bot.loop_active:
        if not(api.ticket):
            api.get_tickets()
        else:
            api.get_new_refresh_ticket()

        mm_api_dict = get_users_from_oauth2_api()
        mm_api_dict = json.loads(mm_api_dict.text)
        trackmania_api_dict = do_requests(mm_api_dict, api)
        final_dict = merge_dicts_from_apis(trackmania_api_dict, mm_api_dict)

        for user in final_dict:
            member = guild.get_member(user['linked_discord'])
            if member:
                try:
                    print(user['account_id'])
                    score = user['score']
                    print("Score:", score)
                    rank = user['rank']
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
                try:
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
                except:
                    print("Cannot add role")
        await asyncio.sleep(300)
    await channel.send("The command has been stopped.")


def get_users_from_oauth2_api():
    url = OAUTH2_API_URL

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


def do_requests(data, api):
    requests_list = do_lists_max_150_ids_per(data)
    list_of_api_elements = []
    print(type(list_of_api_elements))
    for list_of_ids in requests_list:
        request_arg = ''
        for player_id in list_of_ids:
            request_arg += 'players[]=' + str(player_id) + '&'
        request_dict = api.get_players_info(request_arg)
        list_of_api_elements += request_dict['results']
    return list_of_api_elements


def do_lists_max_150_ids_per(data):
    requests_list = how_many_requests_list(data)
    i = 0
    for element in data:
        if len(requests_list[i]) < MAX_IDS_PER_REQUEST:
            requests_list[i].append(element['account_id'])
        else:
            i += 1
            requests_list[i].append(element['account_id'])
    return requests_list


def how_many_requests_list(data):
    size_of_requests_list = int(math.ceil(len(data) / MAX_IDS_PER_REQUEST))
    requests_list = [[] for _ in range(size_of_requests_list)]
    print(requests_list)
    return requests_list


def merge_dicts_from_apis(trackmania_api_dict, mm_api_dict):
    for element in mm_api_dict:
        element['player'] = element.pop('account_id')
    final_dict = defaultdict(dict)
    for element in (trackmania_api_dict, mm_api_dict):
        for e in element:
            final_dict[e['player']].update(e)
    return final_dict.values()


@bot.command()
async def get_guild_token(ctx):
    await ctx.send(ctx.message.guild.id)

keep_alive()
bot.run(os.environ['BOT_SECRET_KEY'])
