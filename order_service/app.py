import redis
import json
import time
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

REDIS_HOST = 'redis'
REDIS_PORT = 6379
CHANNEL = "orders"

# флаг для демонстрации livenessProbe
FAIL_HEALTH = False  # True = сломать /health, False = нормальная работа

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            if FAIL_HEALTH:
                self.send_response(500)  # временно ломаем сервис
                self.end_headers()
                self.wfile.write(b"FAIL")
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")


def run_health_server():
    server = HTTPServer(("0.0.0.0", 8000), HealthHandler)
    server.serve_forever()


def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    time.sleep(2)

    while True:
        with open('orders.json', "r") as f:
            orders = json.load(f)

        for order in orders:
            r.publish(CHANNEL, json.dumps(order))
            print(f"[OrderService] Отправлен заказ: {order}")

            delay = random.randint(1, 3)
            time.sleep(delay)

        print("[OrderService] Все заказы отправлены")
        time.sleep(10)


if __name__ == "__main__":
    main()