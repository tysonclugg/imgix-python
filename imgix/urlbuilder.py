# -*- coding: utf-8 -*-

import warnings
import zlib

from .urlhelper import UrlHelper

from .constants import SHARD_STRATEGY_CYCLE
from .constants import SHARD_STRATEGY_CRC


class UrlBuilder(object):
    """
    Create imgix URLs

    The URL builder can be reused to create URLs for any images on the
    provided domains.

    Parameters
    ----------
    domains : str or array_like
        Domain(s) to use while creating imgix URLs.
    use_https : bool
        If `True`, create HTTPS imgix image URLs. (default `True`)
    sign_key : str or None
        When provided, this key will be used to sign the generated image URLs.
        You can read more about URL signing on our docs:
        https://docs.imgix.com/setup/securing-images
    sign_mode : `SIGNATURE_MODE_QUERY`
        *Deprecated* If `SIGNATURE_MODE_QUERY`, sign the whole URL.
        (default `SIGNATURE_MODE_QUERY`)
    shard_strategy : {`SHARD_STRATEGY_CRC`, `SHARD_STRATEGY_CYCLE`}
        If `SHARD_STRATEGY_CRC`, domain sharding performed using a checksum to
        ensure image path always resolves to the same domain. If
        `SHARD_STRATEGY_CYCLE`, domain sharding performed by sequentially
        cycling through the domains list.  (default `SHARD_STRATEGY_CRC`)
    sign_with_library_version : bool
        If `True`, each created URL is suffixed with 'ixlib' parameter
        indicating the library used for generating the URLs. (default `True`)

    Methods
    -------
    create_url(path, opts={})
        Create URL with the supplied path and `opts` parameters dict.
    """
    def __init__(
            self,
            domains,
            use_https=True,
            sign_key=None,
            sign_mode=None,
            shard_strategy=SHARD_STRATEGY_CRC,
            sign_with_library_version=True):

        if sign_mode is not None:
            warnings.warn("`sign_mode` argument is deprecated and will be "
                          "removed in v2.0", DeprecationWarning, stacklevel=2)

        if not isinstance(domains, (list, tuple)):
            domains = [domains]

        self._domains = domains
        self._sign_key = sign_key
        self._sign_mode = sign_mode
        self._use_https = use_https
        self._shard_strategy = shard_strategy
        self._shard_next_index = 0
        self._sign_with_library_version = sign_with_library_version

    def create_url(self, path, opts={}):
        """
        Create URL with supplied path and `opts` parameters dict.

        Parameters
        ----------
        path : str
        opts : dict
            Dictionary specifying URL parameters. Non-imgix parameters are
            added to the URL unprocessed. For a complete list of imgix
            supported parameters, visit https://docs.imgix.com/apis/url .
            (default {})

        Returns
        -------
        str
            imgix URL
        """
        if self._shard_strategy == SHARD_STRATEGY_CRC:
            crc = zlib.crc32(path.encode('utf-8')) & 0xffffffff
            index = crc % len(self._domains)  # Deterministically choose domain
            domain = self._domains[index]

        elif self._shard_strategy == SHARD_STRATEGY_CYCLE:
            domain = self._domains[self._shard_next_index]
            self._shard_next_index = (
                self._shard_next_index + 1) % len(self._domains)

        else:
            domain = self._domains[0]

        scheme = "https" if self._use_https else "http"

        url_obj = UrlHelper(
            domain,
            path,
            scheme,
            sign_key=self._sign_key,
            sign_mode=self._sign_mode,
            sign_with_library_version=self._sign_with_library_version,
            opts=opts)

        return str(url_obj)
