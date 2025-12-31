from app import app, db, User, World, SharedEvent, GameLog, EventGroup, EventTag, EventLike, user_friends, event_participants
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# 重新设计的模拟数据生成函数（修复好友关系和游戏日志双向性问题）


def regenerate_mock_data():
    """生成重新设计的模拟数据

    修复的问题：
    1. 确保好友关系完全一致
    2. 游戏日志的双向性：当玩家加入世界时，所有玩家都会记录彼此的存在
    3. 更真实的场景模拟：玩家加入已有朋友的世界时，会记录所有已存在的朋友
    """
    print("正在重新生成模拟数据...")

    # 1. 清除所有现有数据
    print("清除现有数据...")
    db.session.execute(event_participants.delete())
    db.session.execute(user_friends.delete())
    db.session.query(EventLike).delete()
    db.session.query(EventTag).delete()
    db.session.query(SharedEvent).delete()
    db.session.query(EventGroup).delete()
    db.session.query(GameLog).delete()
    db.session.query(World).delete()
    db.session.query(User).delete()
    db.session.commit()

    # 2. 创建新的世界
    print("创建世界...")
    worlds = [
        World(world_name="The Black Cat", tags="Social,Music,Dance,Bar"),
        World(world_name="Murder 4", tags="Game,Horror,Puzzle"),
        World(
            world_name="Treehouse in the Shade",
            tags="Social,Relaxing,Nature"),
        World(world_name="Starship Commander", tags="Game,Action,Co-op"),
        World(world_name="Zen Garden", tags="Relaxing,Meditation,Nature"),
        World(world_name="Cyberpunk Market",
              tags="Social,Exploration,Futuristic")
    ]

    for world in worlds:
        db.session.add(world)
    db.session.commit()

    # 3. 创建新用户
    print("创建用户...")
    users = {}
    user_credentials = [
        ("alice", "password123", "Alice"),
        ("bob", "password123", "Bob"),
        ("charlie", "password123", "Charlie"),
        ("david", "password123", "David"),
        ("emma", "password123", "Emma"),
        ("demo", "demo", "Demo User")
    ]

    for username, password, display_name in user_credentials:
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        users[username] = user
    db.session.commit()

    # 4. 建立好友关系网络（确保完全对称）
    print("建立好友关系...")
    # 好友关系矩阵：(user1, user2) - 只需要单向定义，后续会确保双向
    friendship_pairs = [
        ("alice", "bob"),
        ("alice", "charlie"),
        ("alice", "emma"),
        ("bob", "charlie"),
        ("bob", "david"),
        ("charlie", "david"),
        ("david", "emma")
    ]

    # 确保双向好友关系
    for user1_name, user2_name in friendship_pairs:
        user1 = users[user1_name]
        user2 = users[user2_name]

        # 检查并添加双向关系
        if user2 not in user1.friends:
            user1.friends.append(user2)
        if user1 not in user2.friends:
            user2.friends.append(user1)

    # 验证好友关系的对称性
    print("验证好友关系对称性...")
    for user in users.values():
        for friend in user.friends:
            if user not in friend.friends:
                print(f"修复好友关系：{user.username} ↔ {friend.username}")
                friend.friends.append(user)

    db.session.commit()

    # 5. 设置基础时间
    base_time = datetime.now() - timedelta(days=7)  # 一周前

    # 6. 生成游戏日志和共享事件
    print("生成游戏日志和共享事件...")

    # 获取世界引用
    world_dict = {w.world_name: w for w in worlds}

    # 辅助函数：生成游戏日志
    def generate_session_logs(
            world, participants, start_times, end_times, world_id):
        """生成会话的游戏日志，确保双向性

        Args:
            world: 世界对象
            participants: 参与者用户列表
            start_times: 字典，用户名 → 加入时间
            end_times: 字典，用户名 → 离开时间
            world_id: 世界ID
        """
        logs = []

        # 为每个参与者生成日志
        for user in participants:
            username = user.username

            # 1. 加入世界
            join_log = GameLog(
                user_id=user.id,
                timestamp=start_times[username],
                event_type="位置变动",
                world_name=world.world_name,
                world_id=world_id,
                player_name=username,
                is_friend=False
            )
            logs.append(join_log)

            # 2. 记录所有其他参与者（无论加入顺序）
            for other_user in participants:
                if other_user != user:
                    other_username = other_user.username

                    # 检查是否是好友
                    is_friend = other_user in user.friends

                    # 记录其他玩家的加入（根据时间顺序）
                    # 对于新加入的玩家，应该看到所有已存在的玩家
                    if start_times[other_username] <= start_times[username]:
                        # 其他玩家已经在世界中，新玩家会看到他们
                        meet_log = GameLog(
                            user_id=user.id,
                            timestamp=start_times[username],
                            event_type="玩家加入",
                            world_name=world.world_name,
                            world_id=world_id,
                            player_name=other_username,
                            is_friend=is_friend
                        )
                        logs.append(meet_log)
                    else:
                        # 其他玩家稍后加入，记录他们的加入事件
                        meet_log = GameLog(
                            user_id=user.id,
                            timestamp=start_times[other_username],
                            event_type="玩家加入",
                            world_name=world.world_name,
                            world_id=world_id,
                            player_name=other_username,
                            is_friend=is_friend
                        )
                        logs.append(meet_log)

            # 3. 记录其他玩家的离开（如果在当前玩家之前离开）
            for other_user in participants:
                if other_user != user:
                    other_username = other_user.username

                    # 检查是否是好友
                    is_friend = other_user in user.friends

                    if end_times[other_username] < end_times[username]:
                        # 其他玩家在当前玩家之前离开
                        leave_log = GameLog(
                            user_id=user.id,
                            timestamp=end_times[other_username],
                            event_type="玩家离开",
                            world_name=world.world_name,
                            world_id=world_id,
                            player_name=other_username,
                            is_friend=is_friend
                        )
                        logs.append(leave_log)

            # 4. 离开世界
            leave_log = GameLog(
                user_id=user.id,
                timestamp=end_times[username],
                event_type="玩家离开",
                world_name=world.world_name,
                world_id=world_id,
                player_name=username,
                is_friend=False
            )
            logs.append(leave_log)

        return logs

    # ==================== 场景1：多人社交聚会 ====================
    print("\n生成场景1：多人社交聚会 (The Black Cat)")
    black_cat = world_dict["The Black Cat"]
    party_time = base_time + timedelta(days=0, hours=19)

    # 参与者：alice, bob, charlie, emma
    party_participants = [
        users["alice"],
        users["bob"],
        users["charlie"],
        users["emma"]]

    # 每人的加入和离开时间
    join_times = {
        "alice": party_time.replace(hour=19, minute=0, second=0),
        "bob": party_time.replace(hour=19, minute=15, second=0),
        "charlie": party_time.replace(hour=19, minute=30, second=0),
        "emma": party_time.replace(hour=19, minute=45, second=0)
    }

    leave_times = {
        "alice": party_time.replace(hour=22, minute=0, second=0),
        "bob": party_time.replace(hour=21, minute=30, second=0),
        "charlie": party_time.replace(hour=22, minute=30, second=0),
        "emma": party_time.replace(hour=23, minute=0, second=0)
    }

    # 生成双向游戏日志
    party_logs = generate_session_logs(
        black_cat, party_participants, join_times, leave_times, "#12345"
    )

    for log in party_logs:
        db.session.add(log)

    # ==================== 场景2：游戏组队 ====================
    print("\n生成场景2：游戏组队 (Starship Commander)")
    starship = world_dict["Starship Commander"]
    game_time = base_time + timedelta(days=2, hours=14)

    # 参与者：bob, charlie, david
    game_participants = [users["bob"], users["charlie"], users["david"]]

    # 统一的游戏时间：14:00-16:30
    game_start = game_time.replace(hour=14, minute=0, second=0)
    game_end = game_time.replace(hour=16, minute=30, second=0)

    # 所有玩家同时加入和离开
    start_times = {}
    end_times = {}
    for user in game_participants:
        start_times[user.username] = game_start
        end_times[user.username] = game_end

    # 生成双向游戏日志
    game_logs = generate_session_logs(
        starship, game_participants, start_times, end_times, "#67890"
    )

    for log in game_logs:
        db.session.add(log)

    # ==================== 场景3：单人加入已有朋友的世界 ====================
    print("\n生成场景3：单人加入已有朋友的世界 (Treehouse in the Shade)")
    treehouse = world_dict["Treehouse in the Shade"]
    scene_time = base_time + timedelta(days=5, hours=16)

    # 参与者：charlie（先加入），然后是david和emma
    tree_participants = [users["charlie"], users["david"], users["emma"]]

    # 加入和离开时间
    start_times = {
        "charlie": scene_time.replace(hour=16, minute=0, second=0),  # 最先加入
        "david": scene_time.replace(hour=16, minute=20, second=0),  # 第二个加入
        "emma": scene_time.replace(hour=16, minute=30, second=0)   # 最后加入
    }

    end_times = {
        "charlie": scene_time.replace(hour=18, minute=0, second=0),
        "david": scene_time.replace(hour=17, minute=45, second=0),
        "emma": scene_time.replace(hour=17, minute=30, second=0)
    }

    # 生成双向游戏日志 - 特别注意：david和emma加入时会看到已存在的朋友
    tree_logs = generate_session_logs(
        treehouse, tree_participants, start_times, end_times, "#78901"
    )

    for log in tree_logs:
        db.session.add(log)

    # ==================== 场景4：demo用户体验 ====================
    print("\n生成场景4：demo用户体验 (Cyberpunk Market)")
    cyberpunk = world_dict["Cyberpunk Market"]
    demo_time = base_time + timedelta(days=4, hours=20)

    # demo用户和一个陌生人
    demo_participants = [users["demo"]]

    # demo的时间：20:00-21:30
    start_times = {
        "demo": demo_time.replace(hour=20, minute=0, second=0)
    }
    end_times = {
        "demo": demo_time.replace(hour=21, minute=30, second=0)
    }

    # demo的游戏日志
    demo_logs = []

    # 加入世界
    log1 = GameLog(
        user_id=users["demo"].id,
        timestamp=start_times["demo"],
        event_type="位置变动",
        world_name=cyberpunk.world_name,
        world_id="#98765",
        player_name="demo",
        is_friend=False
    )
    demo_logs.append(log1)

    # 遇到陌生人
    stranger_join_time = demo_time.replace(hour=20, minute=15, second=0)
    log2 = GameLog(
        user_id=users["demo"].id,
        timestamp=stranger_join_time,
        event_type="玩家加入",
        world_name=cyberpunk.world_name,
        world_id="#98765",
        player_name="Stranger_123",
        is_friend=False
    )
    demo_logs.append(log2)

    # 陌生人离开
    stranger_leave_time = demo_time.replace(hour=21, minute=0, second=0)
    log3 = GameLog(
        user_id=users["demo"].id,
        timestamp=stranger_leave_time,
        event_type="玩家离开",
        world_name=cyberpunk.world_name,
        world_id="#98765",
        player_name="Stranger_123",
        is_friend=False
    )
    demo_logs.append(log3)

    # 离开世界
    log4 = GameLog(
        user_id=users["demo"].id,
        timestamp=end_times["demo"],
        event_type="玩家离开",
        world_name=cyberpunk.world_name,
        world_id="#98765",
        player_name="demo",
        is_friend=False
    )
    demo_logs.append(log4)

    for log in demo_logs:
        db.session.add(log)

    # ==================== 场景5：双人游戏 ====================
    print("\n生成场景5：双人游戏 (Murder 4)")
    murder4 = world_dict["Murder 4"]
    game_time = base_time + timedelta(days=6, hours=21)

    # david和emma的双人游戏：21:00-22:15
    game_participants = [users["david"], users["emma"]]

    start_times = {
        "david": game_time.replace(hour=21, minute=0, second=0),
        "emma": game_time.replace(hour=21, minute=5, second=0)  # 晚5分钟加入
    }

    end_times = {
        "david": game_time.replace(hour=22, minute=15, second=0),
        "emma": game_time.replace(hour=22, minute=15, second=0)
    }

    # 生成双向游戏日志
    murder_logs = generate_session_logs(
        murder4, game_participants, start_times, end_times, "#34567"
    )

    for log in murder_logs:
        db.session.add(log)

    # ==================== 提交所有数据 ====================
    db.session.commit()
    print("\n模拟数据生成完成！")

    # 验证数据
    print("\n数据验证：")
    print("\n1. 好友关系验证：")
    for user in users.values():
        friends = [f.username for f in user.friends]
        print(f'{user.username}的好友: {friends}')
        # 验证双向性
        for friend_name in friends:
            friend = users[friend_name]
            if user.username not in [f.username for f in friend.friends]:
                print(f'  ❌ 好友关系不对称：{user.username} 在 {friend_name} 的好友列表中缺失！')
            else:
                print(f'  ✅ {user.username} ↔ {friend_name} 关系正常')

    print("\n2. 游戏日志验证：")
    total_logs = GameLog.query.count()
    print(f'共生成 {total_logs} 条游戏日志')

    # 按用户统计日志
    for user in users.values():
        user_logs = GameLog.query.filter_by(user_id=user.id).count()
        print(f'  {user.username}: {user_logs} 条日志')

    # ==================== 从游戏日志生成共享事件 ====================
    print("\n从游戏日志生成共享事件...")
    from app import convert_game_logs
    from flask import Flask
    import sys
    import os
    from flask_login import login_user

    # 模拟Flask请求上下文，以便调用convert_game_logs函数
    for username, user in users.items():
        print(f'\n为 {username} 生成共享事件...')

        # 调用转换函数
        try:
            # 创建请求上下文
            with app.test_request_context('/api/gamelog/convert', method='POST'):
                # 设置当前用户
                login_user(user)
                # 调用转换函数
                result = convert_game_logs()
                print(f'  ✅ 为 {username} 生成了 {result} 个共享事件')
        except Exception as e:
            print(f'  ❌ 为 {username} 生成共享事件时出错: {e}')
            import traceback
            traceback.print_exc()

    # 提交所有转换生成的事件
    db.session.commit()

    print("\n3. 事件验证：")
    events = SharedEvent.query.all()
    print(f'共生成 {len(events)} 个事件')
    for i, event in enumerate(events, 1):
        world = World.query.get(event.world_id)
        participants = [p.username for p in event.participants]
        print(
            f'  事件{i}: {event.friend_name} 在 {world.world_name}, 时间: {event.start_time.strftime("%m/%d %H:%M")}-{event.end_time.strftime("%H:%M")}, 参与者: {participants}')

    # 为事件匹配事件组
    print("\n匹配事件组...")
    from app import match_events_to_groups
    match_events_to_groups()
    print("事件组匹配完成！")


# 运行重新生成数据的函数
if __name__ == "__main__":
    with app.app_context():
        regenerate_mock_data()
