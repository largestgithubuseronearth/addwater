class AddWaterException(Exception):
    # TODO log info

    # TODO User-friendly error message

    def __init__(self, user_msg=None, log_info=None):
        self.msg = user_msg
        self.log_info = log_info


class NetworkException(AddWaterException):
    pass

class FatalPageException(AddWaterException):
    pass

class InstallException(AddWaterException):
    pass
