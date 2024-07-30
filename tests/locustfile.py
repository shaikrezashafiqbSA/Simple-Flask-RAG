from locust import HttpUser, task, between, constant_pacing

class TravelAPIUser(HttpUser):
    wait_time = constant_pacing(60)  # Adjust wait time as needed

    def on_start(self):
        # Replace with your actual Bearer token
        self.auth_header = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.MyVR6Tz4dHLLmqWPHWLnyUp9qnX1HyGDr-WRoWe6LXU'}  

    @task
    def get_itinerary(self):
        headers = self.auth_header
        print(headers)
        payload = {
            "prompt": "i want to go kedah for 2 days for a honeymoon couple, from jungle theme to sea"
        }

        self.client.post("/api/2", json=payload, headers=headers)
