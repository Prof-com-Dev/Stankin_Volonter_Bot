from aiogram import Bot, Dispatcher, types, executor
from pyqrcode import *
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def starter(msg: types.Message):
    await msg.answer('Здравствуй, препод! '
                     '\n Меня зовут Унылый Сглыпа! '
                     '\n Я генерирую qr-коды для различных целей '
                     '\n Напиши что-нибудь, я сделаю из этого QR-код')

@dp.message_handler()
async def send_new_qr_code(msg: types.Message):
    await msg.answer('Ваш текст принят на обработку! \n Пожалуйста, подождите')
    qr_code = create(msg.text)
    qr_code.png('qr_code.png', scale=6)

    with open('qr_code.png', 'rb') as code:
        await bot.send_photo(msg.chat.id, code)
        await bot.send_message(msg.chat.id, 'ВАш QR-код готов. '
                    '\n Вы можете прислать еще текст для генирации и обработки')

executor.start_polling(dp)


