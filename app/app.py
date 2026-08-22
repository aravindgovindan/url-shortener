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


@app.route("/shorten", methods=["POST"])
def shorten_url():
    """Grab the long url from the db"""
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    long_url = data["url"]

    # Save to PostgreSQL
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (long_url) VALUES (%s) RETURNING id", (long_url,))
    url_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Encode the id to base62
    short_code = base62_encode(url_id + OFFSET)

    # Cache the mapping in Redis
    cache.set(short_code, long_url)

    return (
        jsonify(
            {
                "short_url": f"http://localhost:5000/{short_code}",
                "short_code": short_code,
            }
        ),
        201,
    )


@app.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    """Redirect to actual url based on the short code"""
    # Check redis cache first
    long_url = cache.get(short_code)

    if long_url:
        print("Cache hit", flush=True)
        return redirect(long_url, code=302)

    # Cache miss - fall back to PostgreSQL
    print("Cache miss", flush=True)
    conn = get_db()
    cur = conn.cursor()
    url_id = base62_decode(short_code) - OFFSET
    cur.execute("SELECT long_url FROM urls WHERE id = %s", (url_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return jsonify({"error": "Short URL not found"}), 404

    # Found the long URL, cache it in Redis for future requests
    long_url = result[0]
    cache.set(short_code, long_url)

    return redirect(long_url, code=302)
