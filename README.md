## Local development

1. Создайте локальную директорию
```bash
mkdir ~/education/clinic
cd ~/education/clinic
```
2. Clone project
```bash
git clone git@github.com:akushnirenko/clinic.git
cd clinic
```

Далее читаем web/README.md для локальной разработки VueJS

3. Запустите докер.  Убедитесь по логам, что база данных заполняется данными, а затем git@github.com:akushnirenko/clinic.gitстарует app.
```bash
docker compose -f ./docker-compose-dev.yml up --build
```
4. Проверьте что работает все приложение вцелом по адресу
```
http://localhost:8080
```
5. Проверьте, что работает база данных:
```
psql -h localhost -p 55432 -U codes -d marking
```
6. Теперь приступаем как разработке.  Как правильные разработчики создаем свой branch и работаем в нем.
```bash
git switch -c feature/my-super-idea
code .
```

## Production installation
1. Clone project
```bash
git clone git@github.com:akushnirenko/clinic.git
cd chz-marking
```
2. Создайте .env file для подключения к markdb в ВЕДА
```
DATABASE_HOSTNAME = markdb
DATABASE_PORT = 5432
DATABASE_PASSWORD = *********
DATABASE_NAME = marking
DATABASE_USERNAME = postgres
SECRET_KEY = ****5e094faa2556c800000000000000000000000000
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```
3. Запустите production docker , который сконфигурирован под traefik
```bash
docker compose -f docker-compose-prod.yml up --build -d
```
4. Подключитесь к Web интерфейсу (имена уже настроены в ВЕДА):
```
http://marking.vedaved.ru
```

## Полезные команды
1. Если что-то вы все запортили, например в базе или просто хочется все почистить, то удалите все докеры и volumes (там содержимое базы):
```bash
docker compose -f ./docker-compose-dev.yml down -v
```
2. База данных доступна на локальном компьютере на порту 55432. Пароль тот, что вы указали в файле **.env** или в docker-compose файле. Можно подключиться с psql или с помощью навороченного pgadmin4
```bash
psql -U codes -h localhost -p 55432 -d marking
marking=# \dt
marking=# select * from codes;
```

