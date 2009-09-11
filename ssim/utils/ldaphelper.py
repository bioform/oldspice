import ldif
from StringIO import StringIO
from ldap.cidict import cidict
import datetime
import re

"""
The package has two main components: the get_search_results() function, and the LDAPSearchResult class.

The get_search_results() function simply takes the results from a search (either the synchronous ones, or the results from an asynchronous one, fetched with result()) and converts the results to a list of LDAPSearchResult objects.

An LDAPSearchResults object provides some convenience methods for getting information about a record. The get_dn() method returns the record's DN, and the following methods all provide access to the attributes or the record:

    * get_dn(): return the string DN for this record.
    * get_attributes(): get a dictionary of all of the attributes. The keys  are attribute name strings, and the values are lists of attribute value  strings.
    * set_attributes(): takes a dictionary with attribute names for keys, and  lists of attribute values for the value field.
    * has_attribute(): takes a string attribute name and returns true if that attribute name is in the dict  of attributes returned.
    * get_attr_values(): given an attribute name, this returns all of the  values for that attribute (or none if that attribute does not exist).
    * get_attr_names(): returns a list of all of the attribute names for this  record.
    * pretty_print(): returns a formatted string presentation of the record.
    * to_ldif(): returns an LDIF formatted representation of the record.

This object doesn't add much to the original returned data. It just makes it a little easier to access.


The Case Sensitivity Gotcha

There is one noteworthy detail in the code above.
The search operation returns the attributes in a dictionary.
The Python dictionary is case sensitive; the key TEST is different than the key test.

This exemplifies a minor problem in dealing with LDAP information.
Standards-compliant LDAP implementations treat some information in a case-insensitive way.
The following items are, as a rule, treated as case-insensitive:

    * Object class names: inetorgperson is treated as being the same as inetOrgPerson.
    * Attribute Names: givenName is treated as being the same as givenname.
    * Distinguished Names: DNs are case-insensitive, though the all-lower-case version of a DN is called  Normalized Form.

The main area where this problem surfaces is in retrieving information from a search.
Since the attributes are returned in a dict, they are, by default, treated as case-sensitive.
For example, attrs.has_key('objectclass') will return False if the object
class attribute name is spelled objectClass.

To resolve this problem, the Python-LDAP developers created a case-insensitive
dictionary implementation (ldap.cidict.cidict). This cidict class is used above to
wrap the returned attribute dictionary.

Make sure you do something similar in your own code, or you may end up
with false misses when you look for attributes in a case-sensitive way,
e.g. when you look for givenName in an entry where the attribute name is in the form givenname.
"""
class GeneralizedTimeZone(datetime.tzinfo):
    """This class is a basic timezone wrapper for the offset specified
       in a Generalized Time.  It is dst-ignorant."""
    def __init__(self,offsetstr="Z"):
        super(GeneralizedTimeZone, self).__init__()

        self.name = offsetstr
        self.houroffset = 0
        self.minoffset = 0

        if offsetstr == "Z":
            self.houroffset = 0
            self.minoffset = 0
        else:
            if (len(offsetstr) >= 3) and re.match(r'[-+]\d\d', offsetstr):
                self.houroffset = int(offsetstr[0:3])
                offsetstr = offsetstr[3:]
            if (len(offsetstr) >= 2) and re.match(r'\d\d', offsetstr):
                self.minoffset = int(offsetstr[0:2])
                offsetstr = offsetstr[2:]
            if len(offsetstr) > 0:
                raise ValueError()
        if self.houroffset < 0:
            self.minoffset *= -1

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.houroffset, minutes=self.minoffset)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return self.name
    
