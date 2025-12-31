import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=== Testing VRChat Memory Keeper Functionality ===\n")

def test_login():
    print("1. Testing Login Functionality")
    login_data = {
        'username': 'demo',
        'password': 'demo'
    }
    
    response = requests.post(f'{BASE_URL}/login', data=login_data)
    
    if response.status_code == 302:
        cookies = response.cookies
        print("✅ Login successful!")
        return cookies
    else:
        print("❌ Login failed!")
        return None

def test_register():
    print("\n2. Testing Register Functionality")
    register_data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    
    response = requests.post(f'{BASE_URL}/register', data=register_data)
    
    if response.status_code == 302:
        print("✅ Register successful!")
        return True
    else:
        print("❌ Register failed!")
        return False

def test_like_functionality(cookies):
    print("\n3. Testing Like Functionality")
    
    # Get events from timeline
    response = requests.get(f'{BASE_URL}/', cookies=cookies)
    if response.status_code != 200:
        print("❌ Failed to get events")
        return False
    
    # Try to like the first event (ID=1)
    event_id = 1
    response = requests.post(f'{BASE_URL}/api/event/{event_id}/like', cookies=cookies, headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Like successful! Current likes: {data['likes']}")
        return True
    else:
        print(f"❌ Like failed! Status code: {response.status_code}")
        return False

def test_add_tag_functionality(cookies):
    print("\n4. Testing Add Tag Functionality")
    
    event_id = 1
    tag_data = {
        'tag_name': 'test-tag'
    }
    
    response = requests.post(f'{BASE_URL}/event/{event_id}/tags', data=tag_data, cookies=cookies)
    
    if response.status_code == 302:
        print("✅ Add tag successful!")
        return True
    else:
        print(f"❌ Add tag failed! Status code: {response.status_code}")
        return False

def test_timeline_access(cookies):
    print("\n5. Testing Timeline Access")
    
    response = requests.get(f'{BASE_URL}/', cookies=cookies)
    
    if response.status_code == 200:
        print("✅ Timeline access successful!")
        return True
    else:
        print(f"❌ Timeline access failed! Status code: {response.status_code}")
        return False

def test_event_detail_access(cookies):
    print("\n6. Testing Event Detail Access")
    
    event_id = 1
    response = requests.get(f'{BASE_URL}/event/{event_id}', cookies=cookies)
    
    if response.status_code == 200:
        print("✅ Event detail access successful!")
        return True
    else:
        print(f"❌ Event detail access failed! Status code: {response.status_code}")
        return False

# Run all tests
if __name__ == "__main__":
    # Test login first
    cookies = test_login()
    
    if cookies:
        test_register()
        test_like_functionality(cookies)
        test_add_tag_functionality(cookies)
        test_timeline_access(cookies)
        test_event_detail_access(cookies)
        
    print("\n=== Testing Complete ===")
