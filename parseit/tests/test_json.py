import json
from parseit import Input
from parseit.compiler import comp
from parseit.json_parser import (TRUE,
                                 FALSE,
                                 NULL,
                                 JsonArray,
                                 JsonObject,
                                 JsonValue)

DATA0 = """
{
    "name": "Adventure Lookup"
}
""".strip()


DATA1 = """
{
    "name": "Adventure Lookup",
    "icons": [
        {
            "src": "/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "theme_color": "#ffffff",
    "background_color": "#ffffff",
    "display": "standalone"
}
""".strip()

DATA2 = """
{
  "meta": {
    "version": "0.6.0"
  },
  "GROUPS": {
    "c-development": {
      "grp_types": 0,
      "ui_name": "C Development Tools and Libraries",
      "name": "C Development Tools and Libraries",
      "full_list": [
        "valgrind",
        "automake",
        "indent",
        "autoconf",
        "ltrace",
        "bison",
        "ccache",
        "gdb",
        "strace",
        "elfutils",
        "byacc",
        "oprofile",
        "gcc-c++",
        "pkgconfig",
        "binutils",
        "gcc",
        "libtool",
        "cscope",
        "ctags",
        "flex",
        "glibc-devel",
        "make"
      ],
      "pkg_exclude": [],
      "pkg_types": 6
    }
  },
  "ENVIRONMENTS": {}
}""".strip()


def test_true():
    assert TRUE(Input("true")).value is True
    assert comp(TRUE)("true")[1] is True


def test_false():
    assert FALSE(Input("false")).value is False
    assert comp(FALSE)("false")[1] is False


def test_null():
    assert NULL(Input("null")).value is None
    assert comp(NULL)("null")[1] is None


def test_json_value_number():
    assert JsonValue(Input("123")).value == 123
    assert comp(JsonValue)("123")[1] == 123


def test_json_value_string():
    assert JsonValue(Input('"key"')).value == "key"
    assert comp(JsonValue)('"key"')[1] == "key"


def test_json_empty_array():
    assert JsonArray(Input("[]")).value == []
    assert comp(JsonArray)("[]")[1] == []


def test_json_single_element_array():
    assert JsonArray(Input("[1]")).value == [1]
    assert JsonArray(Input("['key']")).value == ["key"]
    assert comp(JsonArray)("['key']")[1] == ["key"]


def test_json_multi_element_array():
    assert JsonArray(Input("[1, 2, 3]")).value == [1, 2, 3]
    assert comp(JsonArray)("[1, 2, 3]")[1] == [1, 2, 3]

    assert JsonArray(Input("['key', -3.4, 'thing']")).value == ["key", -3.4, "thing"]
    assert comp(JsonArray)("['key', -3.4, 'thing']")[1] == ["key", -3.4, "thing"]


def test_json_nested_array():
    assert JsonArray(Input("[1, [4, 5], 3]")).value == [1, [4, 5], 3]
    assert comp(JsonArray)("[1, [4, 5], 3]")[1] == [1, [4, 5], 3]

    assert JsonArray(Input("['key', [-3.4], 'thing']")).value == ["key", [-3.4], "thing"]
    assert comp(JsonArray)("['key', [-3.4], 'thing']")[1] == ["key", [-3.4], "thing"]


def test_json_empty_object():
    assert JsonObject(Input("{}")).value == {}
    assert comp(JsonObject)("{}")[1] == {}


def test_json_single_object():
    assert JsonObject(Input('{"key": "value"}')).value == {"key": "value"}
    assert comp(JsonObject)('{"key": "value"}')[1] == {"key": "value"}


def test_json_multi_object():
    expected = {"key1": "value1", "key2": 15}
    assert JsonObject(Input('{"key1": "value1", "key2": 15}')).value == expected
    assert comp(JsonObject)('{"key1": "value1", "key2": 15}')[1] == expected


def test_json_nested_object():
    text = '{ "key1": ["value1", "value2"], "key2": {"num": 15, "num2": 17 }}'
    data = Input(text)
    expected = {"key1": ["value1", "value2"], "key2": {"num": 15, "num2": 17}}
    assert JsonObject(data).value == expected
    assert comp(JsonObject)(text)[1] == expected


def test_data0():
    data = Input(DATA0)
    expected = json.loads(DATA0)
    assert JsonValue(data).value == expected
    assert comp(JsonValue)(DATA0)[1] == expected


def test_data1():
    data = Input(DATA1)
    expected = json.loads(DATA1)
    assert JsonValue(data).value == expected
    assert comp(JsonValue)(DATA1)[1] == expected


def test_data2():
    data = Input(DATA2)
    expected = json.loads(DATA2)
    assert JsonValue(data).value == expected
    assert comp(JsonValue)(DATA2)[1] == expected
