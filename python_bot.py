import telebot
import json
from random import choice

def open_json():
    global user_data
    with open('user_data.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    return user_data

def dump_json():
    global user_data
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def random_description(d):
    key = choice(list(d.keys()))
    return key, d[key]

token = '8751219621:AAHraCTQWKBXy3pZGuOeOhq1fPlE6_29JpQ'
bot = telebot.TeleBot(token)

user_data = open_json()

@bot.message_handler(commands=['start'])
def start_message(message):
    print(message)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}, это бот поможет выучить базовый синтаксис python')
    # bot.delete_message(message.chat.id, message.id)

@bot.message_handler(commands=['learn'])
def handle_learn(message):
    print(message)
    id = message.from_user.id
    user_dict = user_data.get(str(id), {})
    if not user_dict:
        bot.send_message(message.chat.id, 'Произошла ошибка: Твой словарь пуст. Добавь слова с помощью команды (/addword print вывод в консоль)')
        return
    print(user_dict)
    try:
        words_left = int(message.text.lower().split()[1])
        correct = 0
        amount = words_left
        ask_transl(message, user_dict, words_left, correct, amount)

    except Exception as e:
        bot.send_message(id, f'Произошла ошибка: {e}')

def ask_transl(message, user_dict, words_left, correct, amount):
    chat_id = message.chat.id
    if words_left > 0:
        word, desc = random_description(user_dict)
        bot.send_message(chat_id, f'Значение: {desc}. Введи термин')
        print(word, desc)
        bot.register_next_step_handler_by_chat_id(chat_id, check_transl, word, words_left, correct, amount)
    else:
        bot.send_message(chat_id, f'Тест окончен. Ты решил правильно {correct}/{amount} терминов')

def check_transl(message, correct_trans, words_left, correct, amount):
    user_ans = message.text.lower()
    print(user_ans)
    if user_ans == correct_trans:
        bot.send_message(message.chat.id, 'Правильно!')
        correct += 1
    else:
        bot.send_message(message.chat.id, 'Неправильно! Иди учись')
    ask_transl(message, user_data[str(message.from_user.id)], words_left - 1, correct, amount)


@bot.message_handler(commands=['help'])
def handle_help(message):
    print(message)
    bot.send_message(message.chat.id, 'Добро пожаловать! Я бот чтобы изучить базовый синтаксис Python!')
    bot.send_message(message.chat.id, 'Список доступных команд:\n/start - Начать\n/help - Информация о боте\n/learn - Пройти тест. Ввод через пробел(команда кол-во слов)\n/addword - Добавить слово. Ввод через пробел(команда слово описание)\n/showlist - посмотреть словарь добавленных терминов')
    bot.send_message(message.chat.id, 'Создан мной')

@bot.message_handler(commands=['addword'])
def handle_add_word(message):
    global user_data
    id = message.from_user.id
    user_dict = user_data.get(str(id), {})
    try:
        words = message.text.lower().split()[1:]
        print(words)
        word, translate = words[0], ' '.join(words[1:])
        if translate == "":
            bot.send_message(id, f'Произошла ошибка: Отсутствие описания. Пример ввода: /addword print вывод в консоль')
            return
        user_dict[word] = translate
        user_data[str(id)] = user_dict
        dump_json()
        bot.send_message(message.chat.id, 'Успешно добавлено!')
        print(user_dict)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка : {e}')

@bot.message_handler(commands=['showlist'])
def show_list(message):
    user_dict = user_data.get(str(message.from_user.id), {})
    bot.send_message(message.chat.id, 'Вот твой словарь синтаксиса python:')
    for word, desc in user_dict.items():
        bot.send_message(message.chat.id, text=f'Термин: {word}, значение: {desc}')

    if not user_dict:
        bot.send_message(message.chat.id, 'Твой словарь пуст. Добавь что-нибудь с помощью /addword')

# @bot.message_handler(func=lambda message: True) # если сообщение не пустое, то выполняется функция
# def handle_all(message):
#     print(message)
#     if message.text.lower() in ('как дела',  'как дела?'):
#         bot.send_message(message.chat.id, text='Все ок')
#     else:
#         bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True) # запускается процесс прослушивания событий