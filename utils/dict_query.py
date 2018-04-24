class DictQuery(dict):
    """
    Something to traverse complex json structures easier... For Python 2.7 since Python 3 already has this feature...
    (I can hear Alessandro laughing in the background)
    """

    def get(self, p, default=None):
        keys = p.split(".")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val

    def search_key(self, key):
        if key in self.keys():
            return self[key]
        for item in self.items():
            if isinstance(item, tuple):
                item = DictQuery(item)
                item.search_key(key)
