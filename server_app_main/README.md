## 1
Чтобы запускать фласк приложение:
1) Нужно сначала удалить __init__.py файл из директории вместе с main.py, чтобы питонадекватно мог просматривать все 
названия модулей.
2) Установить переменную окружения FLASK_APP:
    set FLASK_APP=hello.py
    $env:FLASK_APP = "hello.py"
    flask run
3) Запустить сервер командой flask run

## 2
Чтобы сделать миграцию базы данных, нужно:
1) Сделать команду flask db init, если в первый раз делается миграция
2) flask db migrate -m "название миграции" - создает миграцию
3) flask db upgrade - применяет изменения в базе данных на основе текущей миграции
4) flask db downgrade - откатывает изменения до предыдущей версии

## 3
Инструкции по деплою приложения:
1) https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04
В инструкции номер 1 в конфиге сервера nginx нужно указать путь не myproject/myproject.sock, 
а просто myproject.sock - нужно смотреть где создан этот файл.
2) https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04
3) https://sys-adm.in/systadm/nix/945-vklyuchenie-logirovaniya-v-gunicorn.html
https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
В гуникорне нужно включить логгирование, чтобы можно было понять, что происходит
4) в конфиге выставить таймаут работы воркера не 30 секунд, а 10 минут 
https://stackoverflow.com/questions/10855197/gunicorn-worker-timeout-error


## 4
Чтобы обновить приложение - нужно обновить нужные папки - например только папку app, затем:
1) sudo systemctl daemon-reload - обновляем демона
2) sudo systemctl restart ez_print_server_app_main - перезапускаем гуникорн
3) systemctl status ez_print_server_app_main - чекаем статус

## 5
Чтобы чекнуть логи гуникорна, смотрим логи по адресу: /var/log/gunicorn






