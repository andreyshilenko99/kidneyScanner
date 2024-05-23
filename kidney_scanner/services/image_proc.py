import datetime
import threading

import cv2
import numpy as np
from kidney_scanner.logs import Logger
from kidney_scanner.settings import Config
from kidney_scanner.utils import process_image_and_get_bytes


class ImageProcessor(threading.Thread):
    def __init__(self, bot, proc_queue, save_queue, send_queue):
        self.bot = bot
        threading.Thread.__init__(self)
        self.proc_queue = proc_queue
        self.save_queue = save_queue
        self.send_queue = send_queue
        self.config = Config()
        self.logger = Logger()
        self.status = True
        self.daemon = False

    def run(self) -> None:
        while True:
            try:
                if not self.status:
                    self.logger.info(f'ImageProcessor shutdown')
                _time = datetime.datetime.now()
                origin_filename = f"{self.config['ORIGIN_SAVE_PATH']}/{_time}.jpg"
                photo_data = self.proc_queue.get()
                image_bytes = photo_data['data'].read()
                self.save_queue.put({'filename': origin_filename, 'data': image_bytes, 'type': 'origin'})
                decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
                proc_image_bytes, coords = process_image_and_get_bytes(self.config, decoded)
                proc_filename = f"{self.config['PROCESSES_SAVE_PATH']}/{_time}.png"
                txt_filename = f"{self.config['TXT_SAVE_PATH']}/{_time}.txt"
                self.save_queue.put({'filename': proc_filename, 'data': proc_image_bytes, 'coords': coords,
                                     'type': 'processed', 'txt_filename': txt_filename})
                self.send_queue.put({'data': proc_image_bytes, 'tg_id': photo_data['tg_id']})

            except Exception as e:
                self.logger.error(f"Error in ImageProcessor: {e}")




