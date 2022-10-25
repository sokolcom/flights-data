from locust import HttpUser, FastHttpUser, task, between, constant_throughput
import random


class TypicalUser(FastHttpUser):
    weight = 100
    wait_time = between(0.1, 2)

    @task(2)
    def get_aircrafts(self):
        tail_nos = ["N651DL", "N587UA", "N378HA", "N804JB", "N563AS"]
        ac_id = random.choice(tail_nos)
        self.client.get(f"/api/aircrafts?tail-no={ac_id}")

    @task(1)
    def get_airlines(self):
        self.client.get(f"/api/airlines")

    @task(2)
    def get_airports(self):
        airport_ids = ['JFK', 'LAX', 'SFO', 'LGA', 'SEA']
        ap_id = random.choice(airport_ids)
        self.client.get(f"/api/airports?iata={ap_id}")
    
    @task(4)
    def get_flights(self):
        requests = [
            "/api/flights?flighid=HA51", "/api/flights?date=2015-12-24",
            "/api/flights?tail-no=N804JB", "/api/flights?id=1234567",
            "/api/flights?tail-no=N587UA&from=JFK&to=SFO&dow=6"
        ]
        req = random.choice(requests)
        self.client.get(req)
    
    @task(2)
    def get_ac_operator(self):
        tail_nos = ["N651DL", "N587UA", "N378HA", "N804JB", "N563AS"]
        ac_id = random.choice(tail_nos)
        self.client.get(f"/api/ac-operator?tail-no={ac_id}")


    @task(2)
    def get_avgtime(self):
        airline_ids = ['DL', 'AA', 'B6', 'UA']
        al_id = random.choice(airline_ids)
        self.client.get(f"/api/avg-time?id={al_id}")

    @task(10)
    def popular_request(self):
        self.client.get("/api/ac-operator?tail-no=N479HA")
    

class AdminUser(FastHttpUser):
    weight = 1
    wait_time = between(5, 10)

    @task
    def update_aircrafts(self):
        json_data = {
            "token": "@topsecrettoken@",
            "tail_no": "N132SY",
            "mfr": "Airbus",
            "model": "Airbus test",
            "bday": "5999-12-31",
            "photo": "https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fwp-content%2Fblogs.dir%2F6%2Ffiles%2F2016%2F09%2Fyoung-thug-sister-mixtape-00.jpg?w=960&cbr=1&q=90&fit=max"
        }
        self.client.put("/api/aircrafts", json=json_data)

    @task
    def insert_flight(self):
        json_data = {
            "token": "@topsecrettoken@",
            "flight_date": "2016-01-01",
            "day_of_week": 5,
            "tail_no": "N132SY",
            "airline_id": "HA",
            "flight_id": 51,
            "origin": "JFK",
            "dest": "HAN",
            "dist": 4983.00,
            "delayed": 1, 
            "diverted": 0,
            "cancelled": 0
        }
        self.client.post("/api/flights", json=json_data)
    
    @task
    def delete_flight(self):
        json_data = {
            "token": "@topsecrettoken@",
            "id": 1
        }
        self.client.delete("/api/flights", json=json_data)
