**whsh-billing**

Сервис наполняет таблицу t_billing инвойсами и может выполнять передачу инвойсов сервису whsh-accounting.

В сервисе 3 метода:

`GET /top_10_invoices` - Делает выборку первых 10 строк из t_invoices. Без параметров

`POST /create_invoice` - Добавляет запись в таблицу `t_invoices`. В body передается тело новой записи. 

`POST /send_invoices` - 
Можно передать `id_invoice`, `id_account` или все вместе.
По переданным аргументам найдется запись в таблице и
вызовется эндпоинт `/create_account` сервиса `whsh-accounting`,
чтобы тот обновил баланс клиента в своей таблице `t_accounts`. 
Если клиента не было, то `whsh-accounting создаст нового.
Аргументы мапятся в url (`send_invoices/?id_invoice=1`). 

**Запуск:**

Нужно склонировать репозиторий и в склонированной директории выполнить `docker-compose up`.
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
В текущей версии в test_billnig используется БД `sqlite`, которая создается для тестов.
