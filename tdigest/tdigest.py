from random import choice, shuffle, random


class Centroid(object):

    def __init__(self, m, count):
        self.m = m
        self.count = count

    def __str__(self):
        return "%s %s" % (self.m, self.count)


class TDigest(object):

    # compression parameter
    K = 100

    def __init__(self, delta):
        self.delta = delta
        self.n = 0
        # TODO: replace this list with a balanced tree
        self.data = []

    def _add(self, c):
        self.data.append(c)
        self.n += c.count

    def _update(self, s, c):
        i = self.data.index(s)
        self.data[i].m = c.m
        self.data[i].count = c.count

    def _get_z(self, c):
        return min([abs(y.m - c.m) for y in self.data])

    def _get_s(self, c):
        q = self._get_q(c)
        z = self._get_z(c)
        return [y for y in self.data if (abs(y.m - c.m) == z) and
                (c.count + 1 <= 4 * self.n * self.delta * q * (1 - q))]

    def _get_sum(self):
        return sum([c.count for c in self.data])

    def _get_q(self, c):
        return (c.count / 2 + sum([y.count for y in
               (filter(lambda y: y.m < c.m, self.data))])) / self._get_sum()

    def __len__(self):
        return len(self.data)

    def add(self, x, w):
        self.n += 1
        c = Centroid(x, w)
        if len(self.data) == 0:
            self._add(c)
        else:
            s_valid = self._get_s(c)
            while len(s_valid) != 0 and w > 0:
                s = choice(s_valid)
                q = self._get_q(c)
                deltaw = min(4 * self.n * self.delta * q * (1 - q) - s.m, w)
                new_count = s.count + deltaw
                new_m = s.m + deltaw * (x - s.m) / s.count
                self._update(s, Centroid(new_m, new_count))
                w -= deltaw
                s_valid.remove(s)
            if w > 0:
                self._add(c)
        if len(self.data) > self.K / self.delta:
            self._compress()

    def _compress(self):
        reduced = TDigest(self.delta)
        current_data = self.data
        shuffle(current_data)
        for c in current_data:
            reduced.add(c.m, c.count)
        self.data = reduced.data
        self.n = reduced.n

    def quantile(self, q):
        t = 0
        q *= self.n
        data = sorted(self.data, key=lambda x: x.m)
        for i, c in enumerate(data):
            ki = c.count
            if q < t + ki:
                if i == 1:
                    d = data[i + 1].m - data[i].m
                elif i == self.n - 1:
                    d = data[i].m - data[i - 1].m
                else:
                    d = (data[i + 1].m - data[i - 1].m) / 2.0
                return c.m + (1.0 * (q - t) / ki - 0.5) * d
            t += ki
        return data[-1].m


if __name__ == "__main__":

    t = TDigest(0.1)
    for z in range(10000):
        x = 2 * random()
        t.add(x, 1)
    print(len(t))
    print(t.quantile(0.8))
