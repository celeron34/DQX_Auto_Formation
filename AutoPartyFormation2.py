from typing import Any, Tuple

class AutoPartyFormation:
    def __init__(self):
        '''メンバを追加する型'''
        self.role_preference:dict[Any,list] = {}
        self.players:dict[Any,list] = {}
    
    def addMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        if self.role_preference not in role:
            self.role_preference[role] = []
        self.role_preference[role].append(user)
        if user in self.players: # ディクショナリにあった
            self.players[user].append(role)
            # return -1
        else: # ディクショナリになかった
            self.players[user] = [role]
            # return len(self.players)
        return len(self.players) # なんか安定しないあら全部返す

    def remMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        if self.role_preference not in role:
            return len(self.players)
        self.role_preference[role].remove(user)
        if user in self.players: # dictにあった
            self.players[user].remove(role)
            if len(self.players[user]) == 0:
                del self.players[user]
            # return len(self.players)
        else: pass # dictになかった
            # return -1
        return len(self.players) # なんか安定しないから全部返す
        
    def getMemberNum(self) -> int:
        return len(self.players)

    def formation(self, full_roles:dict[Any,int], light_roles:dict[Any,int]) -> Tuple[list, dict]:
        '''full_roles {ロール名 : 人数}
        light_roles {{full_roles : [変換先]}}'''
        assigned_players = set() # 編成済みプレイヤー
        parties:list[dict[Any,list]] = [] # パーティ
        count = 1
        while len(assigned_players) < len(self.players):
            party = {role: [] for role in full_roles}
            for role in full_roles: # role:user
                for player in self.role_preference[role]: # player:list[user]
                    if player not in assigned_players and len(party[role]) < full_roles[role]:
                        party[role].append(player)
                        assigned_players.add(player)
                    if len(party[role]) == full_roles[role]: break
            parties.append(party)
            count += 1
        # ログ
        print('-- フルパーティ編成完了 --')
        for party in parties:
            print(party)
        # return parties

        # フルパーティ判定
        full_parties:list[dict[Any,list]] = []
        solo:dict[Any,list] = {} # dict[User, list[Emoji]]
        for party in parties:
            if all(len(party[role]) == full_roles[role] for role in full_roles):
                full_parties.append(party)
            else:
                for p in party:
                    for user in party[p]:
                        solo[user] = self.players[user]
        
        print('-- PartyFormation.formation result --')
        print(f'-- full_parties --')
        for party in full_parties:
            print(party)
        print(f'-- light_parties --')
        for s in solo:
            print(f'{s}:{solo[s]}')
        return full_parties, solo