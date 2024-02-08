from locust import HttpUser, between, task


class WebsiteTestUser(HttpUser):
    wait_time = between(0.2, 0.5)

    @task(1)
    def ping(self):
        self.client.get("http://localhost:8000/ping")

    @task(50)
    def binance(self):
        self.client.get(
            "http://localhost:8000/v1/courses/"
            "?exchanger=binance&directions=BTC-RUB"
            "&directions=BTC-USD&directions=ETH-RUB&directions=ETH-USD&directions=USDTTRC-RUB&directions=USDTTRC-USD"
            "&directions=USDTERC-RUB&directions=USDTERC-USD"
        )

    @task(50)
    def coingeko(self):
        self.client.get(
            "http://localhost:8000/v1/courses/"
            "?exchanger=coingeko&directions=BTC-RUB"
            "&directions=BTC-USD&directions=ETH-RUB&directions=ETH-USD&directions=USDTTRC-RUB&directions=USDTTRC-USD"
            "&directions=USDTERC-RUB&directions=USDTERC-USD"
        )

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass
