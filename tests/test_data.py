from chronicle.data import Data


class FooObj:
    def __init__(self, a, b):
        self.a = a
        self.b = b


test_data_dict = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4},
    {"a": 5, "b": 6},
]


test_data_dict_redux = [
    {"c": 1, "d": 2},
    {"c": 3, "d": 4},
    {"c": 5, "d": 6},
]


test_data_obj = [
    FooObj(7, 8),
    FooObj(9, 10),
    FooObj(11, 12),
]


def test_data():
    """It creates Datas."""
    # It creates a Data from a dict.
    test_data = Data("test", test_data_dict)
    assert test_data.title == "test"
    assert test_data._raw_data[0] == test_data_dict
    assert test_data.columns == ["a", "b"]
    assert len(test_data) == len(test_data_dict)
    assert next(test_data) == list(test_data_dict[0].values())
    for i, d in enumerate(test_data):
        assert d == list(test_data_dict[1:][i].values())

    # It creates Data from an object.
    test_data = Data("test", test_data_obj)
    assert test_data.title == "test"
    assert test_data._raw_data[0] == test_data_obj
    assert test_data.columns == ["a", "b"]
    assert len(test_data) == len(test_data_obj)
    assert next(test_data) == [test_data_obj[0].a, test_data_obj[0].b]
    for i, d in enumerate(test_data):
        assert d == [test_data_obj[1:][i].a, test_data_obj[1:][i].b]

    # It filters columns.
    test_data = Data("test", test_data_dict, columns=["b"])
    assert test_data.columns == ["b"]
    assert next(test_data) == [test_data_dict[0]["b"]]

    # It combines multiple things together.
    test_data = Data("test", test_data_dict, test_data_obj)
    for i in range(len(test_data_dict)):
        assert test_data[i] == list(test_data_dict[i].values())
    for i in range(len(test_data_obj)):
        assert test_data[i + len(test_data_dict)] == [
            test_data_obj[i].a,
            test_data_obj[i].b,
        ]


def test_data_join():
    """It joins Datas."""
    # It joins multiple dicts together with disparate fields.
    test_data = Data("test", test_data_dict)
    test_data.join(test_data_dict_redux)
    assert test_data.columns == ["a", "b", "c", "d"]
    assert next(test_data) == list(test_data_dict[0].values()) + list(
        test_data_dict_redux[0].values()
    )

    # It joins on an initial empty state.
    test_data = Data("test")
    test_data.join(test_data_obj)
    assert test_data.columns == ["a", "b"]

    # It also joins objects.
    test_data = Data("test", test_data_dict_redux)
    test_data.join(test_data_obj)
    assert test_data.columns == ["c", "d", "a", "b"]
    assert next(test_data) == list(test_data_dict_redux[0].values()) + [
        test_data_obj[0].a,
        test_data_obj[0].b,
    ]

    # It filters joined dicts.
    test_data = Data("test", test_data_dict, columns=["b"])
    test_data.join(test_data_dict_redux, columns=["d"])
    assert test_data.columns == ["b", "d"]
    assert next(test_data) == [test_data_dict[0]["b"], test_data_dict_redux[0]["d"]]


def test_data_f():
    """It filters two lists."""
    assert ["b", "c"] == Data.f(["a", "b", "c"], ["b", "c", "d'"])
