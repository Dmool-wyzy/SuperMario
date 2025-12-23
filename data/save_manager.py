import json
import os

MAX_SLOTS = 6
SAVE_DIR = "saves"


class SaveManager:
    def __init__(self):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    def get_save_path(self, slot):
        return os.path.join(SAVE_DIR, f"slot_{slot}.json")

    def slot_exists(self, slot):
        return os.path.exists(self.get_save_path(slot))

    def load(self, slot):
        path = self.get_save_path(slot)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, slot, data):
        path = self.get_save_path(slot)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Game saved in slot {slot}")
