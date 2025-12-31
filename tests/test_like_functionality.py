#!/usr/bin/env python3
"""
测试点赞功能的脚本
"""

import requests
from requests import Session

def test_like_functionality():
    """测试点赞功能"""
    base_url = "http://127.0.0.1:5000"
    session = Session()
    
    # 1. 登录系统
    print("1. 尝试登录...")
    login_data = {
        "username": "alice",
        "password": "password123"
    }
    login_response = session.post(f"{base_url}/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        print(login_response.text)
        return False
    
    print("登录成功")
    
    # 2. 获取事件列表
    print("\n2. 获取事件列表...")
    index_response = session.get(f"{base_url}/")
    
    if index_response.status_code != 200:
        print(f"获取事件列表失败: {index_response.status_code}")
        return False
    
    print("获取事件列表成功")
    
    # 3. 测试点赞API
    print("\n3. 测试点赞API...")
    event_id = 1  # 假设第一个事件的ID是1
    
    # 3.1 点赞事件
    print(f"   3.1 点赞事件 {event_id}...")
    like_response = session.post(f"{base_url}/api/event/{event_id}/like")
    
    if like_response.status_code != 200:
        print(f"点赞失败: {like_response.status_code}")
        print(like_response.text)
        return False
    
    like_data = like_response.json()
    print(f"   点赞成功，当前点赞数: {like_data['likes']}")
    
    # 3.2 检查点赞状态
    print(f"   3.2 检查事件 {event_id} 的点赞状态...")
    status_response = session.get(f"{base_url}/api/event/{event_id}/like/status")
    
    if status_response.status_code != 200:
        print(f"获取点赞状态失败: {status_response.status_code}")
        print(status_response.text)
        return False
    
    status_data = status_response.json()
    print(f"   点赞状态: {status_data['is_liked']}, 点赞数: {status_data['likes']}")
    
    # 3.3 取消点赞
    print(f"   3.3 取消点赞事件 {event_id}...")
    unlike_response = session.delete(f"{base_url}/api/event/{event_id}/like")
    
    if unlike_response.status_code != 200:
        print(f"取消点赞失败: {unlike_response.status_code}")
        print(unlike_response.text)
        return False
    
    unlike_data = unlike_response.json()
    print(f"   取消点赞成功，当前点赞数: {unlike_data['likes']}")
    
    print("\n✅ 点赞功能测试通过！")
    return True

if __name__ == "__main__":
    test_like_functionality()
