# URL Shortener
> [!NOTE]
> Цей документ має переклад [українською](README_UA.md).

This website is designed for creating short URLs.


## Localization
The website supports two languages: English and Ukrainian. [Flask-Babel](https://pypi.org/project/flask-babel/) is used for localization.

> [!NOTE]
> The website selects the language based on your browser's selected language.

## Features
### Adding and editing short URLs
The website allows users to create and edit short URLs. You can edit the destination (or "long") URL of a short URL on the page **127.0.0.1:5000/<short_url>/modify**, but only if a password was provided during the creation process.

> [!NOTE]
> If 'long' URL does not include `http://` or `https://`, `https://` will be added automatically.

> [!IMPORTANT]
> Password must be strong.

### Change password
In the **127.0.0.1:5000/<short_url>/modify** page you can not only edit the short URL but also change  password.

> [!IMPORTANT]
> Password must be strong.

### Viewing information
By visiting the **127.0.0.1:5000/<short_url>/info** page you can view details such as when the short URL was created and where it redirects.


## Installing dependencies
The website uses [Flask](https://pypi.org/project/Flask/), [Flask-Babel](https://pypi.org/project/flask-babel/) and [bcrypt](https://pypi.org/project/bcrypt/).

> [!IMPORTANT]
> [Python 3.9](https://www.python.org/) or later must be installed.

Dependencies can be installed with the following command:
#### Windows
```
pip install -r requirements.txt
```

#### macOS та Linux
```
pip3 install -r requirements.txt
```


## Running

Use following command
#### Windows
```
python app.py
```

#### macOS та Linux
```
python3 app.py
```

This will host web server at the IP address **127.0.0.1** and port **5000**. Address and port can be changed in[config.py](./config.py) file.

## Security
Password are [hashed](https://en.wikipedia.org/wiki/Cryptographic_hash_function), so they cannot be reverted to original state.

Module [bcrypt](https://pypi.org/project/bcrypt/) is used for hashing.

> [!IMPORTANT]
> Always use strong passwords. Hashing cannot protect against weak passwords.