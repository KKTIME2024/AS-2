#!/usr/bin/env python3
"""
检查数据库中评论的状态
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, EventComment, SharedEvent


def check_comments():
    """检查数据库中评论的状态"""
    with app.app_context():
        print("检查数据库中评论的状态...")
        
        # 检查event_comment表是否存在
        try:
            # 尝试查询评论数
            comment_count = EventComment.query.count()
            print(f"event_comment表存在，共有 {comment_count} 条评论")
            
            # 显示前10条评论
            comments = EventComment.query.order_by(EventComment.created_at.desc()).limit(10).all()
            if comments:
                print("\n最近的评论：")
                for comment in comments:
                    print(f"  - 评论ID {comment.id}: {comment.content[:50]}... (用户: {comment.user.username}, 事件: {comment.event_id}, 时间: {comment.created_at})")
            
            # 检查事件组
            print("\n检查事件组：")
            events = SharedEvent.query.all()
            event_group_count = len(set(event.event_group_id for event in events if event.event_group_id))
            print(f"共有 {len(events)} 个事件，分布在 {event_group_count} 个事件组中")
            
            # 检查每个事件组的评论情况
            event_groups = {}
            for event in events:
                if event.event_group_id:
                    if event.event_group_id not in event_groups:
                        event_groups[event.event_group_id] = []
                    event_groups[event.event_group_id].append(event)
            
            for group_id, group_events in event_groups.items():
                if len(group_events) > 1:
                    print(f"\n事件组 {group_id} (包含 {len(group_events)} 个事件):")
                    group_event_ids = [event.id for event in group_events]
                    group_comments = EventComment.query.filter(
                        EventComment.event_id.in_(group_event_ids)
                    ).all()
                    print(f"  组内共有 {len(group_comments)} 条评论")
                    for comment in group_comments[:5]:  # 显示前5条
                        print(f"    - {comment.user.username}: {comment.content[:30]}... (事件 {comment.event_id})")
            
        except Exception as e:
            print(f"检查event_comment表时出错: {e}")
            print("可能是event_comment表不存在或数据库连接有问题")
            
            # 尝试列出所有表
            try:
                print("\n尝试列出所有表：")
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"数据库中的表：{tables}")
            except Exception as e:
                print(f"列出表时出错: {e}")


if __name__ == "__main__":
    check_comments()