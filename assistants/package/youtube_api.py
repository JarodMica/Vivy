import pytchat
import time
import queue
import random
import threading

class YoutubeAPI:
    def __init__(self, video_id, max_queue_length=2, collection_cycle_duration=20):
        self.max_queue_length = max_queue_length
        self.collection_cycle_duration = collection_cycle_duration
        self.msg_queue = queue.Queue(max_queue_length)
        self.chat = pytchat.create(video_id=video_id)
        self.msg_list = []
        self.last_add_time = time.time()

    def process_chat_messages(self):
        start_time = time.time()
        while True:
            for c in self.chat.get().sync_items():
                if "!vivy" in c.message:
                    message = c.message.replace("!vivy", "").strip()  # remove "!vivy" from the message
                    # Only append messages that are 130 characters or less and contain "!vivy"
                    if len(message) <= 130:
                        c.message = message
                        self.msg_list.append(c)
            if time.time() - start_time >= self.collection_cycle_duration:
                if not self.msg_queue.full() and self.msg_list:
                    chosen_msg = random.choice(self.msg_list)
                    self.msg_queue.put(chosen_msg)
                    self.last_add_time = time.time()  # update the last add time
                start_time = time.time()
                self.msg_list = []

            # Remove the first item in the queue if more than 40 seconds have passed since the last addition
            if time.time() - self.last_add_time > 80:
                self.clear_queue()

    def clear_queue(self):
        if not self.msg_queue.empty():
            self.msg_queue.get_nowait()

    def start(self):
        chat_thread = threading.Thread(target=self.process_chat_messages)
        chat_thread.start()
