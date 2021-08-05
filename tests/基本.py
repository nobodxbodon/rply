import contextlib
import warnings


class BaseTests(object):
    @contextlib.contextmanager
    def assert_warns(self, cls, message):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield
        assert len(w) == 1, "报警数错误，应为 1，现为 " + str(len(w))
        assert w[0].category is cls, "报警类型错误"
        实际信息 = w[0].message.args[0].split('\n')[0]
        assert 实际信息 == message, "报警信息错误，现为'" + 实际信息 + "'"

    @contextlib.contextmanager
    def 应无报错(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield
        assert len(w) == 0, "报警数错误，应为 0，现为 " + str(len(w))
