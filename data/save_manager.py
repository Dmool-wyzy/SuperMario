import json
import os
import time

MAX_SLOTS = 6
SAVE_DIR_NAME = "saves"
SAVE_VERSION = 2


class SaveManager:
    def __init__(self, save_dir=None, max_slots=MAX_SLOTS):
        self.max_slots = int(max_slots)
        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(__file__), "..", SAVE_DIR_NAME)
        self.save_dir = os.path.abspath(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)

    def reset_run(self, existing, slot):
        slot_int = self.validate_slot(slot)
        if slot_int is None:
            slot_int = 0

        base = self.create_new(slot_int)
        if base is None:
            return None

        normalized = self.normalize(existing, slot_int) if isinstance(existing, dict) else None
        if not isinstance(normalized, dict):
            return base

        if isinstance(normalized.get("records"), dict):
            base["records"] = normalized.get("records")

        prev_player = normalized.get("player", {})
        if isinstance(prev_player, dict):
            try:
                prev_top = int(prev_player.get("top_score", 0))
            except (TypeError, ValueError):
                prev_top = 0
            try:
                prev_score = int(prev_player.get("score", 0))
            except (TypeError, ValueError):
                prev_score = 0

            base_player = base.get("player", {})
            if isinstance(base_player, dict):
                base_player["top_score"] = max(prev_top, prev_score, int(base_player.get("top_score", 0) or 0))

        return base

    def validate_slot(self, slot):
        try:
            slot_int = int(slot)
        except (TypeError, ValueError):
            return None
        if 0 <= slot_int < self.max_slots:
            return slot_int
        return None

    def get_save_path(self, slot):
        slot_int = self.validate_slot(slot)
        if slot_int is None:
            return None
        return os.path.join(self.save_dir, f"slot_{slot_int}.json")

    def slot_exists(self, slot):
        path = self.get_save_path(slot)
        return bool(path) and os.path.exists(path)

    def create_new(self, slot):
        slot_int = self.validate_slot(slot)
        if slot_int is None:
            return None
        now_ms = int(time.time() * 1000)
        return {
            "version": SAVE_VERSION,
            "slot": slot_int,
            "updated_at_ms": now_ms,
            "player": {
                "lives": 3,
                "score": 0,
                "coin_total": 0,
                "top_score": 0,
                "big": False,
                "fire": False,
            },
            "progress": {
                "level": 1,
                "checkpoint": None,
                "mario_x": None,
                "mario_y": None,
                "viewport_x": 0,
            },
            "records": {},
            "flags": {
                "cheat_invincible": False,
            },
        }

    def normalize(self, raw, slot=None):
        if not isinstance(raw, dict):
            return None

        def coerce_bool(value, default=False):
            if isinstance(value, bool):
                return value
            if value is None:
                return bool(default)
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                v = value.strip().lower()
                if v in ("1", "true", "t", "yes", "y", "on"):
                    return True
                if v in ("0", "false", "f", "no", "n", "off", ""):
                    return False
                return bool(default)
            return bool(value)

        if raw.get("version") == SAVE_VERSION and isinstance(raw.get("player"), dict):
            slot_int = self.validate_slot(raw.get("slot", slot))
            if slot_int is None:
                slot_int = self.validate_slot(slot)
            if slot_int is not None:
                raw["slot"] = slot_int
            raw.setdefault("updated_at_ms", int(time.time() * 1000))
            raw.setdefault("progress", {})
            raw.setdefault("records", {})
            raw.setdefault("flags", {})
            player = raw.setdefault("player", {})
            player.setdefault("lives", 3)
            player.setdefault("score", 0)
            player.setdefault("coin_total", 0)
            player.setdefault("top_score", 0)
            player.setdefault("big", False)
            player.setdefault("fire", False)
            player["big"] = coerce_bool(player.get("big", False), default=False)
            player["fire"] = coerce_bool(player.get("fire", False), default=False)
            if not isinstance(raw.get("records"), dict):
                raw["records"] = {}
            raw["flags"].setdefault("cheat_invincible", False)
            raw["flags"]["cheat_invincible"] = coerce_bool(raw["flags"].get("cheat_invincible", False), default=False)
            raw["progress"].setdefault("level", 1)
            raw["progress"].setdefault("checkpoint", None)
            raw["progress"].setdefault("mario_x", None)
            raw["progress"].setdefault("mario_y", None)
            raw["progress"].setdefault("viewport_x", 0)
            return raw

        slot_int = self.validate_slot(raw.get("slot", slot))
        if slot_int is None:
            slot_int = self.validate_slot(slot)
        base = self.create_new(slot_int if slot_int is not None else 0) or self.create_new(0)

        base_player = base["player"]
        base_player["lives"] = int(raw.get("lives", base_player["lives"]) or base_player["lives"])
        base_player["score"] = int(raw.get("score", base_player["score"]) or base_player["score"])
        base_player["coin_total"] = int(raw.get("coin_total", base_player["coin_total"]) or base_player["coin_total"])
        base_player["top_score"] = int(raw.get("top_score", base_player["top_score"]) or base_player["top_score"])
        base_player["big"] = coerce_bool(raw.get("big", base_player["big"]), default=base_player["big"])
        base_player["fire"] = coerce_bool(raw.get("fire", base_player["fire"]), default=base_player["fire"])

        progress = base["progress"]
        progress["level"] = int(raw.get("level", progress["level"]) or progress["level"])
        progress["checkpoint"] = raw.get("checkpoint", raw.get("checkpoint_name", progress["checkpoint"]))
        progress["mario_x"] = raw.get("x_position", raw.get("mario_x", progress["mario_x"]))
        progress["mario_y"] = raw.get("y_position", raw.get("mario_y", progress["mario_y"]))
        progress["viewport_x"] = raw.get("viewport_x", progress["viewport_x"])

        flags = base["flags"]
        flags["cheat_invincible"] = coerce_bool(raw.get("cheat_invincible", flags["cheat_invincible"]), default=flags["cheat_invincible"])

        if isinstance(raw.get("records"), dict):
            base["records"] = raw.get("records")

        return base

    def load_with_error(self, slot):
        slot_int = self.validate_slot(slot)
        if slot_int is None:
            return None, "存档槽编号无效"

        path = self.get_save_path(slot_int)
        if not path or not os.path.exists(path):
            return None, None

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError):
            bad_path = f"{path}.bad"
            try:
                os.replace(path, bad_path)
            except OSError:
                pass
            return None, "存档文件损坏，已自动隔离"

        normalized = self.normalize(raw, slot_int)
        if normalized is None:
            return None, "存档格式不支持"
        return normalized, None

    def load(self, slot):
        data, _err = self.load_with_error(slot)
        return data

    def save_with_error(self, slot, data):
        slot_int = self.validate_slot(slot)
        if slot_int is None:
            return "存档槽编号无效"

        normalized = self.normalize(data, slot_int) if isinstance(data, dict) else None
        if normalized is None:
            normalized = self.create_new(slot_int)

        normalized["slot"] = slot_int
        normalized["version"] = SAVE_VERSION
        normalized["updated_at_ms"] = int(time.time() * 1000)

        path = self.get_save_path(slot_int)
        if not path:
            return "存档路径无效"

        tmp_path = f"{path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(normalized, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except OSError:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return "写入存档失败"
        return None

    def save(self, slot, data):
        self.save_with_error(slot, data)

    def delete(self, slot):
        path = self.get_save_path(slot)
        if not path or not os.path.exists(path):
            return False
        try:
            os.remove(path)
        except OSError:
            return False
        return True

    def summarize(self, slot):
        data, err = self.load_with_error(slot)
        if data is None:
            return {
                "exists": False,
                "error": err,
                "slot": self.validate_slot(slot),
            }
        player = data.get("player", {})
        progress = data.get("progress", {})
        return {
            "exists": True,
            "error": err,
            "slot": data.get("slot", self.validate_slot(slot)),
            "lives": player.get("lives", 3),
            "score": player.get("score", 0),
            "coin_total": player.get("coin_total", 0),
            "level": progress.get("level", 1),
            "checkpoint": progress.get("checkpoint", None),
        }
