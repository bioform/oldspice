import xml.sax.handler

class Stats:
    def __init__(self, attributes, counter):
        self.module_name = attributes['name']
        self.counter = counter
        self.count = 0
        self.rate = 0
        self.rate_history = []

    def parse(self, attributes):
        #parse attributes
        self.count = attributes['count']
        self.rate = attributes['rate']
        self.counter = attributes['name']
        self.rate_history = attributes['rate_history'].split(',')

class EventHandler(xml.sax.handler.ContentHandler):
  def __init__(self, counter = 'Received Events'):
    self.stats = None
    self.counter = counter

  def startElement(self, name, attributes):
    if name == "MODULE":
      self.stats = Stats(attributes, self.counter)
    elif name == "COUNTER" and attributes['name'] == self.counter:
      self.stats.parse(attributes)

  def characters(self, data):
    #NOT USED yet
    self.buffer += data

  def endElement(self, name):
    self.buffer = ""