class NetcodeBuffer:
    ALPHA = 0.25
    MAX_COMPENSATION_MS = 250

    def __init__(self, max_samples=8, max_ticks=64):
        self.max_samples = max_samples
        self.max_ticks = max_ticks
        self.samples = []
        self.inputs = {}

    def record(self, seq, rtt, now):
        if isinstance(seq, bool) or not isinstance(seq, int):
            raise ValueError("seq must be an integer")
        if self.samples and seq <= self.samples[-1]["seq"]:
            raise ValueError("seq must be strictly increasing")
        if isinstance(rtt, bool) or not isinstance(rtt, (int, float)) or rtt <= 0:
            raise ValueError("rtt must be a positive number")
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise ValueError("now must be a number")
        if self.samples and now < self.samples[-1]["now"]:
            raise ValueError("sample time must not go backwards")

        self.samples.append({"seq": seq, "rtt": rtt, "now": now})
        if len(self.samples) > self.max_samples:
            del self.samples[: len(self.samples) - self.max_samples]
        return None

    def smoothed_rtt(self):
        if not self.samples:
            return 0.0
        smoothed = float(self.samples[0]["rtt"])
        for sample in self.samples[1:]:
            smoothed = self.ALPHA * sample["rtt"] + (1 - self.ALPHA) * smoothed
        return smoothed

    def jitter(self):
        if len(self.samples) < 2:
            return 0.0
        differences = [
            abs(self.samples[index]["rtt"] - self.samples[index - 1]["rtt"])
            for index in range(1, len(self.samples))
        ]
        return sum(differences) / len(differences)

    def compensation_ms(self):
        if not self.samples:
            return 0.0
        return min(
            self.smoothed_rtt() + 2 * self.jitter(),
            self.MAX_COMPENSATION_MS,
        )

    def push_input(self, tick, action):
        if isinstance(tick, bool) or not isinstance(tick, int) or tick <= 0:
            raise ValueError("tick must be a positive integer")
        if not action or not isinstance(action, str):
            raise ValueError("action must be a non-empty string")
        if tick in self.inputs:
            raise ValueError("input for tick %d already exists" % tick)

        if len(self.inputs) >= self.max_ticks:
            del self.inputs[min(self.inputs)]
        self.inputs[tick] = action
        return None

    def replay(self, from_tick, to_tick):
        if from_tick > to_tick:
            raise ValueError("from_tick must not exceed to_tick")
        return [
            (tick, self.inputs[tick])
            for tick in sorted(self.inputs)
            if from_tick <= tick <= to_tick
        ]

    def state(self):
        return {
            "samples": [dict(sample) for sample in self.samples],
            "inputs": dict(self.inputs),
        }
