from typing import Any
class AutoPartyFormation:
    def __init__(self, roles:dict[Any,int]):
        '''roles {ロール名 : 人数}
        メンバを追加する型'''
        self.role_preference = {role:[] for role in roles}
        self.roles = roles
        self.players:dict[Any,list] = {}
    
    def addMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        self.role_preference[role].append(user)
        if user in self.players: # ディクショナリにあった
            self.players[user].append(role)
            print(f'{__name__} {len(self.players)}')
            # return -1
        else: # ディクショナリになかった
            self.players[user] = [role]
            # return len(self.players)
        return len(self.players)

    def remMember(self, user, role) -> int:
        '''return: int
        登録数
        -1は変化なし'''
        self.role_preference[role].remove(user)
        if user in self.players: # dictにあった
            self.players[user].remove(role)
            if len(self.players[user]) == 0:
                del self.players[user]
                print(f'{__name__} {len(self.players)}')
            # return len(self.players)
        else: pass # dictになかった
            # return -1
        return len(self.players)
        
    def getMemberNum(self) -> int:
        return len(self.players)

    def formation(self) -> list:
        assigned_players = set()
        parties = []
        while len(assigned_players) < len(self.players):
            party = {role: [] for role in self.roles}
            for role in self.roles:
                for player in self.role_preference[role]:
                    if player not in assigned_players and len(party[role]) < self.roles[role]:
                        party[role].append(player)
                        assigned_players.add(player)
                    if len(party[role]) == self.roles[role]: break
            parties.append(party)
        # return parties
        complete_parties = []
        for party in parties:
            if all(len(party[role]) == self.roles[role] for role in self.roles):
                complete_parties.append(party)
        return complete_parties