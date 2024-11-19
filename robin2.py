import discord
from discord.ext import tasks
from dqx_ise import getTable
from datetime import datetime as dt, timedelta as delta
from AutoPartyFormation240616 import AutoPartyFormation as Formation
from typing import Union

# インテント
intents = discord.Intents.all()
intents.message_content = True 
client = discord.Client(intents=intents)

class Guild:
    class RoleEmoji: # id:int あいでぃー emoji:discord.Emoji ロールの絵文字
        id:int = None
        emoji:discord.Emoji = None
        def __init__(self, id:int) -> None:
            self.id = id
        def set_emoji(self, emoji:discord.Emoji):
            self.emoji = emoji

    # class ServerRole:
    #     id:int = None
    #     role:discord.Role = None
    #     def __init__(self, id:int) -> None:
    #         self.id = id
    #     def set_role(self, role:discord.Role):
    #         self.role = role

    def __init__(self, guild):
        self.GUILD = client.get_guild(guild) # ギルド
        self.LIGHT_FORMATION:dict[discord.Emoji, int] = {} # ライトパーティ編成枠
        self.FULL_FORMATION:dict[discord.Emoji, int] = {} # フルパーティ編成枠
        self.TRANCE_FORMATION:dict[discord.Emoji, discord.Emoji] = {} # 職変換
        self.DEV_CH:discord.TextChannel = None # デベロッパーチャンネル
        self.PARTY_CH:discord.TextChannel = None # 募集チャンネル
        self.COMMAND_CH:discord.TextChannel = None # コマンドチャンネル

        self.reclutingMessage:discord.Message = None # 募集メッセージ
        self.reclutingMessageTemplate:str = '【テスト】【異星周回】\n参加希望ロールにリアクション願います' # 募集メッセージテンプレート
        self.memberList:list[discord.Member] = [] # 募集メンバーリスト
        self.timeTable:list[dt] = [] # 防衛軍タイムテーブル
        
        self.roles = {
            'magic':self.RoleEmoji(1247720076656906365),
            'magic_night':self.RoleEmoji(1249660445330247690),
            'ranger':self.RoleEmoji(1249660475101413437),
            'boomerang':self.RoleEmoji(1247713828553228359),
            'butterfly':self.RoleEmoji(1247713053353443390),
            'damage':self.RoleEmoji(1249660350367010846),
            'card':self.RoleEmoji(1247715201541865515),
            'connect':self.RoleEmoji(1247717037950763109),
            'monster':self.RoleEmoji(1247717814144471070),
        }

        # self.shokugyo = {
        #     '弓魔': self.ServerRole(1252170590010478602),
        #     'ブレ': self.ServerRole(1252170810144325634),
        #     '霧レ': self.ServerRole(1252170979929755718),
        #     '札ま': self.ServerRole(1252171064700829757),
        #     '中ま': self.ServerRole(1252172997058498580),
        #     '札バ': self.ServerRole(1252171225602592798),
        #     '道具': self.ServerRole(1252171283706413086),
        #     '遊び': self.ServerRole()
        # }

        self.formation:Formation = None # パーティ編成クラス

ROBIN_GUILD:Guild = None

@client.event
async def on_ready():
    global ROBIN_GUILD

    # チャンネル・ギルドをゲット
    ROBIN_GUILD = Guild(1246651972342386791)

    ROBIN_GUILD.PARTY_CH = client.get_channel(1246662816673304587)
    # ROBIN_GUILD.PARTY_CH = client.get_channel(1246662742987772067)
    ROBIN_GUILD.DEV_CH = client.get_channel(1246662742987772067)
    ROBIN_GUILD.COMMAND_CH = client.get_channel(1249294452149715016)

    # IDからロールを定義
    for role in ROBIN_GUILD.roles:
        ROBIN_GUILD.roles[role].set_emoji(ROBIN_GUILD.GUILD.get_emoji(ROBIN_GUILD.roles[role].id))
    
    ROBIN_GUILD.FULL_FORMATION = { # フルパーティ構成
            ROBIN_GUILD.roles['magic_night'].emoji: 1,
            ROBIN_GUILD.roles['boomerang'].emoji: 1,
            ROBIN_GUILD.roles['butterfly'].emoji: 1,
            ROBIN_GUILD.roles['card'].emoji: 1,
            ROBIN_GUILD.roles['connect'].emoji: 1,
            ROBIN_GUILD.roles['monster'].emoji: 3,
    }

    ROBIN_GUILD.LIGHT_FORMATION = { # ライトパーティ編成
            ROBIN_GUILD.roles['magic_night'].emoji: 1,
            ROBIN_GUILD.roles['ranger'].emoji: 1,
            ROBIN_GUILD.roles['damage'].emoji: 2,
    }
    
    ROBIN_GUILD.TRANCE_FORMATION = { # 職変換
            ROBIN_GUILD.roles['magic_night'].emoji : ROBIN_GUILD.roles['magic_night'].emoji,
            ROBIN_GUILD.roles['boomerang'].emoji : ROBIN_GUILD.roles['ranger'].emoji,
            ROBIN_GUILD.roles['butterfly'].emoji : ROBIN_GUILD.roles['ranger'].emoji,
            ROBIN_GUILD.roles['card'].emoji : ROBIN_GUILD.roles['damage'].emoji,
            ROBIN_GUILD.roles['connect'].emoji : ROBIN_GUILD.roles['damage'].emoji,
            ROBIN_GUILD.roles['monster'].emoji : ROBIN_GUILD.roles['damage'].emoji,
    }

    # タイムテーブルをゲット
    timeTable = getTimetable()
    for t in timeTable:
        print(t)
    await client.change_presence(activity=discord.CustomActivity(name=f'Next:{timeTable[0].strftime('%H')}時'))
    
    ROBIN_GUILD.timeTable = timeTable
    loop.start()

    print('Wakeup Bot')

