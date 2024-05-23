import threading

import requests

from kidney_scanner.logs import Logger
from kidney_scanner.settings import Config


class Sender(threading.Thread):
    def __init__(self, send_queue):
        threading.Thread.__init__(self)
        self.send_queue = send_queue
        self.config = Config()
        self.logger = Logger()
        self.status = True
        self.daemon = False

    def run(self) -> None:
        while True:
            try:
                if not self.status:
                    self.logger.info(f'Sender shutdown')
                message = self.send_queue.get()
                # self.bot.send_photo(chat_id=message['tg_id'], photo=message['data'])
                url = f'https://api.telegram.org/bot{self.config["BOT_TOKEN"]}/sendPhoto'
                files = {'photo': message['data']}
                data = {'chat_id': message['tg_id']}

                response = requests.post(url, files=files, data=data)
                if response.status_code == 200:
                    self.logger.info("Image sent successfully")
                else:
                    self.logger.error(f"Failed to send image. Status code: {response.status_code}")
            except Exception as e:
                self.logger.error(f"Error in Sender: {e}")