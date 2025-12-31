import requests
import json

# 测试搜索功能
def test_search():
    url = 'http://localhost:5000/'
    
    # 测试用例：搜索好友名字
    test_cases = [
        'alice',  # 测试搜索好友名字
        'bob',    # 测试搜索另一个好友名字
        'The Black Cat'  # 测试搜索世界名字
    ]
    
    print("=== 测试搜索功能 ===")
    
    for query in test_cases:
        try:
            # 构造请求URL
            full_url = f'{url}?search={query}'
            
            # 添加登录Cookie（如果需要）
            cookies = {
                # 这里需要根据实际情况添加登录Cookie
                # 例如：'session': 'your_session_cookie'
            }
            
            response = requests.get(full_url, cookies=cookies)
            print(f"\n测试查询: '{query}'")
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✓ 搜索请求成功")
                print(f"响应内容长度: {len(response.text)} 字符")
                
                # 检查响应中是否包含搜索关键词
                if query.lower() in response.text.lower():
                    print(f"✓ 响应内容中包含搜索关键词 '{query}'")
                else:
                    print(f"✗ 响应内容中未找到搜索关键词 '{query}'")
                
            else:
                print(f"✗ 搜索请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    test_search()