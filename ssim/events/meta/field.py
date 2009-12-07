class Field:
    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __str__(self):
        return self.name

DEFAULT_FIELD_LIST = [
    Field('event_id', 'ID'),
    Field('event_dt', 'Event Date'),
    Field('eventclass_id', 'Event Type'),
    Field('severity', 'Severity'),
    Field('machine', 'Machine'),
    Field('logged_dt', 'Logged Date'),
    Field('source_ip', 'Source IP'),
    Field('destination_ip', 'Destination IP'),
    Field('target_resource', 'Target Resource'),
    Field('event_desc', 'Event Description'),
]