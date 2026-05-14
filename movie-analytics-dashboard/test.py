from services.streaming.analytics.realtime_analytics import (
    get_trending_movies,
    get_hot_genres,
    get_active_users,
    get_live_searches,
    get_live_events
)

print("\n=== TRENDING MOVIES ===")
print(get_trending_movies())

print("\n=== HOT GENRES ===")
print(get_hot_genres())

print("\n=== ACTIVE USERS ===")
print(get_active_users())

print("\n=== LIVE SEARCHES ===")
print(get_live_searches())

print("\n=== LIVE EVENTS ===")
print(get_live_events())