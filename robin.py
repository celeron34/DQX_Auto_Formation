import discord
from discord.ext import tasks
from dqx_ise import getTable
from datetime import datetime as dt, timedelta as delta
from AutoPartyFormation import AutoPartyFormation as Formation
from typing import Union

# インテント
intents = discord.Intents.all()
intents.message_content = True 
client = discord.Client(intents=intents)

class Guild:
    GUILD = None # ギルド
    class RoleEmoji: # id:int あいでぃー emoji:discord.Emoji ロールの絵文字
        id:int = None
        emoji:discord.Emoji = None
        def __init__(self, id:int) -> None:
            self.id = id
        def set_emoji(self, emoji:discord.Emoji):
            self.emoji = emoji

    def __init__(self, guild):
        self.GUILD = client.get_guild(guild)
        self.FULL_FORMATION:dict[discord.Emoji, int] = {}
        self.DEV_CH:discord.TextChannel = None # デベロッパーチャンネル
        self.PARTY_CH:discord.TextChannel = None # 募集チャンネル
        self.COMMAND_CH:discord.TextChannel = None # コマンドチャンネル

        self.reclutingMessage:discord.Message = None # 募集メッセージ
        self.reclutingMessageTemplate:str = '【テスト】【異星4人周回】\n4人パーティ参加希望ロールにリアクション願います' # 募集メッセージテンプレート
        self.memberList:list[discord.Member] = [] # 募集メンバーリスト
        self.timeTable:list[dt] = [] # 防衛軍タイムテーブル
        
        self.roles = {
                'ranger':self.RoleEmoji(1249660475101413437),
                'magic_night':self.RoleEmoji(1249660445330247690),
                'damage':self.RoleEmoji(1249660350367010846),
                # 'card':self.RoleEmoji(1247715201541865515),
                # 'monster':self.RoleEmoji(1247717814144471070),
                # 'connect':self.RoleEmoji(1247717037950763109),
                # 'magic':self.RoleEmoji(1247720076656906365),
                # 'boomerang':self.RoleEmoji(1247713828553228359),
                # 'butterfly':self.RoleEmoji(1247713053353443390),
        }

        self.formation:Formation = None # パーティ編成クラス

ROBIN_GUILD:Guild = None

