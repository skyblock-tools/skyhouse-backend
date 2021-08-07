

class JsonWrapper(dict):
    def __init__(self, *args, parent=None, key="", **kwargs):
        self.parent = parent
        self.key = key
        super(JsonWrapper, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        try:
            result = self[item]
            if isinstance(result, dict) and not isinstance(result, JsonWrapper):
                result = JsonWrapper(result, parent=self, key=item)
            return result
        except KeyError as e:
            raise AttributeError() from e

    def __setattr__(self, key, value):
        try:
            self[key] = value
            if self.parent is not None and self.key != "":
                self.parent.__setattr__(self.key, self)
        except KeyError as e:
            raise AttributeError() from e

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError as e:
            raise AttributeError() from e

    def to_dict(self):

        temp = JsonWrapper(self)

        for key in temp:
            if isinstance(temp[key], JsonWrapper):
                temp[key] = temp[key].to_dict()

        return dict(temp)

    @classmethod
    def from_dict(cls, data: dict):
        return JsonWrapper(data)

