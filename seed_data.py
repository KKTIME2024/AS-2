#!/usr/bin/env python3
"""
向数据库添加所有测试数据：用户、世界、游戏日志、共享事件和评论
"""

import sys
import os
from app import app, db, User, World, SharedEvent, GameLog, EventGroup, EventTag, EventComment, ActivityFeed, EventReminder, EventShare, user_friends, event_participants
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


def seed_database():
    """向数据库添加所有测试数据"""
    with app.app_context():
        print("开始向数据库添加测试数据...")
        
        try:
            # 1. 检查数据库状态
            print("1. 检查数据库状态...")
            
            # 检查是否已有数据
            user_count = User.query.count()
            if user_count > 0:
                print(f"   ⚠️  数据库中已有 {user_count} 个用户，可能已包含数据")
                print("   建议先运行 reset_db.py 清空数据库")
                confirm = input("   是否继续添加数据？(y/N): ")
                if confirm.lower() != 'y':
                    print("   操作已取消")
                    return
            
            print("   ✅ 开始添加数据")
            
            # =============================================
            # 2. 生成模拟数据（整合自regenerate_data_v2.py）
            # =============================================
            print("\n2. 生成模拟数据...")
            
            # 生成用户
            print("   a. 创建用户...")
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
            print(f"   ✅ 创建了 {len(users)} 个用户")
            
            # 创建世界
            print("   b. 创建世界...")
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
            world_dict = {w.world_name: w for w in worlds}
            print(f"   ✅ 创建了 {len(worlds)} 个世界")
            
            # 建立好友关系
            print("   c. 建立好友关系...")
            friendship_pairs = [
                ("alice", "bob"),
                ("alice", "charlie"),
                ("alice", "emma"),
                ("bob", "charlie"),
                ("bob", "david"),
                ("charlie", "david"),
                ("david", "emma")
            ]
            
            for user1_name, user2_name in friendship_pairs:
                user1 = users[user1_name]
                user2 = users[user2_name]
                
                if user2 not in user1.friends:
                    user1.friends.append(user2)
                if user1 not in user2.friends:
                    user2.friends.append(user1)
            db.session.commit()
            print("   ✅ 建立了双向好友关系")
            
            # 辅助函数：生成游戏日志
            def generate_session_logs(
                    world, participants, start_times, end_times, world_id):
                """生成会话的游戏日志，确保双向性"""
                logs = []
                
                for user in participants:
                    username = user.username
                    
                    # 加入世界
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
                    
                    # 记录所有其他参与者
                    for other_user in participants:
                        if other_user != user:
                            other_username = other_user.username
                            is_friend = other_user in user.friends
                            
                            if start_times[other_username] <= start_times[username]:
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
                    
                    # 记录其他玩家的离开
                    for other_user in participants:
                        if other_user != user:
                            other_username = other_user.username
                            is_friend = other_user in user.friends
                            
                            if end_times[other_username] < end_times[username]:
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
                    
                    # 离开世界
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
            
            # 生成游戏日志
            print("   d. 生成游戏日志...")
            base_time = datetime.now() - timedelta(days=7)
            
            # 场景1：多人社交聚会
            black_cat = world_dict["The Black Cat"]
            party_time = base_time + timedelta(days=0, hours=19)
            party_participants = [users["alice"], users["bob"], users["charlie"], users["emma"]]
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
            party_logs = generate_session_logs(black_cat, party_participants, join_times, leave_times, "#12345")
            
            # 场景2：游戏组队
            starship = world_dict["Starship Commander"]
            game_time = base_time + timedelta(days=2, hours=14)
            game_participants = [users["bob"], users["charlie"], users["david"]]
            game_start = game_time.replace(hour=14, minute=0, second=0)
            game_end = game_time.replace(hour=16, minute=30, second=0)
            start_times = {user.username: game_start for user in game_participants}
            end_times = {user.username: game_end for user in game_participants}
            game_logs = generate_session_logs(starship, game_participants, start_times, end_times, "#67890")
            
            # 场景3：单人加入已有朋友的世界
            treehouse = world_dict["Treehouse in the Shade"]
            scene_time = base_time + timedelta(days=5, hours=16)
            tree_participants = [users["charlie"], users["david"], users["emma"]]
            start_times = {
                "charlie": scene_time.replace(hour=16, minute=0, second=0),
                "david": scene_time.replace(hour=16, minute=20, second=0),
                "emma": scene_time.replace(hour=16, minute=30, second=0)
            }
            end_times = {
                "charlie": scene_time.replace(hour=18, minute=0, second=0),
                "david": scene_time.replace(hour=17, minute=45, second=0),
                "emma": scene_time.replace(hour=17, minute=30, second=0)
            }
            tree_logs = generate_session_logs(treehouse, tree_participants, start_times, end_times, "#78901")
            
            # 场景4：demo用户体验
            cyberpunk = world_dict["Cyberpunk Market"]
            demo_time = base_time + timedelta(days=4, hours=20)
            demo_participants = [users["demo"]]
            start_times = {"demo": demo_time.replace(hour=20, minute=0, second=0)}
            end_times = {"demo": demo_time.replace(hour=21, minute=30, second=0)}
            demo_logs = []
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
            
            # 场景5：双人游戏
            murder4 = world_dict["Murder 4"]
            game_time = base_time + timedelta(days=6, hours=21)
            game_participants = [users["david"], users["emma"]]
            start_times = {
                "david": game_time.replace(hour=21, minute=0, second=0),
                "emma": game_time.replace(hour=21, minute=5, second=0)
            }
            end_times = {
                "david": game_time.replace(hour=22, minute=15, second=0),
                "emma": game_time.replace(hour=22, minute=15, second=0)
            }
            murder_logs = generate_session_logs(murder4, game_participants, start_times, end_times, "#34567")
            
            # 提交所有游戏日志
            all_logs = party_logs + game_logs + tree_logs + demo_logs + murder_logs
            for log in all_logs:
                db.session.add(log)
            db.session.commit()
            print(f"   ✅ 生成了 {len(all_logs)} 条游戏日志")
            
            # 从游戏日志生成共享事件
            print("   e. 从游戏日志生成共享事件...")
            
            def process_user_game_logs(user):
                """处理用户游戏日志，生成共享事件"""
                from app import get_or_create_world, match_events_to_groups
                
                game_logs = GameLog.query.filter_by(
                    user_id=user.id).order_by(
                    GameLog.timestamp).all()
                
                all_users = User.query.all()
                username_to_user = {u.username: u for u in all_users}
                
                world_sessions = {}
                converted_count = 0
                
                for log in game_logs:
                    world_key = f"{log.world_name}_{log.world_id}"
                    player_name = log.player_name
                    
                    if log.event_type == '位置变动':
                        if player_name == user.username:
                            if world_key not in world_sessions:
                                world_sessions[world_key] = {
                                    'world_name': log.world_name,
                                    'world_id': log.world_id,
                                    'players': {},
                                    'events': []
                                }
                            if player_name not in world_sessions[world_key]['players']:
                                world_sessions[world_key]['players'][player_name] = {
                                    'start_time': log.timestamp,
                                    'is_friend': False
                                }
                    
                    elif log.event_type == '玩家加入':
                        if world_key in world_sessions:
                            world_sessions[world_key]['players'][player_name] = {
                                'start_time': log.timestamp,
                                'is_friend': log.is_friend
                            }
                    
                    elif log.event_type == '玩家离开':
                        if player_name != user.username:
                            if world_key in world_sessions and player_name in world_sessions[world_key]['players']:
                                player_info = world_sessions[world_key]['players'].pop(player_name)
                                duration = int(
                                    (log.timestamp - player_info['start_time']).total_seconds())
                                
                                world = get_or_create_world(world_sessions[world_key]['world_name'], '')
                                
                                # 检查是否已存在相同事件（基于参与者、世界和时间范围）
                                existing_event = SharedEvent.query.filter(
                                    SharedEvent.world_id == world.id,
                                    SharedEvent.start_time == player_info['start_time'],
                                    SharedEvent.end_time == log.timestamp
                                ).first()
                                
                                # 如果没有相同事件，则创建新事件
                                if not existing_event:
                                    event = SharedEvent(
                                        user_id=user.id,
                                        world_id=world.id,
                                        friend_name=player_name.strip(),
                                        start_time=player_info['start_time'],
                                        end_time=log.timestamp,
                                        duration=duration
                                    )
                                    
                                    event.participants.append(user)
                                    if player_name in username_to_user:
                                        other_user = username_to_user[player_name]
                                        event.participants.append(other_user)
                                        
                                        if player_info['is_friend'] and other_user not in user.friends:
                                            user.friends.append(other_user)
                                            other_user.friends.append(user)
                                    
                                    db.session.add(event)
                                    converted_count += 1
                        else:
                            if world_key in world_sessions and player_name in world_sessions[world_key]['players']:
                                world_sessions[world_key]['players'].pop(player_name)
                
                # 处理当前用户的加入和离开事件
                current_user_sessions = {}
                for log in game_logs:
                    world_key = f"{log.world_name}_{log.world_id}"
                    player_name = log.player_name
                    
                    if log.event_type == '位置变动' and player_name == user.username:
                        current_user_sessions[world_key] = {
                            'start_time': log.timestamp,
                            'world_name': log.world_name,
                            'world_id': log.world_id
                        }
                    
                    elif log.event_type == '玩家离开' and player_name == user.username:
                        if world_key in current_user_sessions:
                            session = current_user_sessions.pop(world_key)
                            
                            if world_key in world_sessions:
                                world_session = world_sessions[world_key]
                                for other_player_name, other_player_info in world_session['players'].items():
                                    if other_player_name == user.username:
                                        continue
                                        
                                    overlap_start = max(
                                        session['start_time'], other_player_info['start_time'])
                                    overlap_end = log.timestamp
                                    
                                    if overlap_start < overlap_end:
                                        duration = int(
                                            (overlap_end - overlap_start).total_seconds())
                                        
                                        world = get_or_create_world(session['world_name'], '')
                                        
                                        # 检查是否已存在相同事件（基于参与者、世界和时间范围）
                                        existing_event = SharedEvent.query.filter(
                                            SharedEvent.world_id == world.id,
                                            SharedEvent.start_time == overlap_start,
                                            SharedEvent.end_time == overlap_end
                                        ).first()
                                        
                                        # 如果没有相同事件，则创建新事件
                                        if not existing_event:
                                            event = SharedEvent(
                                                user_id=user.id,
                                                world_id=world.id,
                                                friend_name=other_player_name.strip(),
                                                start_time=overlap_start,
                                                end_time=overlap_end,
                                                duration=duration
                                            )
                                            
                                            event.participants.append(user)
                                            if other_player_name in username_to_user:
                                                other_user = username_to_user[other_player_name]
                                                event.participants.append(other_user)
                                                
                                                if other_player_info['is_friend'] and other_user not in user.friends:
                                                    user.friends.append(other_user)
                                                    other_user.friends.append(user)
                                            
                                            db.session.add(event)
                                            converted_count += 1
                
                return converted_count
            
            total_events = 0
            for username, user in users.items():
                try:
                    count = process_user_game_logs(user)
                    total_events += count
                except Exception as e:
                    print(f"     ❌ 为 {username} 生成事件失败: {e}")
            
            # 提交所有事件
            db.session.commit()
            
            # 清理重复事件和错误事件
            print("   f. 清理错误事件...")
            all_events = SharedEvent.query.all()
            cleaned_count = 0
            
            for event in all_events:
                participant_usernames = [p.username for p in event.participants]
                
                if (event.friend_name == users[event.user.username].username) or \
                   (len(participant_usernames) == 1 and participant_usernames[0] == event.user.username) or \
                   (len(participant_usernames) == 0):
                    db.session.delete(event)
                    cleaned_count += 1
            
            db.session.commit()
            
            # 匹配事件组
            print("   g. 匹配事件组...")
            from app import match_events_to_groups
            match_events_to_groups()
            
            final_event_count = SharedEvent.query.count()
            print(f"   ✅ 生成了 {final_event_count} 个共享事件")
            
            # =============================================
            # 3. 添加测试评论（整合自add_test_comments.py）
            # =============================================
            print("\n3. 添加测试评论...")
            
            test_comments = [
                "这个事件太棒了！",
                "我还记得那天我们一起玩得很开心。",
                "这个世界真的很有趣，我们下次再一起去。",
                "感谢分享这个事件！",
                "这个经历让我难忘。",
                "希望以后能有更多这样的活动。",
                "这个事件的标签分类很清楚。",
                "我喜欢这个事件的备注信息。",
                "这个世界的环境设计得很精美。",
                "和你一起玩游戏总是很愉快。"
            ]
            
            events = SharedEvent.query.all()
            comment_count = 0
            
            for event in events:
                for i in range(min(3, len(test_comments))):
                    user = users[list(users.keys())[(comment_count) % len(users)]]
                    
                    # 检查是否已存在相同评论（基于事件ID、用户ID和内容）
                    existing_comment = EventComment.query.filter(
                        EventComment.event_id == event.id,
                        EventComment.user_id == user.id,
                        EventComment.content == test_comments[i]
                    ).first()
                    
                    # 如果没有相同评论，则创建新评论
                    if not existing_comment:
                        comment = EventComment(
                            event_id=event.id,
                            user_id=user.id,
                            content=test_comments[i],
                            created_at=datetime.now()
                        )
                        
                        db.session.add(comment)
                        comment_count += 1
                
                test_comments = test_comments[min(3, len(test_comments)):]
                if not test_comments:
                    test_comments = [
                        "这个事件太棒了！",
                        "我还记得那天我们一起玩得很开心。",
                        "这个世界真的很有趣，我们下次再一起去。",
                        "感谢分享这个事件！",
                        "这个经历让我难忘。"
                    ]
            
            db.session.commit()
            print(f"   ✅ 添加了 {comment_count} 条测试评论")
            
            # =============================================
            # 4. 验证数据
            # =============================================
            print("\n4. 验证数据...")
            
            print(f"   a. 用户数量: {User.query.count()}")
            print(f"   b. 世界数量: {World.query.count()}")
            print(f"   c. 游戏日志数量: {GameLog.query.count()}")
            print(f"   d. 共享事件数量: {SharedEvent.query.count()}")
            print(f"   e. 评论数量: {EventComment.query.count()}")
            print(f"   f. 事件组数量: {len(set(event.event_group_id for event in SharedEvent.query.all() if event.event_group_id))}")
            
            # =============================================
            # 5. 完成
            # =============================================
            print("\n🎉 数据添加完成！")
            print("   数据库中已包含所有测试数据：")
            print("   - 用户、世界、游戏日志、共享事件、评论")
            print("   - 双向好友关系")
            print("   - 事件组匹配")
            print("   - 跨事件评论同步")
            print("\n   可以使用以下账户登录测试：")
            print("   - alice / password123")
            print("   - bob / password123")
            print("   - charlie / password123")
            print("   - david / password123")
            print("   - emma / password123")
            print("   - demo / demo")
            
        except Exception as e:
            print(f"   ❌ 数据添加失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
        finally:
            db.session.close()


if __name__ == "__main__":
    seed_database()