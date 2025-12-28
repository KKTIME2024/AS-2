import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/vrchat_memories.db')
cursor = conn.cursor()

print("=== Database Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n=== Users ===")
cursor.execute("SELECT id, username FROM user;")
users = cursor.fetchall()
for user in users:
    print(f"- {user[0]}: {user[1]}")

print("\n=== Worlds ===")
cursor.execute("SELECT id, world_name FROM world;")
worlds = cursor.fetchall()
for world in worlds:
    print(f"- {world[0]}: {world[1]}")

print("\n=== Shared Events ===")
cursor.execute("SELECT COUNT(*) FROM shared_event;")
event_count = cursor.fetchone()[0]
print(f"Total events: {event_count}")

if event_count > 0:
    cursor.execute("SELECT id, friend_name, world_id, start_time FROM shared_event LIMIT 3;")
    events = cursor.fetchall()
    print("Sample events:")
    for event in events:
        print(f"- {event[0]}: With {event[1]} in world {event[2]} at {event[3]}")

conn.close()