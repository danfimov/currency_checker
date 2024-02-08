# Currency checker

Project have two parts:

- API for getting cryptocurrency rate in RUB and USD 
- Async worker for getting info about cryptocurrency rates from various platform APIs.

## Tech details and problems

### Currency rates on different platforms

I don’t know the cryptocurrency domain very well, so I didn’t fully understand what USDTTRC and USDTERC are.
A quick search on the Internet told me that this is Tether (USDT), which is processed by various Ethereum (USDTERC) and Tron (USDTTRC) infrastructures.

The Coingeko API and Binance API don't seem to have the option to show a different rate for them.
Therefore, I used regular USDT as USDTERC, and regular TRX instead of USDTTRC (to preserve the number of possible options).

Plus, the Binance API cannot display information on the USDT-USD exchange rate. Since this cryptocurrency pegged to the USD, I hardcoded the currency rate as 1.

### Coingeko free account

Coingeko have RPS limit for free accounts: 10_000 requests/month and 10-30 requests/minute. 
Because of that we need plenty of accounts for minimize time for updating exchange rates. 

Safe path for testing - use one account with env variable `COINGEKO_SCHEDULER__INTERVAL=60` for example.
On production this interval should be less of course.

### Metrics

Service can provide metrics about:
- API usage;
- Requests from workers to cryptocurrency platform APIs;
- Dramatiq queues;

If you need them, you can run metrics servers by passing env vars to containers:
```dotenv
# Example
API_METRICS_PORT=8001
SCHEDULER_METRICS_PORT=8002
BROKER_METRICS_PORT=8003
```

## Before run

1. Copy `conf/.env.example` to `conf/.env`:
    ```bash
    cp conf/.env.example conf/.env
    ```

2. Run migrations
    ```bash
    make migrate
    ```

    Alternatively you can set `RUN_MIGRATIONS_ON_STARTUP=1` and run application.

3. Add token from alive Coingeko accounts to `accounts` table, for example:
   ```sql
   INSERT INTO public.accounts (token, source) VALUES ('CG-JRbBUYiLpTvoSrwgiMWL397S', 'coingeko');
   ```

## Run on docker

```bash
docker compose up -d --remove-orphans --force-recreate --build
```

## Local run

Scheduler:
```bash
poetry run python3 -m currency_checker.scheduler
```

Broker with workers:
```bash
poetry run python3 -m currency_checker.scheduler.broker
```

API:
```yaml
poetry run python3 -m currency_checker.api
```
