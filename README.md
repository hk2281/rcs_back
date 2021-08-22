# Django backend for RCS ITMO.
by Egor Kondrashov, 2021.

При деплое нужно прописать следующие команды:
sudo chown -R 777:777 ./logs
sudo chown -R 777:777 ./rcs_back/media

Т. к. это mounted папки, в которые хотят писать приложения внутри докера.
Но они работают не от root, а от пользователя 777:777.

git clone https://github.com/xalvaine/restarter.git
фронт

Gunicorn workers на сервере иногда умирали с signal 9, скорее всего
потому что не хватало памяти. Пофиксил, добавив swap-memory.