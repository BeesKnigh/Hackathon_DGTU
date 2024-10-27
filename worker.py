import time
from model import AssistantModel
from request_queue import RequestQueue

assistant_model = AssistantModel()
queue = RequestQueue()

def process_requests():
    while True:
        # Извлекаем запрос из очереди
        request = queue.get_request_from_queue()
        if request:
            request_id = request['request_id']
            user_query = request['user_query']
            response = assistant_model.generate_response(user_query)
            
            queue.save_response(request_id, response)
            print(f"Ответ на запрос {request_id}: {response}")
        
        time.sleep(1)

if __name__ == "__main__":
    process_requests()
