import xml.sax.handler

class Event:
    def __init__(self, attributes):
        self.event_dt = attributes['event_dt']
        self.guid = attributes['guid']
        self.log_dt = attributes['log_dt']
        self.fields = {}

    def add_field(self, attributes):
        self.fields[attributes['name']] = attributes['value']

class EventHandler(xml.sax.handler.ContentHandler):
  def __init__(self):
    self.inTitle = 0
    self.events = []
    self.buffer = ""
    self.currentEvent = None

  def startElement(self, name, attributes):
    if name == "EVENT":
      self.currentEvent = Event(attributes)
    elif name == "FIELD":
      self.currentEvent.add_field(attributes)

  def characters(self, data):
    #NOT USED yet
    self.buffer += data

  def endElement(self, name):
    if name == "EVENT":
      self.events += [self.currentEvent]
    self.buffer = ""