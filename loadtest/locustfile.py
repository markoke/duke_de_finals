from locust import HttpUser, task, constant

class WebsiteUser(HttpUser):
    host = "http://20.121.88.29:80"
    wait_time = constant(0)

    @task
    def predict(self):
        self.client.get("/example_predict")