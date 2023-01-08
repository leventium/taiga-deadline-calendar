# Deadline calendar (Beta)

## Описание
Вебхук для автоматического подхватывания информации о дедлайнах в тайге и их переноса в календарь пользователя или проекта. Для каждого пользователя/проекта есть персональная ссылка, позволяющая подписаться на каледарь с дедлайнами в любом удобном сервисе имеющим функцию подписных календарей.

## Инструкция по развёртыванию
- Скопируйте docker-compose.yaml на сервер
- Задайте в разделе environment скопированного файла информацию о...
    1. Адресе тайги в `TAIGA_URL`
    2. Токене тайги в `TAIGA_TOKEN`
    3. Опционально. Адресе redis в `REDIS_CONNSTRING`, если уже есть запущенный инстанс не желаете создавать новый.
    4. Опционально. Временной зоне в `TIME_ZONE` (`Europe/Moscow` по умолчанию)
- Запустите сервис командой
```
sudo docker-compose up -d
```
- Радуйтесь жизни

## To Do
- [x] Make async
- [x] Include caches