@client.event
async def on_reaction_add(reaction:discord.Reaction, user:Union[discord.Member,discord.User]):
    global ROBIN_GUILD
    if user == client.user: return # 自信（ボット）のリアクションを無視
    if not reaction.is_custom_emoji(): return # カスタム絵文字以外を無視
    if reaction.emoji not in ROBIN_GUILD.FULL_FORMATION: # 想定しないリアクションを削除
        print(f'{dt.now()} recive reaction add_clear {user} {reaction.emoji.name}')
        await reaction.message.clear_reaction(reaction.emoji)
        return
    print(f'{dt.now()} recive reaction add {user} {reaction.emoji.name}')
    if reaction.message == ROBIN_GUILD.reclutingMessage: # 募集メッセージ
        # パーティ編成クラスに追加と人数更新
        memberNum = ROBIN_GUILD.formation.addMember(user, reaction.emoji)
        if memberNum >= 0: # 参加数が変わったから更新
            await ROBIN_GUILD.reclutingMessage.edit(content=f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 {memberNum}人')

@client.event
async def on_reaction_remove(reaction:discord.Reaction, user:Union[discord.Member,discord.User]):
    global ROBIN_GUILD
    if user == client.user: return # 自信（ボット）のリアクションを無視
    if not reaction.is_custom_emoji(): return # カスタム絵文字以外を無視
    if reaction.emoji not in ROBIN_GUILD.FULL_FORMATION: return # 想定しないリアクションを無視
    print(f'{dt.now()} recive reaction remove {user} {reaction.emoji.name}')
    if reaction.message == ROBIN_GUILD.reclutingMessage: # 募集メッセージ
        # パーティ編成クラスから削除と人数更新
        memberNum = ROBIN_GUILD.formation.rmMember(user, reaction.emoji) # 参加数変化なしは -1
        if memberNum >= 0: # 参加数が変わったから更新
            await ROBIN_GUILD.reclutingMessage.edit(content=f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 {memberNum}人')

async def reply_message(message:discord.Message, send:str, accept:bool):
    msg = await message.reply(send)
    await msg.delete(delay=10)
    if accept: print(f'{message.guild.name} {message.author.display_name} command success: {message.content}')
    else: print(f'{message.guild.name} {message.author.display_name} command error: {message.content}')

@client.event
async def on_message(message:discord.Message):
    global ROBIN_GUILD
    if message.author == client.user: return # 自身であれば無視
    if message.channel == ROBIN_GUILD.COMMAND_CH: # コマンドチャンネル
        # コマンドを実行
        msg = message.content.split(' ')
        admin_roles_name = ['サーバー管理者', '開発部', 'nico_robot', '運営維持管理', '準備ﾒﾝﾊﾞｰ臨時']
        guild_roles = await ROBIN_GUILD.GUILD.fetch_roles()
        success_roles:list[str] = []
        error_roles:list[str] = []
        rep_end = ''
        if msg[0] in 'ロール追加':
            rep_end = '追加'
            for m in msg[1:]:
                if m in admin_roles_name:
                    error_roles.append(m)
                    continue
                for role in guild_roles:
                    if m in role.name:
                        await message.author.add_roles(role)
                        success_roles.append(role.name)
                        break
                else: error_roles.append(m)

        elif msg[0] in 'ロール削除':
            rep_end = '削除'
            for m in msg[1:]:
                if m in admin_roles_name:
                    error_roles.append(m)
                    continue
                for role in guild_roles:
                    if m in role.name:
                        await message.author.remove_roles(role)
                        success_roles.append(role.name)
                        break
                else: error_roles.append(m)
        
        else:
            m = await message.reply(f'[エラー] {msg[0]} は無効です')
            await m.delete(delay=10)
            await message.delete(delay=10)
            return

        if len(success_roles) > 0:
            rep = ''
            for s in success_roles:
                rep += f'{s} '
            rep += f'の{rep_end}に成功'
            m = await message.reply(f'{rep}')
            print(rep)
            await m.delete(delay=10)
        if len(error_roles) > 0:
            rep = ''
            for s in error_roles:
                rep += f'{s} '
            rep += f'の{rep_end}に失敗'
            m = await message.reply(f'{rep}')
            print(rep)
            await m.delete(delay=10)
        await message.delete(delay=10)
            
        # コマンドチャンネル end

    elif message.channel == ROBIN_GUILD.DEV_CH: # デベロッパーチャンネル
        msg = message.content.split(' ')
        if msg[0] == '$reclute':
            now = dt.now()
            ROBIN_GUILD.timeTable = [dt(now.year, now.month, now.day, now.hour, now.minute, 0) + delta(minutes=31)] + ROBIN_GUILD.timeTable
            accept_msg = await message.reply(f'{ROBIN_GUILD.timeTable[0]}')
            await accept_msg.delete(delay=10)
            await message.delete(delay=10)
            for t in ROBIN_GUILD.timeTable:
                print(t)

@tasks.loop(seconds=60)
async def loop():
    global ROBIN_GUILD
    
    now = dt.now()
    now = dt(now.year, now.month, now.day, now.hour, now.minute) # 秒数はゼロ

    if now == ROBIN_GUILD.timeTable[0] - delta(minutes=30): # 募集開始
        # パーティ編成クラスをインスタンス化，メッセージ送信
        print(f'{dt.now()} [formation start]')
        ROBIN_GUILD.formation = Formation()
        ROBIN_GUILD.reclutingMessage = await ROBIN_GUILD.PARTY_CH.send(f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 0人')
        await sendReactions(ROBIN_GUILD.reclutingMessage, ROBIN_GUILD.FULL_FORMATION.keys())
        await client.change_presence(activity=discord.CustomActivity(name=f'Formation:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))
    
    elif now == ROBIN_GUILD.timeTable[0] - delta(minutes=5): # ５分前 パーティアナウンス
        # パーティ編成をアナウンス
        await ROBIN_GUILD.reclutingMessage.delete()
        full_parties:list[dict[discord.Emoji, set[Union[discord.Member,discord.User]]]] = None
        light_parties:list[dict[discord.Emoji, set[Union[discord.Member,discord.User]]]] = None
        full_parties, light_parties = ROBIN_GUILD.formation.formation(ROBIN_GUILD.FULL_FORMATION, ROBIN_GUILD.LIGHT_FORMATION, ROBIN_GUILD.TRANCE_FORMATION)
        del ROBIN_GUILD.formation

        ROBIN_GUILD.reclutingMessage = None
        if len(full_parties) == 0:
            await ROBIN_GUILD.PARTY_CH.send('今回のフルパーティは０組です')
        else:
            await ROBIN_GUILD.PARTY_CH.send('【フルパーティ】')
            print('full parties')
            for party in full_parties:
                msg = ''
                for emoji in party:
                    emo = str(emoji)
                    for user in party[emoji]:
                        msg += f'{emo}->{user.mention} '
                        print(f'{emoji.name}:{user.display_name}',end=' ')
                await ROBIN_GUILD.PARTY_CH.send(msg.strip(' '))
                print()

        if len(light_parties) == 0:
            await ROBIN_GUILD.PARTY_CH.send('今回のライトパーティは０組です')
        else:
            await ROBIN_GUILD.PARTY_CH.send('【ライトパーティ】')
            print('light parties')
            for party in light_parties:
                msg = ''
                for emoji in party:
                    # emo = str(emoji)
                    for user in party[emoji]:
                        msg += f'{user.mention} '
                        print(f'{emoji.name}:{user.display_name}',end=' ')
                        # msg += f'{emo}->{user.mention} '
                await ROBIN_GUILD.PARTY_CH.send(msg.strip(' '))
                print()

    elif now == ROBIN_GUILD.timeTable[0]: # 0分前 タイムテーブル更新
        print('[formation finish]')
        ROBIN_GUILD.reclutingMessage = None
        del ROBIN_GUILD.timeTable[0] # 先頭を削除
        await client.change_presence(activity=discord.CustomActivity(name=f'Next:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))

    if len(ROBIN_GUILD.timeTable) == 0: # タイムテーブルが空
        # 取りに行く
        ROBIN_GUILD.timeTable += getTimetable()
        for t in ROBIN_GUILD.timeTable:
            print(t)
        await client.change_presence(activity=discord.CustomActivity(name=f'Next:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))

# @client.event
# async def on_error(event, args, kwargs):
#     print(f'{event} でエラーでたンゴ')
#     print(f'{args}')
#     print(f'{kwargs}')

async def sendReactions(message:discord.Message, roles:list[discord.Emoji]):
    # リアクションを一斉送信
    for role in roles:
        await message.add_reaction(role)

def getTimetable() -> list[dt]:
    # タイムテーブルを取りに行く
    timeTable = []
    now30 = dt.now() + delta(minutes=30)
    for t in getTable():
        # 通過したものは追加しない
        if t > now30:
            timeTable.append(t)
    return timeTable

client.run('')
