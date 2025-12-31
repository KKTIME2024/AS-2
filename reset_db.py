#!/usr/bin/env python3
"""
重置数据库：清空所有数据并重新初始化表结构
"""

import sys
import os
from app import app, db, User, World, SharedEvent, GameLog, EventGroup, EventTag, EventComment, ActivityFeed, EventReminder, EventShare, user_friends, event_participants


def reset_database():
    """重置数据库，清空所有数据并重新初始化表结构"""
    with app.app_context():
        print("开始重置数据库...")
        
        try:
            # 1. 清空所有数据（按照依赖关系顺序）
            print("1. 清空所有数据...")
            
            # 删除关联表数据
            db.session.execute(event_participants.delete())
            db.session.execute(user_friends.delete())
            
            # 删除所有表数据（按照外键依赖顺序）
            db.session.query(EventComment).delete()
            db.session.query(EventReminder).delete()
            db.session.query(EventShare).delete()
            db.session.query(ActivityFeed).delete()
            db.session.query(EventTag).delete()
            db.session.query(SharedEvent).delete()
            db.session.query(EventGroup).delete()
            db.session.query(GameLog).delete()
            db.session.query(World).delete()
            db.session.query(User).delete()
            
            # 提交删除操作
            db.session.commit()
            print("   ✅ 所有数据已清空")
            
            # 2. 重新创建所有表
            print("2. 重新创建数据库表...")
            db.drop_all()
            db.create_all()
            print("   ✅ 数据库表已重新创建")
            
            print("\n🎉 数据库重置成功！")
            print("   数据库已清空并重新初始化，所有表结构已创建")
            print("   可以运行 seed_data.py 来添加测试数据")
            
        except Exception as e:
            print(f"   ❌ 数据库重置失败: {e}")
            print("   请检查数据库连接和权限")
            import traceback
            traceback.print_exc()
            db.session.rollback()
        finally:
            db.session.close()


if __name__ == "__main__":
    reset_database()