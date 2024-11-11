def form_parties(players_roles):
    # プレイヤーごとに応募しているロールを格納するリスト
    players = players_roles

    # パーティのロール数の要件
    required_roles = {'role_1': 1, 'role_2': 1, 'role_3': 1, 'role_4': 1, 'role_5': 1, 'role_6': 3}
    
    parties = []

    def backtrack(current_party, role_count, used_players):
        # パーティが完成したら、結果リストに追加
        if role_count == required_roles:
            parties.append(current_party.copy())
            return
        
        for i, roles in enumerate(players):
            if i in used_players:
                continue
            
            for role in roles:
                if role_count[role] < required_roles[role]:
                    current_party.append((i, role))
                    role_count[role] += 1
                    used_players.add(i)
                    
                    backtrack(current_party, role_count, used_players)
                    
                    # バックトラック
                    current_party.pop()
                    role_count[role] -= 1
                    used_players.remove(i)
    
    backtrack([], {role: 0 for role in required_roles}, set())
    
    return parties

# 各プレイヤーの応募しているロール（例）
players_roles = [
    ['role_1', 'role_2'],
    ['role_2', 'role_3'],
    ['role_3', 'role_4'],
    ['role_4', 'role_5'],
    ['role_5', 'role_6'],
    ['role_6', 'role_1'],
    ['role_1', 'role_6'],
    ['role_2', 'role_6'],
    ['role_3', 'role_6'],
    ['role_4', 'role_5'],
    ['role_5', 'role_1'],
    ['role_6']
]

# パーティ編成を実行
parties = form_parties(players_roles)

print(f"形成されたパーティ数: {len(parties)}")
for i, party in enumerate(parties):
    print(f"パーティ {i + 1}: {party}")
