import dotenv

import asyncio

import logging
import os

from aiogram import types, F, Bot, Dispatcher
from aiogram.filters import Command
import zipfile

dotenv.load_dotenv()
from utils import downloader, upload_file_to_yandex_disk, walker, clear_static, zip_folder

bot = Bot(token=os.environ['TOKEN'])
dp = Dispatcher()

logging.root.handlers.clear()

logging.basicConfig(level=logging.WARNING, filename="logs.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s\n" + '_' * 100)


async def start(message: types.Message):
    await message.answer('Привет, пришли сюда архив с фотографиями и я распознаю на них весь тест')


async def get_document(message: types.Message):
    mes = await message.answer("⬇️ Скачиваем файлы...")
    filename = downloader(message.text)

    if not filename.endswith(".zip"):
        return await message.answer("Мы принимаем только архивы с расширением zip")

    await mes.edit_text("📦 Распаковываем файлы...")
    if not os.path.isdir('static/' + filename[:-4]):
        with zipfile.ZipFile('static/' + filename, 'r') as zip_ref:
            zip_ref.extractall('static/' + filename[:-4])

    await mes.edit_text("🔍 Распознаем файлы...")
    await walker('static/' + filename[:-4], 'static/' + filename[:-4] + '_done', mes)

    await mes.edit_text("📦 Упаковываем файлы...")
    zip_folder('static/' + filename[:-4] + '_done', 'static/' + filename[:-4] + '_done.zip')

    await mes.edit_text("⬆️ Загружаем файлы...")
    url = upload_file_to_yandex_disk('static/' + filename[:-4] + '_done.zip', f'disk:/recognizer/{filename}')

    # clear_static(filename[:-4])
    await mes.edit_text('✅ Все готово!\n\n'
                        f'Вы можете загрузить архив <a href="{url}">по этой ссылке</a>', parse_mode='HTML')


@dp.startup()
async def on_start():
    commands = [types.BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands)


@dp.shutdown()
async def on_final():
    await bot.session.close()


async def main():
    dp.message.register(start, Command('start'))
    dp.message.register(get_document, F.text.startswith('https'))

    print('Start...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
