from Vkinder import *
from keyboard import keyboard3
import signal


def goodbye(signum, frame):
    bot.write_msg(user_id, 'До свидания')


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        message_text = event.text.lower()
        user_id = str(event.user_id)

        signal.signal(signal.SIGALRM, handler=goodbye)
        signal.alarm(60)

        if message_text == 'нажмите, чтобы узнать на что я способен \N{smiling face with sunglasses}':
            bot.write_msg(user_id,
                          f'Приветствую, {bot.name(user_id)}! Я - бот VKinder. Могу помочь тебе найти пару! Я отправлю Вам 3 самые популярные фото юзера, чтобы составить своё первое впечатление. Если не понравится жми "Еще варианты"!\n'
                          f'\n Чтобы удалить историю просмотра нажмите "Удалить историю"', keyboard3.get_keyboard())

        elif message_text == 'удалить историю':
            reset_profile_loading_counter(user_id)
            drop_seen_users(user_id)
            bot.write_msg(user_id, f'Окей, {bot.name(user_id)} ваша история удалена!')

        elif message_text == 'начать автоматический поиск':
            create_table_seen_users(engine)
            bot.write_msg(user_id, f'Отлично, {bot.name(user_id)} тогда приступим')
            bot.send_info_about_users(user_id)

        elif message_text == 'начать поиск по индивидуальным предпочтениям':
            create_table_seen_users(engine)
            bot.write_msg(user_id, f'Отлично, {bot.name(user_id)} тогда приступим')
            bot.send_info_about_users_individual_parameters(user_id)

        else:
            bot.write_msg(event.user_id, 'Я вас не понимаю, повторите')