@client.event
async def on_ready():
    global ROBIN_GUILD

    # チャンネル・ギルドをゲット
    ROBIN_GUILD = Guild(1246651972342386791)

    ROBIN_GUILD.PARTY_CH = client.get_channel(1246662816673304587)
    ROBIN_GUILD.DEV_CH = client.get_channel(1246662742987772067)
    ROBIN_GUILD.COMMAND_CH = client.get_channel(1249294452149715016)

    # IDからロールを定義
    for role in ROBIN_GUILD.roles:
        ROBIN_GUILD.roles[role].set_emoji(ROBIN_GUILD.GUILD.get_emoji(ROBIN_GUILD.roles[role].id))
    
    # フルパーティ構成
    ROBIN_GUILD.FULL_FORMATION = {
            ROBIN_GUILD.roles['damage'].emoji: 2,
            ROBIN_GUILD.roles['ranger'].emoji: 1,
            ROBIN_GUILD.roles['magic_night'].emoji: 1,
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
    print(f'{dt.now()} recive reaction add {user} {reaction.emoji.name}')

    if reaction.message == ROBIN_GUILD.reclutingMessage: # 募集メッセージ
        # パーティ編成クラスに追加と人数更新
        # if user in memberList: return # メンバーリストに含まれていれば無視
        memberNum = ROBIN_GUILD.formation.addMember(user, reaction.emoji) # 参加数変化なしは -1
        if memberNum >= 0: # 参加数が変わったから更新
            await ROBIN_GUILD.reclutingMessage.edit(content=f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 {memberNum}人')

@client.event
async def on_reaction_remove(reaction:discord.Reaction, user:Union[discord.Member,discord.User]):
    global ROBIN_GUILD
    if user == client.user: return # 自信（ボット）のリアクションを無視
    if not reaction.is_custom_emoji(): return # カスタム絵文字以外を無視
    print(f'{dt.now()} recive reaction remove {user} {reaction.emoji.name}')
    if reaction.message == ROBIN_GUILD.reclutingMessage: # 募集メッセージ
        # パーティ編成クラスから削除と人数更新
        memberNum = ROBIN_GUILD.formation.remMember(user, reaction.emoji) # 参加数変化なしは -1
        if memberNum >= 0: # 参加数が変わったから更新
            await ROBIN_GUILD.reclutingMessage.edit(content=f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 {memberNum}人')

@client.event
async def on_message(message:discord.Message):
    global ROBIN_GUILD
    if message.author == client.user: return # 自身であれば無視
    now = dt.now()
    if message.channel == ROBIN_GUILD.COMMAND_CH: # コマンドチャンネルの場合
        # コマンドを実行
        msg = message.content.split(' ')
        if msg[0] in 'ロール追加':
            ranks = [message.guild.get_role(1246662449042821150),
                     message.guild.get_role(1246662345879457893),
                     message.guild.get_role(1246662293501116446)]
            if msg[1] in '初級':
                await message.author.add_roles(ranks[0])
                await message.author.remove_roles(ranks[1])
                await message.author.remove_roles(ranks[2])
            elif msg[1] in '中級':
                await message.author.remove_roles(ranks[0])
                await message.author.add_roles(ranks[1])
                await message.author.remove_roles(ranks[2])
            elif msg[1] in '上級':
                await message.author.remove_roles(ranks[0])
                await message.author.remove_roles(ranks[1])
                await message.author.add_roles(ranks[2])
            else:
                error_msg = await message.reply('[エラー] 処理は行われませんでした')
                await error_msg.delete(delay=10)
                await message.delete(delay=10)
                print(f'{now.strftime('%Y/%m/%d_%H:%M:%S')} {message.author.display_name} command error: {message.content}')
                return
            accept_msg = await message.reply('[成功] ロールを変更しました')
            await accept_msg.delete(delay=10)
            await message.delete(delay=10)
            print(f'{now.strftime('%Y/%m/%d_%H:%M:%S')} {message.author.display_name} command succes: {message.content}')
        else:
            error_msg = await message.reply('[エラー] 処理は行われませんでした')
            await error_msg.delete(delay=10)
            await message.delete(delay=10)
            print(f'{now.strftime('%Y/%m/%d_%H:%M:%S')} {message.author.display_name} command error: {message.content}')

    
    elif message.channel == ROBIN_GUILD.DEV_CH:
        msg = message.content.split(' ')
        if msg[0] == '$reclute':
            now = dt.now()
            timeTable = [dt(now.year, now.month, now.day, now.hour, now.minute, 0) + delta(minutes=11)] + timeTable
            accept_msg = await message.reply(f'{timeTable[0]}')
            await accept_msg.delete(delay=10)
            await message.delete(delay=10)

@tasks.loop(seconds=60)
async def loop():
    global ROBIN_GUILD
    
    now = dt.now()
    now = dt(now.year, now.month, now.day, now.hour, now.minute) # secondsはゼロ

    if now == ROBIN_GUILD.timeTable[0] - delta(minutes=30): # 募集開始
        # パーティ編成クラスをインスタンス化，メッセージ送信
        print('[formation start]')
        ROBIN_GUILD.formation = Formation(ROBIN_GUILD.FULL_FORMATION)
        ROBIN_GUILD.reclutingMessage = await ROBIN_GUILD.PARTY_CH.send(f'{ROBIN_GUILD.reclutingMessageTemplate}\n参加数 0人')
        await sendReactions(ROBIN_GUILD.reclutingMessage, ROBIN_GUILD.roles)
        await client.change_presence(activity=discord.CustomActivity(name=f'Formation:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))
    elif now == ROBIN_GUILD.timeTable[0] - delta(minutes=5): # ５分前 パーティアナウンス
        # パーティ編成をアナウンス
        await ROBIN_GUILD.reclutingMessage.delete()
        # full_parties:list[dict[discord.Emoji, list[Union[discord.Member,discord.User]]]] = None
        # solo:dict[discord.User, list[discord.Emoji]] = None
        # full_parties, solo = ROBIN_GUILD.formation.formation()
        full_parties:list[dict[discord.Emoji, list]] = ROBIN_GUILD.formation.formation()
        del ROBIN_GUILD.formation

        ROBIN_GUILD.reclutingMessage = None
        if len(full_parties) == 0:
            m = await ROBIN_GUILD.PARTY_CH.send('今回のパーティは０組です')
            # m.delete(delay=5*60) # RuntimeWarning: Enable tracemalloc to get the object allocation traceback
        else:
            m = await ROBIN_GUILD.PARTY_CH.send('完成パーティ')
            # m.delete(delay=5*60) # RuntimeWarning: Enable tracemalloc to get the object allocation traceback
            for party in full_parties:
                msg = ''
                for emoji in party:
                    emo = str(emoji) # AttributeError: 'list' object has no attribute 'id'
                    for user in party[emoji]:
                        msg += f'{emo}->{user.mention} '
                m = await ROBIN_GUILD.PARTY_CH.send(msg.strip(' '))
                # m.delete(delay=5*60)

        # m = await ROBIN_GUILD.PARTY_CH.send('参加意思メンバー')
        # msg = ''
        # for user in solo.keys(): # OK メンション未確認
        #     msg += f'{user.mention}'
        #     for e in solo[user]:
        #         msg += f' {str(e)}'
        #     msg += '\n'
        # await ROBIN_GUILD.PARTY_CH.send(msg.strip('\n'))

        # if len(light_parties) == 0: await PARTY_CH.send('今回のライトパーティは０組です')
        # else:
        #     await PARTY_CH.send('以下ライトパーティ')
        #     for party in light_parties:
        #         msg = ''
        #         for role in party:
        #             emo = f'<:custom_emoji_name:{party[role].id}>'
        #             msg += f'{emo}:{party[role].name} '
        #         await PARTY_CH.send(msg)
        
#    elif now == timeTable[0] - delta(minutes=20): # 予備募集
#        msg = await PARTY_CH.send('【テスト】異星周回 予備募集\n参加希望ロールにリアクション願います\n※パーティ編成未実装')
#        await sendReactions(msg, REACTION_EMOJIS)
#        await client.change_presence(activity=discord.CustomActivity(name=f'Pre-recluting:{timeTable[0].strftime('%H')}時'))

    elif now == ROBIN_GUILD.timeTable[0]: # 0分前 タイムテーブル更新
        print('[formation finish]')
        del ROBIN_GUILD.timeTable[0] # 先頭を削除
        await client.change_presence(activity=discord.CustomActivity(name=f'Next:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))

    if len(ROBIN_GUILD.timeTable) == 0: # タイムテーブルが空
        # 取りに行く
        ROBIN_GUILD.timeTable += getTimetable()
        for t in ROBIN_GUILD.timeTable:
            print(t)
        await client.change_presence(activity=discord.CustomActivity(name=f'Next:{ROBIN_GUILD.timeTable[0].strftime('%H')}時'))

@client.event
async def on_error(event, args, kwargs):
    print(f'{event} でエラーでたンゴ')
    print(f'{args}')
    print(f'{kwargs}')

async def sendReactions(message:discord.Message, roles:dict[str,Guild.RoleEmoji]):
    # リアクションを一斉送信
    for r in roles:
        await message.add_reaction(roles[r].emoji)

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
