class GridInventory:
    def __init__(self, width, height, max_stack=5):
        self.width = width
        self.height = height
        self.max_stack = max_stack
        self.items = {}

    @staticmethod
    def _is_positive_int(value):
        return isinstance(value, int) and not isinstance(value, bool) and value > 0

    @staticmethod
    def _is_coord(value):
        return isinstance(value, int) and not isinstance(value, bool)

    def _effective_size(self, w, h, rotated):
        if rotated:
            return h, w
        return w, h

    def _footprint_valid(self, w, h, x, y, rotated, ignore_id=None):
        if not (self._is_positive_int(w) and self._is_positive_int(h)):
            return False
        if not (self._is_coord(x) and self._is_coord(y)):
            return False
        if not isinstance(rotated, bool):
            return False
        eff_w, eff_h = self._effective_size(w, h, rotated)
        if x < 0 or y < 0:
            return False
        if x + eff_w > self.width or y + eff_h > self.height:
            return False
        for item_id, item in self.items.items():
            if item_id == ignore_id:
                continue
            overlap_x = x < item["x"] + item["w"] and item["x"] < x + eff_w
            overlap_y = y < item["y"] + item["h"] and item["y"] < y + eff_h
            if overlap_x and overlap_y:
                return False
        return True

    def place(self, item_id, w, h, x, y, rotated=False):
        if item_id in self.items:
            raise ValueError(f"item {item_id!r} already placed")
        if not self._footprint_valid(w, h, x, y, rotated):
            raise ValueError("placement does not fit inside the free grid")
        eff_w, eff_h = self._effective_size(w, h, rotated)
        self.items[item_id] = {
            "x": x,
            "y": y,
            "w": eff_w,
            "h": eff_h,
            "qty": 1,
            "rotated": rotated,
        }

    def stack(self, item_id, qty):
        if item_id not in self.items:
            raise ValueError(f"unknown item {item_id!r}")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("stack quantity must be a positive integer")
        item = self.items[item_id]
        if item["qty"] + qty > self.max_stack:
            raise ValueError("stack would exceed max stack size")
        item["qty"] += qty

    def remove(self, item_id, qty=1):
        if item_id not in self.items:
            raise ValueError(f"unknown item {item_id!r}")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("remove quantity must be a positive integer")
        item = self.items[item_id]
        if qty > item["qty"]:
            raise ValueError("cannot remove more than the held quantity")
        item["qty"] -= qty
        if item["qty"] == 0:
            del self.items[item_id]

    def move(self, item_id, x, y, rotated=False):
        if item_id not in self.items:
            raise ValueError(f"unknown item {item_id!r}")
        item = self.items[item_id]
        if rotated == item["rotated"]:
            eff_w, eff_h = item["w"], item["h"]
        else:
            eff_w, eff_h = item["h"], item["w"]
        if not self._footprint_valid(eff_w, eff_h, x, y, rotated=False,
                                     ignore_id=item_id):
            raise ValueError("target position does not fit inside the free grid")
        item["x"] = x
        item["y"] = y
        item["w"] = eff_w
        item["h"] = eff_h
        item["rotated"] = rotated

    def can_place(self, w, h, x, y, rotated=False):
        return self._footprint_valid(w, h, x, y, rotated)

    def state(self):
        return {"items": {item_id: dict(item)
                          for item_id, item in self.items.items()}}
