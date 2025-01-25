import redis

# Connect to Redis
redis_client = redis.StrictRedis(
    host='host.docker.internal',
    port=6379,
    decode_responses=True  # Decodes responses to strings
)

print(redis_client.info())

# Test the connection
try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis.")