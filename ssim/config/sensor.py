from django import forms
from copy import copy
from xml.dom.minidom import parse, parseString
from symantec.ssim.OrderedDict import *

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
    def __init__(self, name = 'MyName', title = 'MyTitle', type='MyType', required=False, value='', enumvalues = None, encrypted = False):
        if enumvalues is None:
            enumvalues = []
        self.name = name
        self.title = title
        self.type = type
        self.enumvalues = enumvalues

        self.required = False
        if required == 'true':
            self.required = True

        self.value = value
        self.encrypted = False
        if encrypted == 'true':
            self.encrypted = True

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
    

def get_sensor_specs(dom):
    """
        Extract all sensor specs from document
    """
    sensor_spec = OrderedDict()
    sensor_spec_node = dom.getElementsByTagName("sensor-spec")[0]
    sensor_spec_properties = sensor_spec_node.getElementsByTagName("property")
    for item in sensor_spec_properties:
        name = item.getAttribute('name')
        title = item.getAttribute('description')
        type = item.getAttribute('type')
        value = item.getAttribute('default')
        required = item.getAttribute('required')
        encrypted = item.getAttribute('encrypted')

        choices = []
        enumvalues = item.getAttribute('enumvalues')
        if enumvalues:
            for ent in enumvalues.split(','):
                choices.append((ent,ent))
        sensor_spec[name] = SensorField(name=name, title=title,type=type,value=value, required=required, enumvalues=choices, encrypted=encrypted)
    return sensor_spec

def parse_sensor_data(sensor_xml, sensor_name):
    #parse XML
    dom = parseString(sensor_xml)
    #get all sensors
    sensor_nodes = dom.getElementsByTagName("sensor")
    #create new sensor instance
    sensor = None #init variable
    # get sensor_spec
    sensor_spec = get_sensor_specs(dom)
    # get all sensor data
    if sensor_name:
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
    else:
        sensor = Sensor(name="Sensor %s" % len(sensor_nodes), enabled='disabled') #init variable
        for field_name in sensor_spec:
            sensor.fields += [sensor_spec[field_name]]

    return sensor

def delete_all_childs(node):
    if node.childNodes:
        for child in node.childNodes:
            node.removeChild(child)

def remove_sensor_from_xml(sensor_xml, sensor_name):
    #parse XML
    dom = parseString(sensor_xml)
    #get all sensors
    sensors = dom.getElementsByTagName("sensors")[0]
    sensor_nodes = dom.getElementsByTagName("sensor")
    for item in sensor_nodes:
        name = item.getAttribute('name')
        if name == sensor_name:
            sensors.removeChild(item)
            break

    return dom.toxml()

def update_sensor_xml(form):
    sensor_name = form.sensor_name
    #parse XML
    dom = parseString(form.sensor_xml)
    #get all sensors
    sensor_nodes = dom.getElementsByTagName("sensor")
    # get all sensor data
    if sensor_name:
        for item in sensor_nodes:
            name = item.getAttribute('name')
            if name == sensor_name:
                for property in item.getElementsByTagName('property'):
                    name = property.getAttribute('name')
                    delete_all_childs(property)
                    txt = dom.createTextNode(form.data[name])
                    property.appendChild(txt)
    else:
        index = len(sensor_nodes) + 1
        sensor_name = "Sensor %s" % index
        # get sensor_spec
        sensor_spec = get_sensor_specs(dom)
        sensor = dom.createElement('sensor')
        sensor.setAttribute('enabled', 'false')
        sensor.setAttribute('name', sensor_name)
        #add all fields
        for name in sensor_spec:
            property = dom.createElement('property')
            property.setAttribute('name', name)
            field = sensor_spec[name]
            property.setAttribute('encrypted', ('%s' % field.encrypted).lower())
            txt = dom.createTextNode(form.data[name])
            property.appendChild(txt)
            sensor.appendChild(property)
        #add new sensor
        sensors = dom.getElementsByTagName("sensors")[0]
        sensors.appendChild(sensor);
        

    return sensor_name, dom.toxml()

def get_form_field(field):
    if field.type == 'int':
        return forms.IntegerField(label=field.title, required=field.required, initial = field.value, widget=textWidget)
    elif field.type == 'password':
        return forms.CharField(label=field.title, required=field.required, initial = field.value, widget=passwordWidget)
    elif field.type == 'enum':
        return forms.ChoiceField(label=field.title, required=field.required, initial = field.value, choices = field.enumvalues, widget=copy(selectWidget))
    elif field.type == 'boolean':
        return forms.BooleanField(label=field.title, required=field.required, initial = field.value, widget=checkboxWidget)

    return forms.CharField(label=field.title, required=field.required, initial = field.value, widget=textWidget)

def get_sensor_form(sensor_xml, sensor_name = None):
    """Return the form for a specific Board."""
    sensor_instance = parse_sensor_data(sensor_xml, sensor_name)
    class SensorForm(forms.Form):
        def __init__(self, *args, **kwargs):
                forms.Form.__init__(self, *args, **kwargs)
                self.sensor_xml = sensor_xml
                self.sensor_name = sensor_name
        def update_xml(self):
                return update_sensor_xml(self)
    setattr(SensorForm, 'sensor', sensor_instance)
    for field in sensor_instance.fields:
        setattr(SensorForm, field.name, get_form_field(field))
    return type('SensorForm', (forms.Form, ), dict(SensorForm.__dict__))


