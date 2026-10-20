
from collections import defaultdict, deque
from threading import Lock
from time import time

from flask import (
    Flask,
    request,
    render_template_string,
    jsonify,
)

from NewsServer import response

app = Flask(__name__)

# Rate limit configuration
LIMIT = 5
WINDOW = 60
BUCKET_CAPACITY = 5
REFILL_RATE = 1 / 12  # One token every 12 seconds

# Separate state for each client and algorithm
fixed_windows = {}
sliding_windows = defaultdict(deque)
token_buckets = {}

lock = Lock()


def get_client():
    # request.remote_addr is suitable for local development.
    # Configure trusted proxies correctly before deploying publicly.
    return request.remote_addr or "unknown"


def check_rate_limit(algorithm, client):
    now = time()

    with lock:
        if algorithm == "fixed":
            key = (client, algorithm)
            window_start = int(now // WINDOW) * WINDOW

            state = fixed_windows.get(key)

            if state is None or state[0] != window_start:
                state = [window_start, 0]
                fixed_windows[key] = state

            if state[1] >= LIMIT:
                retry_after = window_start + WINDOW - now
                return False, 0, max(1, int(retry_after + 0.999))

            state[1] += 1
            remaining = LIMIT - state[1]

            return True, remaining, 0

        elif algorithm == "sliding":
            key = (client, algorithm)
            timestamps = sliding_windows[key]
            cutoff = now - WINDOW

            # Remove requests outside the rolling time window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= LIMIT:
                retry_after = timestamps[0] + WINDOW - now
                return False, 0, max(1, int(retry_after + 0.999))

            timestamps.append(now)
            remaining = LIMIT - len(timestamps)

            return True, remaining, 0

        elif algorithm == "token":
            key = (client, algorithm)
            tokens, last_update = token_buckets.get(
                key, (BUCKET_CAPACITY, now)
            )

            # Refill tokens according to elapsed time
            tokens = min(
                BUCKET_CAPACITY,
                tokens + (now - last_update) * REFILL_RATE,
            )

            if tokens < 1:
                retry_after = (1 - tokens) / REFILL_RATE
                token_buckets[key] = (tokens, now)

                return False, 0, max(1, int(retry_after + 0.999))

            tokens -= 1
            token_buckets[key] = (tokens, now)

            return True, int(tokens), 0

    return False, 0, 0


def selected_algorithm(value):
    allowed = {"fixed", "sliding", "token"}
    return value if value in allowed else "fixed"


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>News Server | Rate Limiter Lab</title>

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            padding: 30px 16px;
            display: grid;
            place-items: center;
            font-family: Arial, sans-serif;
            color: #e5e7eb;
            background: #0b1120;
        }

        .card {
            width: 100%;
            max-width: 560px;
            padding: 30px;
            border: 1px solid #334155;
            border-radius: 20px;
            background: #172033;
            box-shadow: 0 20px 60px #0005;
        }

        .tag {
            color: #38bdf8;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        h1 { margin-bottom: 8px; }

        .muted {
            color: #94a3b8;
            line-height: 1.5;
        }

        label {
            display: block;
            margin: 24px 0 8px;
            font-weight: bold;
        }

        select, button {
            width: 100%;
            padding: 13px;
            border-radius: 10px;
            font-size: 15px;
        }

        select {
            color: #e5e7eb;
            background: #0f172a;
            border: 1px solid #475569;
        }

        button {
            margin-top: 12px;
            border: 0;
            color: #082f49;
            background: #38bdf8;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover { background: #7dd3fc; }

        .news {
            margin: 24px 0;
            padding: 22px;
            border-radius: 12px;
            background: #0f172a;
            font-size: 21px;
            line-height: 1.5;
            overflow-wrap: anywhere;
        }

        .status {
            margin-top: 16px;
            padding: 13px;
            border-radius: 10px;
            background: #243449;
            line-height: 1.5;
        }

        .error { color: #fca5a5; }
        .success { color: #86efac; }

        .footer {
            margin-top: 22px;
            font-size: 13px;
            color: #94a3b8;
        }
    </style>
</head>
<body>
    <main class="card">
        <div class="tag">● NEWS SERVER / RATE LIMITER LAB</div>
        <h1>Today's News</h1>
        <p class="muted">
            Choose an algorithm and test how it controls your requests.
        </p>

        <form action="/news" method="post">
            <label for="algorithm">Select rate-limiting algorithm</label>

            <select id="algorithm" name="algorithm">
                <option value="fixed"
                    {{ 'selected' if selected == 'fixed' else '' }}>
                    Fixed Window
                </option>
                <option value="sliding"
                    {{ 'selected' if selected == 'sliding' else '' }}>
                    Sliding Window Log
                </option>
                <option value="token"
                    {{ 'selected' if selected == 'token' else '' }}>
                    Token Bucket
                </option>
            </select>

            <button type="submit">Get Random News</button>
        </form>

        {% if news %}
            <div class="news">{{ news }}</div>
        {% endif %}

        {% if message %}
            <div class="status {{ 'error' if error else 'success' }}">
                {{ message }}
            </div>
        {% endif %}

        {% if remaining is not none %}
            <div class="status">
                Requests remaining: <strong>{{ remaining }}</strong>
            </div>
        {% endif %}

        <div class="footer">
            Fixed and sliding windows: 5 requests per 60 seconds.
            Token bucket: capacity 5, refilling at 1 token per 12 seconds.
        </div>
    </main>
</body>
</html>
"""


def render_page(**kwargs):
    return render_template_string(HTML, **kwargs)


@app.route("/")
def home():
    return render_page(
        selected="fixed",
        news=None,
        message=None,
        error=False,
        remaining=None,
    )


@app.route("/news", methods=["POST"])
def get_news():
    algorithm = selected_algorithm(request.form.get("algorithm", "fixed"))
    allowed, remaining, retry_after = check_rate_limit(
        algorithm, get_client()
    )

    if not allowed:
        return render_page(
            selected=algorithm,
            news=None,
            message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            error=True,
            remaining=0,
        ), 429

    return render_page(
        selected=algorithm,
        news=response(),
        message="Request allowed!",
        error=False,
        remaining=remaining,
    )


@app.route("/api/news")
def api_news():
    algorithm = selected_algorithm(request.args.get("algorithm", "fixed"))
    allowed, remaining, retry_after = check_rate_limit(
        algorithm, get_client()
    )

    if not allowed:
        result = jsonify({
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "algorithm": algorithm,
            "retry_after_seconds": retry_after,
        })
        result.status_code = 429
        result.headers["Retry-After"] = str(retry_after)
        return result

    result = jsonify({
        "news": response(),
        "algorithm": algorithm,
        "remaining": remaining,
    })
    result.headers["X-RateLimit-Remaining"] = str(remaining)
    return result


if __name__ == "__main__":
    app.run(debug=True)
