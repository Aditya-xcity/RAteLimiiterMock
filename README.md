# Rate Limiter Lab

A Flask-based rate limiter simulation built to understand and compare three common rate-limiting algorithms: Fixed Window, Sliding Window Log, and Token Bucket.

The project provides a simple web interface and a JSON API to demonstrate how rate limiters control incoming requests, track client usage, and reject requests when limits are exceeded.

## Overview

Rate limiting is a technique used to control how frequently a client can access a service within a given period. It helps prevent excessive requests, protects server resources, and improves service stability.

This project implements three algorithms so their behavior can be explored and compared in a practical environment.

## Implemented Algorithms

### 1. Fixed Window Counter

- Allows a maximum of 5 requests per 60-second window.
- Divides time into fixed intervals.
- Resets the request counter when a new window begins.
- Simple to implement, but can allow a burst of requests around window boundaries.

### 2. Sliding Window Log

- Allows a maximum of 5 requests within any rolling 60-second period.
- Stores the timestamp of each accepted request.
- Removes timestamps that fall outside the rolling window.
- Provides more precise enforcement than a fixed window, but requires storing request timestamps.

### 3. Token Bucket

- Has a maximum capacity of 5 tokens.
- Refills at a rate of 1 token every 12 seconds.
- Each accepted request consumes one token.
- Allows short bursts of requests while controlling the long-term request rate.

## Features

- Three selectable rate-limiting algorithms.
- Web interface for testing requests interactively.
- JSON API for programmatic testing.
- Per-client rate-limit tracking using the client's IP address.
- HTTP 429 responses when the request limit is exceeded.
- `Retry-After` response header for rejected API requests.
- Remaining-request information for accepted requests.
- Thread synchronization using Python's `Lock`.

## Tech Stack

- Python
- Flask
- HTML and CSS
- Python standard library (`collections`, `threading`, `time`, and `random`)

## Project Structure

```text
rate-limiter-lab/
├── app.py
├── NewsServer.py
└── README.md
```

- `app.py`: Flask application, rate-limiting algorithms, web interface, and API endpoints.
- `NewsServer.py`: Contains sample news messages and the function that returns a random message.
- `README.md`: Project documentation.

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd rate-limiter-lab
```

Replace `<your-repository-url>` with your Git repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install Flask
```

## Running the Application

Start the Flask server:

```bash
python app.py
```

Open the following URL in your browser:

```text
http://127.0.0.1:5000/
```

Select a rate-limiting algorithm and click **Get Random News** to send requests and observe how the selected algorithm behaves.

## API Usage

The project also provides a JSON endpoint for testing rate limiting without using the web interface.

### Endpoint

```http
GET /api/news
```

### Select an algorithm

Fixed Window:

```http
GET /api/news?algorithm=fixed
```

Sliding Window Log:

```http
GET /api/news?algorithm=sliding
```

Token Bucket:

```http
GET /api/news?algorithm=token
```

If no algorithm is specified, the application uses Fixed Window by default.

### Successful Response

Example:

```json
{
  "news": "aaj lab cancel ho gayi",
  "algorithm": "fixed",
  "remaining": 4
}
```

The `remaining` field indicates how many additional requests the selected algorithm currently allows.

### Rate Limit Exceeded

When the limit is exceeded, the API returns HTTP status `429 Too Many Requests`.

Example:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "algorithm": "fixed",
  "retry_after_seconds": 42
}
```

The response also includes a `Retry-After` header indicating how many seconds the client should wait before retrying.

## How to Test

1. Start the application.
2. Open the web interface or call the API.
3. Select one algorithm.
4. Send repeated requests and observe the remaining-request count.
5. Continue sending requests until the server returns HTTP 429.
6. Observe the retry time and test again after waiting.
7. Repeat the experiment with the other algorithms.
8. Compare how each algorithm handles request bursts and time windows.

For API testing, you can use a browser, Postman, or curl.

Example:

```bash
curl -i "http://127.0.0.1:5000/api/news?algorithm=fixed"
```

To observe rate limiting, send multiple requests to the same endpoint using the same client IP address.

## Comparison

| Property | Fixed Window | Sliding Window Log | Token Bucket |
|---|---|---|---|
| Tracking method | Request counter | Request timestamps | Available tokens |
| Time behavior | Fixed intervals | Rolling time window | Continuous refill |
| Allows bursts | Yes, especially at window boundaries | Within the configured limit | Yes, up to bucket capacity |
| Memory usage | Low | Higher as timestamps are stored | Low |
| Implementation complexity | Low | Moderate | Moderate |

## Limitations

This project is intended for educational purposes and local experimentation.

- Rate-limit state is stored in process memory and is lost when the application restarts.
- Multiple application worker processes will not share their counters.
- Client identification uses `request.remote_addr`, which may not identify the original client correctly behind a reverse proxy.
- The implementation does not use a shared storage system such as Redis.
- The Flask development server and debug mode are not intended for production deployment.
- The API currently uses IP-based tracking rather than authenticated user identities or API keys.

## Learning Objectives

Through this project, the goal is to understand:

- Why rate limiting is needed in backend systems.
- How different rate-limiting algorithms manage request frequency.
- How HTTP 429 responses communicate rate-limit violations.
- How retry information can be returned to clients.
- How shared state, concurrency, and deployment architecture affect rate limiting.
- Why production systems often require centralized storage and distributed rate-limiting strategies.

## Future Improvements

- Add automated tests for each algorithm.
- Add a request simulator to generate bursts and timed requests.
- Visualize token refills and request counts.
- Introduce Redis for shared state across workers.
- Add configurable limits and window sizes.
- Compare memory usage and algorithm behavior under different workloads.


