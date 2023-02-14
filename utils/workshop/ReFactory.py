"""一个工厂模式"""
from abc import ABCMeta, abstractmethod
import re


class PatternFactory(object, metaclass=ABCMeta):
    @abstractmethod
    def compile(self): pass


class EmailPattern(PatternFactory):

    @property
    def compile(self):
        return re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')


class PhonePattern(PatternFactory):
    @property
    def compile(self):
        return re.compile(r"^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$")


class Pattern(object):
    def __init__(self): pass

    def __getitem__(self, item):
        if not hasattr(self, '_re_' + item):
            raise ValueError(
                "在{0}类里,不存在{1}方法".format(self.__class__.__name__, item)
            )
        return getattr(self, '_re_' + item)()

    def __setitem__(self, key, value):
        setattr(self, '_re_' + key, value)

    def _re_email(self):
        return EmailPattern().compile

    def _re_phone(self):
        return PhonePattern().compile


if __name__ == '__main__':
    obj = Pattern()
    print(obj["email"])
