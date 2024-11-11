from typing import Any as any, Tuple as tuple
class AutoPartyFormation:
    full_priority = None
    light_priority = None
    def __init__(self):
        self.players:dict[any, set] = {}

    def addMember(self, user, role) -> int:
        if user in self.players:
            if role not in self.players[user]:
                self.players[user].add(role)
            return -1
        else:
            self.players[user] = {role}
            return len(self.players)

    def rmMember(self, user, role) -> int:
        if user in self.players:
            self.players[user].remove(role)
            if len(self.players[user]) == 0:
                del self.players[user]
            return len(self.players)
        else:
            return -1

    def _formation(self, players:dict[any,set], party_roles:dict[any,int]) -> list[dict[any,set]]:
        # ロール人数

        if len(players) % len(party_roles) == 1: # 孤立することが確定してる
            pass

        roles_num = {role:0 for role in party_roles}
        for role in party_roles:
            for player in players:
                if role in players[player]:
                    roles_num[role] += 1
        print(roles_num)
        while True:
            s = sum(roles_num[role] for role in roles_num)
            if len(players) >= s: break
            roles_sum = {role:roles_num[role] / party_roles[role] for role in roles_num}
            target = max(roles_sum, key=roles_sum.get)
            players_sum = {player:0 for player in players}
            for player in players:
                if target not in players[player]: continue
                for role in party_roles:
                    if role in players[player]:
                        players_sum[player] += roles_sum[role]
            max_player = max(players_sum, key=players_sum.get)
            print(f'{max_player} {target}')
            if len(players[max_player]) == 1:
                pass
                break
            else:
                players[max_player].remove(target)
                roles_num[target] -= 1
        print(players)
        print(roles_num)

        parties = [{role:set() for role in party_roles}]
        for player in players:
            # if len(players[player]) == 0: continue
            role = list(players[player])[0]
            for party in range(len(parties)):
                if role in parties[party] and len(parties[party][role]) < party_roles[role]:
                    parties[party][role].add(player)
                    break
            else:
                parties.append({role:set() for role in party_roles})
                parties[party+1][role].add(player)
        # parties.append({role:[] for role in party_roles})
        return parties
        # return parties, solo

    def formation(self, fullparty_roles:dict[any, int], lightparty_roles:dict[any, int], trans_roles:dict[any, any]) -> tuple[list[dict[any,set]], list[dict[any,set]]]:
        
        parties = self._formation(self.players, fullparty_roles)
        lightplayers = {}
        full_parties = []
        print(parties)
        for party in parties:
            if all(fullparty_roles[role] == len(party[role]) for role in fullparty_roles):
                full_parties.append(party)
            else:
                for players in party.values():
                    for player in players:
                        lightplayers[player] = {trans_roles[role] for role in self.players[player]}

        if len(lightplayers) > 0:
            lightparties = self._formation(lightplayers, lightparty_roles)
        else:
            lightparties = []
        return full_parties, lightparties

from random import randint

f = AutoPartyFormation()
role_pool = ['魔', '霧', '投', '札', '継', '攻', '攻', '攻']
iterater = range(16*2+4)
for i in iterater:
    r = randint(0, 7)
    f.addMember(f'u{i%(8*2)}', role_pool[r])
with open('res.txt', 'w', encoding='utf-8-sig') as file:
    for player in f.players:
        file.write(f'{player} {f.players[player]}\n')
trance_dict = {'魔':'魔', '霧':'レ', '投':'レ', '札':'火', '継':'火', '攻':'火', '攻':'火', '攻':'火'}
full_role = {'魔':1, '霧':1, '投':1, '札':1, '継':1, '攻':3}
light_role = {'魔':1, 'レ':1, '火':2}
full, light = f.formation(full_role, light_role, trance_dict)
print('full')
for i in full:
    print(i)
print('light')
for i in light:
    print(i)