def parse_generalized_time(timestr):
    """Parses are Generalized Time string (as specified in X.680),
       returning a datetime object.  Generalized Times are stored inside
       the krbPasswordExpiration attribute in LDAP.

       This method doesn't attempt to be perfect wrt timezones.  If python
       can't be bothered to implement them, how can we..."""

    if len(timestr) < 8:
        return None
    try:
        date = timestr[:8]
        time = timestr[8:]

        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:8])

        hour = min = sec = msec = 0
        tzone = None

        if (len(time) >= 2) and re.match(r'\d', time[0]):
            hour = int(time[:2])
            time = time[2:]
            if len(time) >= 2 and (time[0] == "," or time[0] == "."):
                hour_fraction = "."
                time = time[1:]
                while (len(time) > 0) and re.match(r'\d', time[0]):
                    hour_fraction += time[0]
                    time = time[1:]
                total_secs = int(float(hour_fraction) * 3600)
                min, sec = divmod(total_secs, 60)

        if (len(time) >= 2) and re.match(r'\d', time[0]):
            min = int(time[:2])
            time = time[2:]
            if len(time) >= 2 and (time[0] == "," or time[0] == "."):
                min_fraction = "."
                time = time[1:]
                while (len(time) > 0) and re.match(r'\d', time[0]):
                    min_fraction += time[0]
                    time = time[1:]
                sec = int(float(min_fraction) * 60)

        if (len(time) >= 2) and re.match(r'\d', time[0]):
            sec = int(time[:2])
            time = time[2:]
            if len(time) >= 2 and (time[0] == "," or time[0] == "."):
                sec_fraction = "."
                time = time[1:]
                while (len(time) > 0) and re.match(r'\d', time[0]):
                    sec_fraction += time[0]
                    time = time[1:]
                msec = int(float(sec_fraction) * 1000000)

        if (len(time) > 0):
            tzone = GeneralizedTimeZone(time)

        return datetime.datetime(year, month, day, hour, min, sec, msec, tzone)

    except ValueError:
        return None

def get_search_results(results):
    """Given a set of results, return a list of LDAPSearchResult
    objects.
    """
    res = []

    if type(results) == tuple and len(results) == 2 :
        (code, arr) = results
    elif type(results) == list:
        arr = results

    if len(results) == 0:
        return res

    for item in arr:
        res.append( LDAPSearchResult(item) )

    return res

class LDAPSearchResult:
    """A class to model LDAP results.
    """

    dn = ''

    def __init__(self, entry_tuple):
        """Create a new LDAPSearchResult object."""
        (dn, attrs) = entry_tuple
        if dn:
            self.dn = dn
        else:
            return

        self.attrs = cidict(attrs)

    def get_attributes(self):
        """Get a dictionary of all attributes.
        get_attributes()->{'name1':['value1','value2',...],
				'name2: [value1...]}
        """
        return self.attrs

    def set_attributes(self, attr_dict):
        """Set the list of attributes for this record.

        The format of the dictionary should be string key, list of
        string alues. e.g. {'cn': ['M Butcher','Matt Butcher']}

        set_attributes(attr_dictionary)
        """

        self.attrs = cidict(attr_dict)

    def has_attribute(self, attr_name):
        """Returns true if there is an attribute by this name in the
        record.

        has_attribute(string attr_name)->boolean
        """
        return self.attrs.has_key( attr_name )

    def get_attr_values(self, key):
        """Get a list of attribute values.
        get_attr_values(string key)->['value1','value2']
        """
        return self.attrs[key]

    def get_attr_names(self):
        """Get a list of attribute names.
        get_attr_names()->['name1','name2',...]
        """
        return self.attrs.keys()

    def get_dn(self):
        """Get the DN string for the record.
        get_dn()->string dn
        """
        return self.dn


    def pretty_print(self):
        """Create a nice string representation of this object.

        pretty_print()->string
        """
        str = "DN: " + self.dn + "n"
        for a, v_list in self.attrs.iteritems():
            str = str + "Name: " + a + "n"
            for v in v_list:
                str = str + "  Value: " + v + "n"
        str = str + "========"
        return str

    def to_ldif(self):
        """Get an LDIF representation of this record.

        to_ldif()->string
        """
        out = StringIO()
        ldif_out = ldif.LDIFWriter(out)
        ldif_out.unparse(self.dn, dict(self.attrs))
        return out.getvalue()