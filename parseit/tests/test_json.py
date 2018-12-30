from parseit import Input
from parseit.json_parser import (TRUE,
                                 FALSE,
                                 NULL,
                                 JsonArray,
                                 JsonObject,
                                 JsonValue)


def test_true():
    assert TRUE(Input("true")).value is True


def test_false():
    assert FALSE(Input("false")).value is False


def test_null():
    assert NULL(Input("null")).value is None


def test_json_value_number():
    assert JsonValue(Input("123")).value == 123


def test_json_value_string():
    assert JsonValue(Input('"key"')).value == "key"


def test_json_empty_array():
    assert JsonArray(Input("[]")).value == []


def test_json_single_element_array():
    assert JsonArray(Input("[1]")).value == [1]
    assert JsonArray(Input("['key']")).value == ["key"]


def test_json_multi_element_array():
    assert JsonArray(Input("[1,2,3]")).value == [1, 2, 3]
    assert JsonArray(Input("['key',-3.4,'thing']")).value == ["key", -3.4, "thing"]


def test_json_nested_array():
    assert JsonArray(Input("[1,[4,5],3]")).value == [1, [4, 5], 3]
    assert JsonArray(Input("['key',[-3.4],'thing']")).value == ["key", [-3.4], "thing"]


def test_json_empty_object():
    assert JsonObject(Input("{}")).value == {}


def test_json_single_object():
    assert JsonObject(Input('{"key":"value"}')).value == {"key": "value"}


def test_json_multi_object():
    expected = {"key1": "value1", "key2": 15}
    assert JsonObject(Input('{"key1":"value1","key2":15}')).value == expected


def test_json_nested_object():
    data = Input('{"key1":["value1","value2"],"key2":{"num":15}}')
    expected = {"key1": ["value1", "value2"], "key2": {"num": 15}}
    assert JsonObject(data).value == expected
