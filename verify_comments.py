#!/usr/bin/env python3
"""
验证评论是否能够跨事件组同步显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, SharedEvent, EventComment


def verify_comments():
    """验证评论跨事件组同步显示"""
    with app.app_context():
        # 获取所有事件
        events = SharedEvent.query.all()
        
        # 按事件组分组
        event_groups = {}
        for event in events:
            if event.event_group_id:
                if event.event_group_id not in event_groups:
                    event_groups[event.event_group_id] = []
                event_groups[event.event_group_id].append(event)
        
        print(f"找到 {len(event_groups)} 个事件组:")
        for group_id, group_events in event_groups.items():
            print(f"  - 事件组 {group_id} 包含 {len(group_events)} 个事件: {[event.id for event in group_events]}")
        
        # 验证每个事件组内的评论是否同步
        print("\n开始验证评论同步...")
        
        for group_id, group_events in event_groups.items():
            if len(group_events) < 2:
                continue
            
            print(f"\n验证事件组 {group_id}:")
            
            # 获取事件组内所有事件的ID
            group_event_ids = [event.id for event in group_events]
            
            # 获取事件组内的所有评论
            group_comments = EventComment.query.filter(
                EventComment.event_id.in_(group_event_ids)
            ).order_by(EventComment.created_at.desc()).all()
            
            print(f"  事件组内共有 {len(group_comments)} 条评论")
            
            # 检查每个事件是否能看到所有评论
            for event in group_events:
                # 获取当前事件应该显示的评论（同一事件组内的所有评论）
                comments = EventComment.query.filter(
                    EventComment.event_id.in_(group_event_ids),
                    EventComment.parent_id == None
                ).order_by(EventComment.created_at.desc()).all()
                
                print(f"  - 事件 {event.id} 应该显示 {len(comments)} 条评论")
                
                for comment in comments[:3]:  # 只显示前3条
                    print(f"    - {comment.user.username}: {comment.content[:20]}... (来自事件 {comment.event_id})")
        
        print("\n验证完成！")
        print("现在可以在浏览器中访问事件详情页面，检查评论是否正确显示。")
        print("例如:")
        for event in events[:2]:
            print(f"  - http://localhost:5000/event/{event.id}")


if __name__ == "__main__":
    verify_comments()