import multiprocessing

from kidney_scanner.logs import Logger


class FileSave(multiprocessing.Process):
    def __init__(self, save_queue):
        multiprocessing.Process.__init__(self)
        self.save_queue = save_queue
        self.logger = Logger()
        self.status = True
        self.daemon = False

    def run(self) -> None:
        while True:
            try:
                if not self.status:
                    self.logger.info(f'FileSave shutdown')
                msg = self.save_queue.get()
                if msg['type'] == 'origin':
                    with open(msg['filename'], 'wb') as file:
                        file.write(msg['data'])
                elif msg['type'] == 'processed':
                    with open(msg['filename'], 'wb') as file:
                        file.write(msg['data'])
                    with open(msg['txt_filename'], 'w') as file:
                        for element in msg['coords']:
                            file.write(str(element) + '\n')
            except Exception as e:
                self.logger.error(f"Error in FileSave: {e}")
