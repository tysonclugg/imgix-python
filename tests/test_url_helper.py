# -*- coding: utf-8 -*-

import imgix
import warnings

from imgix.compat import urlparse
from imgix.urlhelper import UrlHelper


def _default_helper():
    return UrlHelper('my-social-network.imgix.net', '/users/1.png')


def test_create():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png')
    assert type(helper) is UrlHelper


def test_create_sign_mode_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        UrlHelper('my-social-network.imgix.net', '/users/1.png',
                  sign_mode=imgix.SIGNATURE_MODE_QUERY)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)


def test_create_non_query_sign_mode():
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UrlHelper('my-social-network.imgix.net', '/users/1.png',
                      sign_mode=imgix.SIGNATURE_MODE_PATH)
    except Exception:
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)
    else:
        assert False


def test_create_with_url_parameters():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       sign_with_library_version=False,
                       opts={"w": 400, "h": 300})
    assert str(helper) == "https://my-social-network.imgix.net/users/1.png?" \
                          "h=300&w=400"


def test_create_with_splatted_falsy_parameter():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       sign_with_library_version=False,
                       opts={"or": 0})
    assert str(helper) == "https://my-social-network.imgix.net" \
                          "/users/1.png?or=0"


def test_create_with_signature():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       sign_key="FOO123bar",
                       sign_with_library_version=False)
    assert str(helper) == \
        "https://my-social-network.imgix.net/users/1.png" \
        "?s=6797c24146142d5b40bde3141fd3600c"


def test_create_with_paremeters_and_signature():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       sign_key="FOO123bar",
                       sign_with_library_version=False,
                       opts={"w": 400, "h": 300})
    assert str(helper) == \
        "https://my-social-network.imgix.net/users/1.png" \
        "?h=300&w=400&s=1a4e48641614d1109c6a7af51be23d18"


def test_create_with_fully_qualified_url():
    helper = UrlHelper("my-social-network.imgix.net",
                       "http://avatars.com/john-smith.png",
                       sign_key="FOO123bar",
                       sign_with_library_version=False)
    assert str(helper) == \
        "https://my-social-network.imgix.net/"\
        "http%3A%2F%2Favatars.com%2Fjohn-smith.png" \
        "?s=493a52f008c91416351f8b33d4883135"


def test_create_with_fully_qualified_url_with_special_chars():
    helper = UrlHelper("my-social-network.imgix.net",
                       u"http://avatars.com/でのパ.png",
                       sign_key="FOO123bar",
                       sign_with_library_version=False)
    assert str(helper) == "https://my-social-network.imgix.net/http%3A%2F%2F" \
                          "avatars.com%2F%E3%81%A7%E3%81%AE%E3%83%91.png" \
                          "?s=8e04a5dd9a659a6a540d7c817d3df1d3"


def test_use_https():
    # Defaults to https
    helper = UrlHelper("my-social-network.imgix.net", "/users/1.png")
    assert urlparse.urlparse(str(helper)).scheme == "https"

    helper = UrlHelper('my-social-network.imgix.net', "/users/1.png",
                       scheme="http")
    assert urlparse.urlparse(str(helper)).scheme == "http"


def test_utf_8_characters():
    helper = UrlHelper('my-social-network.imgix.net', u'/ǝ',
                       sign_with_library_version=False)
    assert str(helper) == "https://my-social-network.imgix.net/%C7%9D"


def test_more_involved_utf_8_characters():
    helper = UrlHelper('my-social-network.imgix.net',
                       u'/üsers/1/でのパ.png',
                       sign_with_library_version=False)
    assert str(helper) == 'https://my-social-network.imgix.net/' \
                          '%C3%BCsers/1/%E3%81%A7%E3%81%AE%E3%83%91.png'


def test_param_values_are_escaped():
    helper = UrlHelper('my-social-network.imgix.net', 'demo.png',
                       opts={"hello world": "interesting"},
                       sign_with_library_version=False)

    assert str(helper) == "https://my-social-network.imgix.net/demo.png?" \
                          "hello%20world=interesting"


def test_param_keys_are_escaped():
    opts = {"hello_world": "/foo\"> <script>alert(\"hacked\")</script><"}
    helper = UrlHelper('my-social-network.imgix.net', 'demo.png', opts=opts,
                       sign_with_library_version=False)

    assert str(helper) == "https://my-social-network.imgix.net/demo.png?" \
        "hello_world=%2Ffoo%22%3E%20%3Cscript%3Ealert%28%22" \
        "hacked%22%29%3C%2Fscript%3E%3C"


def test_base64_param_variants_are_base64_encoded():
    opts = {"txt64": u"I cannøt belîév∑ it wors! 😱"}
    helper = UrlHelper('my-social-network.imgix.net', '~text',
                       opts=opts,
                       sign_with_library_version=False)

    assert str(helper) == "https://my-social-network.imgix.net/~text?txt64=" \
        "SSBjYW5uw7h0IGJlbMOuw6l24oiRIGl0IHdvcu-jv3MhIPCfmLE"


def test_signing_url_with_ixlib():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png')
    assert str(helper) == (
        "https://my-social-network.imgix.net/users/1.png?ixlib=python-" +
        imgix._version.__version__)


def test_set_parameter():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       sign_with_library_version=False)

    helper.set_parameter('w', 400)
    assert str(helper) == "https://my-social-network.imgix.net/" \
                          "users/1.png?w=400"

    helper.set_parameter('h', 300)
    assert str(helper) == "https://my-social-network.imgix.net/" \
                          "users/1.png?h=300&w=400"


def test_set_parameter_with_init_opts():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       opts={"or": 0},
                       sign_with_library_version=False)

    helper.set_parameter('w', 400)
    helper.set_parameter('h', 300)
    assert str(helper) == "https://my-social-network.imgix.net" \
                          "/users/1.png?h=300&or=0&w=400"


def test_set_parameter_base64_encoded():
    helper = UrlHelper('my-social-network.imgix.net', '~text',
                       sign_with_library_version=False)

    helper.set_parameter("txt64", u"I cannøt belîév∑ it wors! 😱")
    assert str(helper) == "https://my-social-network.imgix.net/~text?txt64=" \
                          "SSBjYW5uw7h0IGJlbMOuw6l24oiRIGl0IHdvcu-jv3MhIPCfmLE"


def test_set_parameter_with_none_value():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       opts={'h': 300, 'w': 400},
                       sign_with_library_version=False)

    helper.set_parameter("w", None)
    assert str(helper) == "https://my-social-network.imgix.net" \
                          "/users/1.png?h=300"


def test_set_parameter_with_false_value():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       opts={'h': 300, 'w': 400},
                       sign_with_library_version=False)

    helper.set_parameter("w", False)
    assert str(helper) == "https://my-social-network.imgix.net" \
                          "/users/1.png?h=300"


def test_delete_parameter():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       opts={'h': 300, 'w': 400},
                       sign_with_library_version=False)

    helper.delete_parameter('w')
    assert str(helper) == "https://my-social-network.imgix.net" \
                          "/users/1.png?h=300"


def test_delete_all_parameters():
    helper = UrlHelper('my-social-network.imgix.net', '/users/1.png',
                       opts={'h': 300, 'w': 400},
                       sign_with_library_version=False)

    helper.delete_parameter('w')
    helper.delete_parameter('h')
    assert str(helper) == "https://my-social-network.imgix.net/users/1.png"
