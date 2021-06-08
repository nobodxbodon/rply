import contextlib
import warnings


class BaseTests(object):
    @contextlib.contextmanager
    def assert_warns(self, cls, message):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield
        assert len(w) == 1, "未报警"
        assert w[0].category is cls, "报警类型错误"
        assert w[0].message.args[0].split('\n')[0] == message, "报警信息错误"
