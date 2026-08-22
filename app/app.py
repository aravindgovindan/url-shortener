import os
import string

from flask import Flask, request, jsonify, redirect
import redis
import psycopg2

app = Flask(__name__)

# Define the characters for defining base62 encoding
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

# Define an offset to avoid generating short URLs that are too short
OFFSET = 1998

# connect to Redis
cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
)


def get_db():
    """Connect to the PostgreSQL database for storage"""
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        database=os.environ.get("POSTGRES_DB", "url_shortener"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "password"),
    )
    return conn


def base62_encode(num):
    """Encode a number in Base62"""
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        num, rem = divmod(num, 62)
        result.append(ALPHABET[rem])
    result.reverse()
    return "".join(result)


def base62_decode(code):
    """Decode a Base62 string to a number"""
    num = 0
    for char in code:
        num = num * 62 + ALPHABET.index(char)
    return num
