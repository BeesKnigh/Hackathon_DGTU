import redis
import json

class RequestQueue:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def add_request_to_queue(self, request_id, user_query):
        request_data = {"request_id": request_id, "user_query": user_query}
        self.r.rpush("request_queue", json.dumps(request_data))

    def get_request_from_queue(self):
        request_data = self.r.lpop("request_queue")
        if request_data:
            return json.loads(request_data)
        return None

    def save_response(self, request_id, response):
        self.r.set(f"response:{request_id}", response)

    def get_response(self, request_id):
        return self.r.get(f"response:{request_id}")

    def get_queue_length(self):
        return self.r.llen("request_queue")
