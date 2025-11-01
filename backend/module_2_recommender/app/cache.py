# /module_2_recommender/app/cache.py
import redis
import json
import os

# Nama service dari docker-compose
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = 6379
CACHE_TTL_SEC = 6 * 60 * 60 # Cache 6 Jam

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    redis_client.ping()
    print("Koneksi Redis sukses.")
except Exception as e:
    print(f"Gagal koneksi ke Redis: {e}")
    redis_client = None

def get_recommendations(user_id: str):
    if not redis_client:
        return None
    try:
        data = redis_client.get(f"recs:{user_id}")
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Error GET cache Redis: {e}")
        return None

def set_recommendations(user_id: str, package_ids: list):
    if not redis_client:
        return
    try:
        redis_client.setex(f"recs:{user_id}", CACHE_TTL_SEC, json.dumps(package_ids))
    except Exception as e:
        print(f"Error SET cache Redis: {e}")