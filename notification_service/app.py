import redis
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

REDIS_HOST = "redis"
REDIS_PORT = 6379
CHANNEL = "orders"


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")


def run_health_server():
    server = HTTPServer(("0.0.0.0", 8081), HealthHandler)
    server.serve_forever()


def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    time.sleep(1)

    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)

    print(f"[NotificationService] Подписан на канал {CHANNEL}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            print(f"[NotificationService] заказ #{data['id']} {data['item']} {data['price']}")


if __name__ == "__main__":
    main()