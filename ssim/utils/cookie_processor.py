import re

def get_cookies(response):
    cookies = {}
    set_cookie = response.getheader('set-cookie')
    if set_cookie:
        cookie_list = _normalized_cookie_tuples( _parse_ns_headers(set_cookie) )
        for tup in cookie_list:
            name, value, standard, rest = tup
            cookies[name] = value
    return cookies

def _parse_ns_headers(ns_header):
    """Ad-hoc parser for Netscape protocol cookie-attributes.

    The old Netscape cookie format for Set-Cookie can for instance contain
    an unquoted "," in the expires field, so we have to use this ad-hoc
    parser instead of split_header_words.

    XXX This may not make the best possible effort to parse all the crap
    that Netscape Cookie headers contain.  Ronald Tschalar's HTTPClient
    parser is probably better, so could do worse than following that if
    this ever gives any trouble.

    Currently, this is also used for parsing RFC 2109 cookies.

    """
    known_attrs = ("expires", "domain", "path", "secure",
                   # RFC 2109 attrs (may turn up in Netscape cookies, too)
                   "port", "max-age")

    result = []

    pairs = []
    version_set = False
    for ii, param in enumerate(re.split(r";\s*", ns_header)):
        param = param.rstrip()
        if param == "": continue
        if "=" not in param:
            k, v = param, None
        else:
            k, v = re.split(r"\s*=\s*", param, 1)
            k = k.lstrip()
        if ii != 0:
            lc = k.lower()
            if lc in known_attrs:
                k = lc
            if k == "version":
                # This is an RFC 2109 cookie.
                version_set = True
            if k == "expires":
                # convert expires date to seconds since epoch
                if v.startswith('"'): v = v[1:]
                if v.endswith('"'): v = v[:-1]
                v = http2time(v)  # None if invalid
        pairs.append((k, v))

    if pairs:
        if not version_set:
            pairs.append(("version", "0"))
        result.append(pairs)

    return result

def _normalized_cookie_tuples(attrs_set):
    """Return list of tuples containing normalised cookie information.

    attrs_set is the list of lists of key,value pairs extracted from
    the Set-Cookie or Set-Cookie2 headers.

    Tuples are name, value, standard, rest, where name and value are the
    cookie name and value, standard is a dictionary containing the standard
    cookie-attributes (discard, secure, version, expires or max-age,
    domain, path and port) and rest is a dictionary containing the rest of
    the cookie-attributes.

    """
    cookie_tuples = []

    boolean_attrs = "discard", "secure"
    value_attrs = ("version",
                   "expires", "max-age",
                   "domain", "path", "port",
                   "comment", "commenturl")

    for cookie_attrs in attrs_set:
        name, value = cookie_attrs[0]

        # Build dictionary of standard cookie-attributes (standard) and
        # dictionary of other cookie-attributes (rest).

        # Note: expiry time is normalised to seconds since epoch.  V0
        # cookies should have the Expires cookie-attribute, and V1 cookies
        # should have Max-Age, but since V1 includes RFC 2109 cookies (and
        # since V0 cookies may be a mish-mash of Netscape and RFC 2109), we
        # accept either (but prefer Max-Age).
        max_age_set = False

        bad_cookie = False

        standard = {}
        rest = {}
        for k, v in cookie_attrs[1:]:
            lc = k.lower()
            # don't lose case distinction for unknown fields
            if lc in value_attrs or lc in boolean_attrs:
                k = lc
            if k in boolean_attrs and v is None:
                # boolean cookie-attribute is present, but has no value
                # (like "discard", rather than "port=80")
                v = True
            if k in standard:
                # only first value is significant
                continue
            if k == "domain":
                if v is None:
                    _debug("   missing value for domain attribute")
                    bad_cookie = True
                    break
                # RFC 2965 section 3.3.3
                v = v.lower()
            if k == "expires":
                if max_age_set:
                    # Prefer max-age to expires (like Mozilla)
                    continue
                if v is None:
                    _debug("   missing or invalid value for expires "
                          "attribute: treating as session cookie")
                    continue
            if k == "max-age":
                max_age_set = True
                try:
                    v = int(v)
                except ValueError:
                    _debug("   missing or invalid (non-numeric) value for "
                          "max-age attribute")
                    bad_cookie = True
                    break
                # convert RFC 2965 Max-Age to seconds since epoch
                # XXX Strictly you're supposed to follow RFC 2616
                #   age-calculation rules.  Remember that zero Max-Age is a
                #   is a request to discard (old and new) cookie, though.
                k = "expires"
                v = self._now + v
            if (k in value_attrs) or (k in boolean_attrs):
                if (v is None and
                    k not in ("port", "comment", "commenturl")):
                    _debug("   missing value for %s attribute" % k)
                    bad_cookie = True
                    break
                standard[k] = v
            else:
                rest[k] = v

        if bad_cookie:
            continue

        cookie_tuples.append((name, value, standard, rest))

    return cookie_tuples