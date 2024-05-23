import asyncio
import io
import multiprocessing

from aiogram import Dispatcher, types

from kidney_scanner.logs import Logger
from kidney_scanner.settings import Config


class BotService(multiprocessing.Process):

    def __init__(self, bot, proc_queue):

        multiprocessing.Process.__init__(self)
        self.daemon = False
        self.status = True
        self.bot = bot
        self.config = Config()
        self.proc_queue = proc_queue
        self.logger = Logger()
        self.dp = Dispatcher()

    def run(self):
        try:
            @self.dp.message()
            async def handle_image(message: types.Message):
                if message.photo:
                    image = io.BytesIO()
                    print(type(image))
                    await self.bot.download(
                        message.photo[-1],
                        destination=image
                    )
                    msg = {'data': image, 'tg_id': message.chat.id}
                    self.proc_queue.put(msg)
                else:
                    await message.reply("Please send an image to save.")

            async def start_polling():
                await self.dp.start_polling(self.bot)

            asyncio.run(start_polling())
        except Exception as e:
            self.logger.exception(f'BotService: {e}')

    def stop(self):
        self.logger.info(f'BotService down')
        self.status = False
