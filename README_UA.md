# Скорочувач посилань
> [!NOTE]
> An [English](README.md) version of this document is available.

Це сайт, який дозволяє користувачам створювати короткі посилання.

## Локалізація
Сайт перекладено двома мовами: українською та англійською. Для локалізації використано модуль [Flask-Babel](https://pypi.org/project/flask-babel/).

> [!NOTE]
> Сайт автоматично визначає мову користувача на основі налаштувань мови його браузера.


## Можливості
### Створення та змінення коротких посилань
Сайт дозволяє створювати короткі посилання. Якщо при створенні посилання ввести пароль, тоді за адресою **127.0.0.1:5000/<коротке_посилання>/modify** ви зможете змінити 'довге' посилання на яке посилається коротке.

> [!NOTE]
> Якщо не вказати `http://` або `https://` для "довгого" посилання, тоді автоматично буде додано  `https://`.


> [!IMPORTANT]
> Пароль має бути надійним.

### Зміна пароля
На сторінці **127.0.0.1:5000/<коротке_посилання>/modify** окрім зміни посилання можна також змінити пароль.

> [!IMPORTANT]
> Пароль має бути надійним.

### Перегляд інформації
Перейшовши на сторінку **127.0.0.1:5000/<коротке_посилання>/info** ви отримаєте інформацію про те, коли було створено коротке посилання і куди воно веде.


## Встановлення залежностей
Для запуску потрібно встановити [Flask](https://pypi.org/project/Flask/), [Flask-Babel](https://pypi.org/project/flask-babel/) та [bcrypt](https://pypi.org/project/bcrypt/).

> [!IMPORTANT]
> У вас має бути [Python 3.9](https://www.python.org/) або пізніша версія

Їх можна встановити наступною командою:
#### Windows
```
pip install -r requirements.txt
```

#### macOS та Linux
```
pip3 install -r requirements.txt
```


## Запуск

Для запуску використайте наступну команду:

#### Windows
```
python app.py
```

#### macOS та Linux
```
python3 app.py
```

Це запустить локальний сервер з IP-адресою **127.0.0.1** та портом **5000**. Адресу та порт можна змінити у файлі [config.py](./config.py).

## Безпека
Паролі у базі даних зберігаються у [гешованому(хешованому) вигляді](https://uk.wikipedia.org/wiki/%D0%9A%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D1%96%D1%87%D0%BD%D0%B0_%D0%B3%D0%B5%D1%88-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D1%96%D1%8F), завдяки чому їх неможливо перетворити назад в оригінальний пароль.

Гешування відбувається завдяки модулю [bcrypt](https://pypi.org/project/bcrypt/).

> [!IMPORTANT]
> Використовуйте надійні та унікальні паролі. Гешування не врятує, якщо ваш пароль ненадійний.

> [!IMPORTANT]
> Коротке посилання генерується випадковим чином.