# Локальная разработка VUEJS интерфейса

Вам необходимо установить nodejs и необходимые модули

## Собираем backend и базу данных в виде docker.
```sh
cd web
npm install
```

### Запускаем development сервер

Необходимые переменные backend устанавливаются в файле .env.development. Заходим в основную папку проекта и собираем докеры, а затем подключаемся к ним.

```sh
cd ..
docker compose -f docker-compose-dev.yml up app db --build
cd web
npm run dev
```

### Проверка интерфейса

Смотрим точки подключения backend
http://localhost:8000/docs

Интерфейс должен быть доступен http://localhost:5173/  Должен открыться списоок выполненных серий (batches)


