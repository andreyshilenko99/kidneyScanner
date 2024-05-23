import asyncio
import multiprocessing
import os
import signal
import sys
from functools import partial
import psutil
from aiogram import Bot

from kidney_scanner.services.bot import BotService
from kidney_scanner.services.image_proc import ImageProcessor
from kidney_scanner.services.file_save import FileSave
from kidney_scanner.services.send import Sender
from kidney_scanner.settings import Config


def core():
    config = Config()

    proc_queue = multiprocessing.Queue()

    bot = Bot(token=config['BOT_TOKEN'])

    bot_service = BotService(bot, proc_queue)

    bot_service.start()

    save_queue = multiprocessing.Queue()

    send_queue = multiprocessing.Queue()

    image_processor = ImageProcessor(bot, proc_queue, save_queue, send_queue)

    image_processor.start()

    file_save = FileSave(save_queue)

    file_save.start()

    sender = Sender(send_queue)

    sender.start()

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(getattr(signal, "SIGINT"),
                            partial(terminate_process,
                                    loop=loop,
                                    bot_service=bot_service,
                                    image_proc=image_processor,
                                    file_save=file_save,
                                    sender=sender


                                    )
                            )
    loop.add_signal_handler(getattr(signal, "SIGTERM"),
                            partial(terminate_process,
                                    loop=loop,
                                    bot_service=bot_service,
                                    image_proc=image_processor,
                                    file_save=file_save,
                                    sender=sender
                                    )
                            )

    return loop


def kill_process(pid):
    p = psutil.Process(pid)
    p.terminate()


def terminate_process(
        loop,
        bot_service,
        image_proc,
        file_save,
        sender

):
    kill_process(bot_service.pid)
    image_proc.stop()
    sender.stop()
    kill_process(file_save.pid)
    os.kill(os.getpid(), signal.SIGHUP)
    kill_process(os.getpid())

    loop.stop()
    sys.exit(0)
