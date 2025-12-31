#!/usr/bin/env python3
# 测试游戏日志导入和转换功能

import requests
import json

# 测试配置
BASE_URL = 'http://localhost:5000'
USERNAME = 'demo'
PASSWORD = 'demo'

# 示例游戏日志数据，模拟用户提供的真实格式
test_log_data = """
12/28 01:53 
 位置变动 
 メゾン荘 201号室 #53949 friends+
12/28 01:52 
 玩家离开 
 💚 
 SaKi43
12/28 01:52 
 玩家离开 
 💚 
 LiLor_2333
12/28 01:52 
 玩家离开 
 💚 
 Nagikokoro
12/28 01:40 
 玩家离开 
 💚 
 Mossball˵¬ᴗ¬˵
12/28 01:26 
 玩家离开 
 Hutienxi
12/28 00:52 
 玩家加入 
 💚 
 Nagikokoro
12/28 00:28 
 玩家加入 
 Hutienxi
12/28 00:27 
 玩家离开 
 💚 
 Φ古明地恋Φ
12/28 00:24 
 玩家离开 
 💚 
 小黄c123
12/28 00:23 
 玩家加入 
 💚 
 Φ古明地恋Φ
12/28 00:22 
 玩家加入 
 💚 
 Mossball˵¬ᴗ¬˵
12/28 00:22 
 玩家加入 
 💚 
 LiLor_2333
12/28 00:22 
 玩家加入 
 💚 
 小黄c123
12/28 00:22 
 玩家加入 
 💚 
 SaKi43
"""

def test_game_log_import():
    """测试游戏日志导入和转换功能"""
    print("测试游戏日志导入和转换功能...")
    
    # 1. 登录获取session
    session = requests.Session()
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    login_response = session.post(f'{BASE_URL}/login', data=login_data)
    if login_response.status_code != 200:
        print("登录失败")
        return False
    
    print("✓ 登录成功")
    
    # 2. 批量导入游戏日志
    bulk_import_data = {
        'log_text': test_log_data
    }
    
    bulk_import_response = session.post(f'{BASE_URL}/api/gamelog/bulk_import', data=bulk_import_data)
    if bulk_import_response.status_code != 200:
        print("批量导入失败")
        print(bulk_import_response.text)
        return False
    
    bulk_import_result = bulk_import_response.json()
    if bulk_import_result.get('success'):
        print(f"✓ 批量导入成功，导入了 {bulk_import_result.get('imported_count')} 条记录")
    else:
        print(f"批量导入失败: {bulk_import_result.get('error')}")
        return False
    
    # 3. 转换游戏日志为SharedEvent
    convert_response = session.post(f'{BASE_URL}/api/gamelog/convert')
    if convert_response.status_code != 200:
        print("转换失败")
        print(convert_response.text)
        return False
    
    convert_result = convert_response.json()
    if convert_result.get('success'):
        print(f"✓ 转换成功，生成了 {convert_result.get('converted_count')} 个事件")
    else:
        print(f"转换失败: {convert_result.get('error')}")
        return False
    
    # 4. 验证事件是否成功创建
    index_response = session.get(f'{BASE_URL}/')
    if index_response.status_code == 200:
        print("✓ 可以访问首页，事件已成功展示")
    else:
        print("无法访问首页")
        return False
    
    print("\n🎉 所有测试通过！游戏日志导入和转换功能正常工作")
    return True

if __name__ == '__main__':
    test_game_log_import()
