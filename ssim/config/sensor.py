from django import forms
from copy import copy
from xml.dom.minidom import parse, parseString

textWidget = forms.TextInput(attrs={'class':'text ui-widget-content ui-corner-all'})
passwordWidget = forms.PasswordInput(attrs={'class':'text ui-widget-content ui-corner-all'})
selectWidget = forms.Select(attrs={'class':'ui-widget-content ui-corner-all'})
checkboxWidget = forms.CheckboxInput(attrs={'class':'text ui-widget-content ui-corner-all'})

class Sensor:
    def __init__(self, name = 'Undefined', enabled = False, fields = None):
        if fields is None:
            fields = []
        self.name = name
        self.enabled = enabled
        self.fields = fields

class SensorField:
    def __init__(self, name = 'MyName', title = 'MyTitle', type='MyType', required=False, value='', enumvalues=[]):
        self.name = name
        self.title = title
        self.type = type
        self.enumvalues = enumvalues

        self.required = False
        if required == 'true':
            self.required = True

        self.value = value

    def __str__(self):
        return "%s(%s)" % (self.name, self.type)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def get_all_sensors(sensor_xml):
    sensor_list = []
    dom = parseString(sensor_xml)
    sensor_nodes = dom.getElementsByTagName("sensor")
    for item in sensor_nodes:
        name = item.getAttribute('name')
        enabled = item.getAttribute('enabled')
        sensor_list += [Sensor(name=name, enabled=enabled)]
    return sensor_list
    

def parse_sensor_data(sensor_xml, sensor_name):
    sensor = None #init variable
    dom = parseString(sensor_xml)
    # get sensor_spec
    sensor_spec = {}
    sensor_spec_node = dom.getElementsByTagName("sensor-spec")[0]
    sensor_spec_properties = sensor_spec_node.getElementsByTagName("property")
    for item in sensor_spec_properties:
        name = item.getAttribute('name')
        title = item.getAttribute('description')
        type = item.getAttribute('type')
        value = item.getAttribute('default')
        required = item.getAttribute('required')

        choices = []
        enumvalues = item.getAttribute('enumvalues')
        if enumvalues:
            for ent in enumvalues.split(','):
                choices.append((ent,ent))
        sensor_spec[name] = SensorField(name=name, title=title,type=type,value=value, required=required, enumvalues=choices)

    # get all sensor data
    sensor_nodes = dom.getElementsByTagName("sensor")
    for item in sensor_nodes:
        name = item.getAttribute('name')
        if name == sensor_name:
            enabled = item.getAttribute('enabled')
            sensor = Sensor(name=name, enabled=enabled)
            
            sensor_properties = item.getElementsByTagName("property")
            for property in sensor_properties:
                name = property.getAttribute('name')
                value = getText(property.childNodes)
                sensor_field = copy(sensor_spec[name])
                sensor_field.value = value
                sensor.fields += [sensor_field]
            break
    return sensor

def get_form_field(field):
    if field.type == 'int':
        return forms.IntegerField(label=field.title, required=field.required, initial = field.value, widget=textWidget)
    elif field.type == 'password':
        return forms.CharField(label=field.title, required=field.required, initial = field.value, widget=passwordWidget)
    elif field.type == 'enum':
        return forms.ChoiceField(label=field.title, required=field.required, initial = field.value, choices = field.enumvalues, widget=selectWidget)
    elif field.type == 'boolean':
        return forms.BooleanField(label=field.title, required=field.required, initial = field.value, widget=checkboxWidget)

    return forms.CharField(label=field.title, required=field.required, initial = field.value, widget=textWidget)

def get_sensor_form(sensor_xml, sensor_name = None):
    """Return the form for a specific Board."""
    sensor_instance = parse_sensor_data(sensor_xml, sensor_name)
    class SensorForm(forms.Form):
        def __init__(self, *args, **kwargs):
                forms.Form.__init__(self, *args, **kwargs)
        def save(self):
                "Do the save"
    setattr(SensorForm, 'sensor', sensor_instance)
    for field in sensor_instance.fields:
        setattr(SensorForm, field.name, copy(get_form_field(field)))
    return type('SensorForm', (forms.Form, ), dict(SensorForm.__dict__))


