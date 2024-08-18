# Telegram Official Creative Society Bot

## Hosting

### Oracle Cloude

1. Видео по которому создавал виртуалку.
   https://youtu.be/18o6UcF0nnQ

---

2. После создания подключился к виртуалке по ssh.

---

3. На виртуалке сгенерил ssh ключ и добавил себе в настройки моего GitHub профиля что бы можно было туда склонить проект бота..

---

4. Установил питон нужной версии. Python 3.9.15

---

5. `pip install -r requirements.txt`

---

6. `cp config.py.example config.py` настроить конфиги.

---

7. Заупустил бота в фоновом режиме следующей командой `nohup python climate_news_bot.py &`

---

### Как убить фоноый процесс бота.

You can find the process and its process ID with this command:

```
ps ax | grep climate_news_bot.py

# or
# list of running processes Python

ps -fA | grep python
```

ps stands for process status

If you want to stop the execution, you can kill it with the kill command:

```
kill PID
```
