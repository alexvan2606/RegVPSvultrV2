


class VultrAPIError(Exception):
    def __init__(self, error, *args, **kwargs):
        self.error = error
        
        print(self.error)
