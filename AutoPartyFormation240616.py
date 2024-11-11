from typing import Any, Tuple as tuple
class AutoPartyFormation:
    full_priority = None
    light_priority = None
    def __init__(self):
        self.players:dict[Any, set] = {}

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
        
    def getMembers(self) -> dict[Any,set]:
        return self.players

    def _formation(self, players:dict[Any,set], party_roles:dict[Any,int]) -> list[dict[Any,set]]:
        # ロール人数
        # print(self.getMembers())
        # ロール人数算出
        roles_num = {role:0 for role in party_roles}
        for role in party_roles:
            for player in players:
                if role in players[player]:
                    roles_num[role] += 1
                    
        # 【人数が少ないロールから埋める方法】
        # 最小かつ最大パーティ数より大きいロールを選定
        # ターゲットロールの中で自由度の高い人からロール権を削除
        # ロール人数が最大パーティ数以下になるまで繰り返す
        # ターゲットロールのメンバーが確定する
        # 確定したメンバーのターゲットロール以外を削除
        
        # 参加ロール数と枠数が同じになるまで
        while len(players) < sum(roles_num[role] for role in roles_num):
            # ロール係数
            roles_sum = {role:roles_num[role] / party_roles[role] for role in roles_num}
            target = max(roles_sum, key=roles_sum.get) # ターゲットロール選定
            players_sum = {player:0 for player in players} # プレイヤー係数
            for player in players:
                if target not in players[player]: continue # 関係ない人はパス
                for role in party_roles:
                    if role in players[player]:
                        players_sum[player] += roles_sum[role] # プレイヤー係数にロール係数を足していく
            max_player = max(players_sum, key=players_sum.get) # ターゲットプレイヤー
            if len(players[max_player]) == 1: # 無職になっちゃうから終わり 破れ
                pass
                break
            else:
                # 候補削除
                players[max_player].remove(target)
                roles_num[target] -= 1

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
                
        # パーティが１つになるか孤立する人がいなくなるまで繰り返す
        while len(parties) > 1 and any(self._party_sum(party) == 1 for party in parties):
            # print(f'solo{parties}')
            for party_num in range(1, len(parties)): # ２つ目のパーティから捜査
                if self._party_sum(parties[party_num]) == 1: # 孤立している
                    if self._party_sum(parties[party_num-1]) == len(party_roles): # 1つ前のパーティが満タン -> 1つ前パーティから1人連れてくる
                        for role in party_roles: # パーティの空枠を探す
                            # 孤立パーティに空枠 かつ 1つ前パーティの人がいる
                            if party_roles[role] > len(parties[party_num]) and len(parties[party_num-1][role]):
                                # プレイヤ移動を実行 1つ前パーティから孤立パーティに移動
                                parties[party_num][role].add(parties[party_num-1][role].pop())
                                break
                    else: # 1つ前のパーティが満タンでない
                        # # 強制的に移動する
                        solo_player = self._get_players_from_party(parties[party_num]).pop()
                        for role in players[solo_player]: # パーティの空を探す
                            if party_roles[role] > len(parties[party_num-1][role]):
                                parties[party_num-1][role].add(solo_player)
                                break
                        else: # 空きがなかったから強制的に配属
                            for role in party_roles:
                                if role in players[solo_player]:
                                    parties[party_num-1][role].add(solo_player)
                            else: parties[party_num-1][list(players[solo_player])[0]].add(solo_player)
                        # 処理おわり パーティが空になるので del
                        del parties[party_num]
                        break

        return parties
        # return parties, solo
    
    def formation(self, fullparty_roles:dict[Any, int], lightparty_roles:dict[Any, int], trans_roles:dict[Any, Any]) -> tuple[list[dict[Any,set]], list[dict[Any,set]]]:
        
        parties = self._formation(self.players, fullparty_roles)
        lightplayers = {}
        full_parties:list[Any,set] = []
        # print(parties)
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

    def _party_sum(self, party:dict[Any,set]) -> int:
        return len(self._get_players_from_party(party))
    
    def _get_players_from_party(self, party:dict[Any,set]) -> set[Any]:
        players:set[Any] = set()
        for player_set in party.values():
            if len(player_set) == 0: continue
            for player in player_set:
                players.add(player)
        return players
    

# 動作テスト
if __name__ == '__main__':
    from random import randint
    f = AutoPartyFormation()

    role_pool = ['魔', '霧', '投', '札', '継', '攻', '攻', '攻']
    iterater = range(16*2+4)
    for i in iterater:
        r = randint(0, 7)
        f.addMember(f'u{i%17}', role_pool[r])
    with open('res.txt', 'w', encoding='utf-8-sig') as file:
        for player in f.players:
            file.write(f'{player} {f.players[player]}\n')
    
    trance_dict = {'魔':'魔', '霧':'レ', '投':'レ', '札':'火', '継':'火', '攻':'火', '攻':'火', '攻':'火'}
    full_role = {'魔':1, '霧':1, '投':1, '札':1, '継':1, '攻':3}
    light_role = {'魔':1, 'レ':1, '火':2}
    # print(f.getMembers())
    # players = {'u0': {'霧', '攻', '札'}, 'u1': {'攻', '投'}, 'u2': {'攻', '投'}, 'u3': {'継', '投'}, 'u4': {'継', '投'}, 'u5': {'攻'}, 'u6': {'継', '投'}, 'u7': {'札', '投'}, 'u8': {'魔', '札'}}
    # players = {'u0': {'霧', '攻', '札'}, 'u1': {'攻', '投'}, 'u2': {'攻', '投'}, 'u3': {'継', '投'}, 'u4': {'継', '投'}, 'u5': {'攻'}, 'u6': {'継', '投'}, 'u7': {'札', '投'}, 'u8': {'魔', '札'}, 'u9': {'札', '投'}, 'u10': {'攻', '投'}, 'u11': {'攻', '魔'}, 'u12': {'攻'}, 'u13': {'攻', '札'}, 'u14': {'霧', '継'}, 'u15': {'継'}}
    # for u in players:
    #     for r in players[u]:
    #         f.addMember(u, r)
    print(f.getMembers())
    full, light = f.formation(full_role, light_role, trance_dict)
    print('full')
    for i in full:
        print(i)
    print('light')
    for i in light:
        print(i)