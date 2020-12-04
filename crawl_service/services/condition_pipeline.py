import hashlib


class ConditionPipeline(object):
    order = (
        'check_dupplicate',
    )

    def __init__(self):
        self.condition = None
        self.funcs = []

    def add(self, con, func, value):
        self.funcs.append(func)

    def run(self):
        pass

    @staticmethod
    def md5_hash(value: str):
        return hashlib.md5(value.encode()).digest()

