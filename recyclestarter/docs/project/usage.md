# Запуск
Установить docker и docker-compose.

Локальный запуск:

```
./local.sh
```
# Тестирование
```
docker exec django bash -c "python manage.py test --settings config.settings.test --parallel --keepdb"
```

## coverage:
```
docker exec django bash -c "coverage run manage.py test --settings config.settings.test --keepdb && coverage html"
```
смотрим htmlcov/index.html
