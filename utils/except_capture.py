"""异常捕获装饰类"""
from utils.response import APIResponse


class ExceptCapture(object):
    """异常捕获类"""

    @staticmethod
    def except_capture(status=1000, data={}):

        def wrapper(func):
            def inner(*args, **kwargs):
                try:
                    obj = func(*args, **kwargs)
                    return obj
                except Exception as e:
                    return APIResponse(data={"cw": 11}, code=status)

            return inner

        return wrapper


if __name__ == '__main__':
    @ExceptCapture.except_capture(status=1000, data={1: 1})
    def asy():
        print(a)


    print(asy())
