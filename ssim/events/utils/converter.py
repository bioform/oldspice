from symantec.ssim.events.utils.queries import *

def create_query(data):
    if not data.get('filter'):
        return None
    view = data.get('view', None)
    view_range = data.get('view_range', None)
    time_unit = data.get('time_unit', None)
    uniq_value_by_column = data.get('uniq_value_by_column', None)
    uniq_column = data.get('uniq_column', None)

    fields = data.getlist('field')
    conditions =data.getlist('condition')
    fields_values = data.getlist('field_value')

    query = Query()
    query.type = 'archive'
    query.name = 'undefined'

    criteria = Criteria()
    criteria.name = ''
    criteria.conditions = []

    for num in range(0,len(fields)):
        condition = Condition()
        condition.operator = conditions[num]

        arg1 = Argument()
        arg1.field = Field();
        arg1.field.name = fields[num]

        arg2 = Argument()
        arg2.value = Value()
        arg2.value.text = fields_values[num]

        condition.arguments = [arg1, arg2]

        criteria.conditions += [condition]

    query.event_criterias = [criteria]
    return query

def query_for_archive(query):
    result = ""
    criterias = query.event_criterias
    if not criterias:
        criterias = query.criterias
    for criteria in criterias:
        for condition in criteria.conditions:
            field = condition.arguments[0].field.name
            if len(field) > 0:
                if len(result) != 0:
                    result += " and "
                result += condition.arguments[0].field.name
                result += condition.operator
                result += condition.arguments[1].value.text
                
    if len(result) == 0:
        result = None
    return result
