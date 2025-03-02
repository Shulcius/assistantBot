# Бот помощник учителя

Этот бот предназначен для помощи преподавателям и их ученикам в изучении языка Python. Функционал включает:

1. **Регистрация пользователей**: Сохранение прогресса и настроек.
2. **Получение домашних заданий и учебных материалов**: Доступ к заданиям по разным темам.
3. **Проверка решений задач**: Автоматическая проверка кода на корректность выполнения задания.

Проект нацелен на упрощение процесса обучения и предоставление удобного инструмента для практики программирования.

# Установка и настройка
## Убедитесь, что у вас установлены все необходимые зависимости:

```
pip install -r requirements.txt
```
### Создайте файл .env и добавьте туда токен вашего бота:
```
BOT_TOKEN=<ваш_токен>
```
### Настройте подключение к базе данных PostgreSQL:
```
DB_CONFIG = {
    'host': '<хост>',
    'database': '<база_данных>',
    'user': '<пользователь>',
    'password': '<пароль>'
}
```
### Запустите бота:
```
python main.py
```
### Команды бота

/start — приветственное сообщение и информация о командах.
/help — список доступных команд.
/reg — начните процесс регистрации.
Структура проекта
main.py — основной файл запуска бота.
form.py — класс Form для работы с FSM.
config.py — конфигурационный файл с токеном бота.
requirements.txt — файл зависимостей.

### Лицензия
Данный проект распространяется под лицензией MIT. Вы можете свободно использовать, изменять и распространять его, соблюдая условия лицензии.