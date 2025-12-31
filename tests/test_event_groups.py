from app import app, db, SharedEvent, EventGroup, EventLike

with app.app_context():
    # 查询所有事件组
    event_groups = EventGroup.query.all()
    print(f"\n事件组数量: {len(event_groups)}")

    # 打印每个事件组的信息
    for i, group in enumerate(event_groups, 1):
        print(f"\n事件组 {i} ({group.id}):")
        print(f"  创建时间: {group.created_at}")
        print(f"  关联事件数: {len(group.events)}")
        print(f"  关联点赞数: {len(group.likes)}")

        # 打印关联的事件
        for event in group.events:
            print(f"    事件 {event.id}:")
            print(f"      用户: {event.user.username}")
            print(f"      世界: {event.world.world_name}")
            print(f"      好友: {event.friend_name}")
            print(f"      时间: {event.start_time} - {event.end_time}")

    # 查询所有事件
    events = SharedEvent.query.all()
    print(f"\n\n所有事件 ({len(events)}):")
    for event in events:
        print(f"\n事件 {event.id}:")
        print(f"  用户: {event.user.username}")
        print(f"  世界: {event.world.world_name}")
        print(f"  好友: {event.friend_name}")
        print(f"  时间: {event.start_time} - {event.end_time}")
        print(f"  事件组ID: {event.event_group_id}")
        print(f"  点赞数: {len(event.likes)}")
