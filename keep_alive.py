from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "Bảo Huy Đang chạy!"

def run():
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run, daemon=True)
    thread.start()
    logging.info("Keep-alive thread started.")
