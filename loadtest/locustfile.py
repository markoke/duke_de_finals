from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    host = "http://20.121.88.29:80"
    wait_time = between(1, 10)

    @task
    def predict(self):
        self.client.get("/example_predict")