#!/usr/bin/env python3
"""
添加测试评论，模拟不同账户对不同事件的留言
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, SharedEvent, User, EventComment
from datetime import datetime


def add_test_comments():
    """添加测试评论"""
    with app.app_context():
        # 获取所有用户
        users = User.query.all()
        print(f"找到 {len(users)} 个用户:")
        for user in users:
            print(f"  - {user.username} (ID: {user.id})")
        
        # 获取所有事件
        events = SharedEvent.query.all()
        print(f"\n找到 {len(events)} 个事件:")
        for event in events:
            print(f"  - 事件 {event.id}: {event.friend_name} 在 {event.world.world_name} (创建者: {event.user.username}, 事件组: {event.event_group_id})")
        
        if len(users) < 2:
            print("\n需要至少2个用户来模拟跨账户交互")
            return
        
        if len(events) < 2:
            print("\n需要至少2个事件来模拟多事件交互")
            return
        
        # 定义测试评论内容
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
        
        # 为每个事件添加来自不同用户的评论
        print("\n开始添加测试评论...")
        comment_count = 0
        
        for event in events:
            # 为每个事件添加2-3条评论
            for i in range(min(3, len(test_comments))):
                # 轮流使用不同的用户
                user = users[(comment_count) % len(users)]
                
                # 创建评论
                comment = EventComment(
                    event_id=event.id,
                    user_id=user.id,
                    content=test_comments[i],
                    created_at=datetime.now()
                )
                
                db.session.add(comment)
                comment_count += 1
                print(f"  - 添加评论: {user.username} 对事件 {event.id} 说: {test_comments[i]}")
            
            # 移除已使用的评论，确保多样性
            test_comments = test_comments[min(3, len(test_comments)):]
            if not test_comments:
                test_comments = [
                    "这个事件太棒了！",
                    "我还记得那天我们一起玩得很开心。",
                    "这个世界真的很有趣，我们下次再一起去。",
                    "感谢分享这个事件！",
                    "这个经历让我难忘。"
                ]
        
        # 提交所有更改
        db.session.commit()
        print(f"\n成功添加 {comment_count} 条测试评论！")
        
        # 验证评论是否添加成功
        total_comments = EventComment.query.count()
        print(f"\n当前系统中共有 {total_comments} 条评论")


if __name__ == "__main__":
    add_test_comments()