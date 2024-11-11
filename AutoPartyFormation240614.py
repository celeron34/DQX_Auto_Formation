from typing import Any, Tuple

class AutoPartyFormation:
    def __init__(self):
        '''メンバを追加する型'''
        self.role_preference:dict[Any,list] = {} # dict[role, list[user]]
        self.players:dict[Any,list] = {} # dict[user, list[role]]
    
    def addMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        if role not in self.role_preference:
            self.role_preference[role] = []
        self.role_preference[role].append(user)
        if user in self.players: # ディクショナリにあった
            if role not in self.players[user]: # 同じロールがなかった
                self.players[user].append(role)
            return -1
        else: # ディクショナリになかった
            self.players[user] = [role]
            return len(self.players)
        # return len(self.players) # なんか安定しないあら全部返す

    def remMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        if role not in self.role_preference:
            return len(self.players)
        self.role_preference[role].remove(user)
        if user in self.players: # dictにあった
            self.players[user].remove(role)
            if len(self.players[user]) == 0:
                del self.players[user]
            return len(self.players)
        else: # dictになかった
            pass
            return -1
        # print(len(self.players))
        # return len(self.players) # なんか安定しないから全部返す
        
    def getMemberNum(self) -> int:
        return len(self.players)

    def formation(self, full_roles:dict[Any,int], light_roles:dict[Any,int], trance:dict[Any, Any]) -> Tuple[list, dict]:
        '''full_roles {ロール名 : 人数}
        light_roles {{full_roles : [変換先]}}'''
        assigned_players = set() # 編成済みプレイヤー
        parties:list[dict[Any,list]] = [] # パーティ
        count = 1
        while len(assigned_players) < len(self.players):
            party = {role: [] for role in full_roles}
            for role in full_roles: # role:user
                if role not in self.role_preference:
                    print(f'add preference {role}')
                    self.role_preference[role] = []
                for player in self.role_preference[role]: # player:role
                    if player not in assigned_players and len(party[role]) < full_roles[role]:
                        party[role].append(player)
                        assigned_players.add(player)
                    if len(party[role]) == full_roles[role]: break
            parties.append(party)
            count += 1
            
        # フルパーティ判定
        light_players:dict[Any, list] = {}
        full_parties:list[dict[Any,list]] = []
        for party in parties:
            if all(len(party[role]) == full_roles[role] for role in full_roles):
                # フルパーティたち
                full_parties.append(party)
            else: # フルパーティじゃない人たち
                for p in party:
                    for user in party[p]:
                        light_players[user] = self.players[user]

        # trance player roles
        for player in light_players:
            role_list = []
            for role in light_players[player]:
                if role not in role_list:
                    if role not in trance.keys(): role_list.append(role)
                    else: role_list.append(trance[role])
            light_players[player] = role_list

        # replace role_preference
        self.role_preference = {}
        for user in light_players:
            for role in light_players[user]:
                self.addMember(user, role) # role_preferenceに追加

        # formation light_parties
        assigned_players = set() # 編成済みプレイヤー
        parties:list[dict[Any,list]] = [] # パーティ
        count = 1
        while len(assigned_players) < len(light_players):
            party = {role: [] for role in light_roles}
            for role in light_roles: # role:user
                if role not in self.role_preference:
                    print(f'add preference {role}')
                    self.role_preference[role] = []
                for player in self.role_preference[role]:
                    if player not in assigned_players and len(party[role]) < light_roles[role]:
                        party[role].append(player)
                        assigned_players.add(player)
                    if len(party[role]) == light_roles[role]: break
            parties.append(party)
            count += 1
        light_parties = parties

        return full_parties, light_parties