**whsh-billing**

В сервисе 3 метода:

`GET /top_10_invoices` - без параметров. Делает выборку первых 10 строк из t_invoices

`POST /create_invoice` - с body. Добавляет запись в таблицу `t_invoices`

`POST /send_invoices` - аргументы в url (`send_invoices/?id_invoice=1`). 
Можно передать `id_invoice`, id_account или все вместе.
По переданным аргументам найдется запись в таблице и
вызовется эндпоинт `/create_account` сервиса whsh-accounting,
который обновит баланс клиента в таблице `t_accounts`. Если клиента не было, то создаст нового.

**Запуск:**

Сервис запускается из склонированной директории через `docker-compose up`.
При запуске сервис создает свою БД postgresql с таблицей `t_invoices`.
После запуска можно проверить работоспособность http тестами из папки tests/http,
через http://localhost:8008/docs
или curl-ом:

`curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "id_account": 9999,
  "operation": 100
}' \
 http://localhost:8008/create_invoice`

Также можно использовать тесты из test_billing для проверки основного функционала.
В текущей версии в test_billnig используется БД sqlite, которая создается для тестов. 
