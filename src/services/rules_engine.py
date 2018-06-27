# -*- coding: UTF-8 -*-
'''
:Authors
    - Enzo D. Grosso
'''

from flask import current_app
from utils.toolbox import indexOf, BussinessException, asNumber, RESERVED_WORDS, ACUMULADORES
# from datetime import datetime
import dateutil.parser as date_parser
import time


# ACUMULADORES = {'suma': 'sum', 'maximo': 'max', 'minimo': 'min', 'promedio': 'average', 'contar': 'count'}


class StringBuilder():

	strings = []

	def append(self, value):

		value = self.verify(value)
		if value is not '':
			self.strings.append(value)

	def appendLine(self, value):

		value = self.verify(value)
		if self.isEmpty():
			self.strings.append(value)
		else:
			self.strings.append('\n' + value)

	def clear(self):

		del self.strings[:]

	def isEmpty(self):

		return len(self.strings) == 0

	def build(self):
		return ''.join(self.strings)

	def verify(self, value):

		if value is None:
			return ''
		else:
			return str(value)


def getStringBuilder():
	return StringBuilder()


def getBinding(entity, attr, tipo):
	return '$jjuhnu' + entity + attr + tipo


def getAcums(data, array):
	try:
		final = []

		for cond in array:
			if 'parentesis' in cond and cond['parentesis'] is True:
				continue
			for rest in cond['conds']:
				if rest['operator'] != 'en' and rest['operator'] != 'entre' and 'formula' in rest and rest['formula'] is not None and rest['formula'] != {}:

					final.append(rest['formula']['acums'])
					if 'types' in rest['formula'] and rest['formula']['types'] is not None and 'types' in data and data['types'] is not None:

						for tp in rest['formula']['types']:
							if tp not in data['types']:
								data['types'].append(tp)

		if 'actions' in data and data['actions'] is not None:

			for act in data['actions']:

				if 'formula' in act and act['formula'] is not None and act['formula'] != {}:

					if 'acums' in act['formula'] and act['formula']['acums'] is not None and act['formula']['acums'].strip() != '' and act['formula']['acums'] not in final:

						final.append(act['formula']['acums'])

					if 'types' in act['formula'] and act['formula']['types'] is not None and 'types' in data and data['types'] is not None:

						for tp in act['formula']['types']:
							if tp not in data['types']:
								data['types'].append(tp)

		return '\n\t'.join(final)

	except Exception as e:
		raise e


def inyectContCond(binding, conds, actions):

	if conds is None or actions is None or binding is None:
		return

	for action in actions:
		if 'message' in action and action['message'] is True:
			continue

		if ('formula' in action and action['formula'] is not None and action['formula'] != {}) or ('funct' in action and action['funct'] is not None and action['funct'] != {}):
			continue

		bind = action['binding']['name'].split('.', 1)

		if binding == '$' + bind[0]:
			cond = {'attr': {'name': bind[1], 'type': action['binding']['type']}, 'value': action['value'], 'binding': '', 'used': False, 'connector': ',', 'operator': '!='}
			conds.append(cond)


def inyectControl(binding, conds, ruleName):

	if conds is None or binding is None or ruleName is None:
		return

	cond = {'attr': {'name': '("' + ruleName + '|"+fact_id.toString())', 'type': 'long'}, 'value': '', 'binding': '', 'used': False, 'connector': ',', 'operator': 'no en', 'memberOf': '$SRC.rules'}

	conds.append(cond)


def makeRuleMVEL(jsonObject, functNames=[]):
    '''
    jjuhnu
    '''
    sb = getStringBuilder()

    sb.clear()

    cCond = False

    if 'contraCondicion' in jsonObject and jsonObject['contraCondicion'] is not None:
        cCond = jsonObject['contraCondicion']

    globalRuleName = jsonObject['name']

    sb.appendLine('rule "' + globalRuleName + '"')

    sb.appendLine('dialect "mvel"')

    if 'salience' in jsonObject and jsonObject['salience'] is not None:
        sb.appendLine('salience ' + str(jsonObject['salience']))

    sb.appendLine('no-loop true')

    if 'duration' in jsonObject and jsonObject['duration'] is not None:
        sb.appendLine('duration ' + str(jsonObject['duration']))

    sb.appendLine('when')
    sb.appendLine('\t$SRC: SystemControl()')

    list = jsonObject['rules']

    accumulators = getAcums(jsonObject, list)

    if accumulators is not None and accumulators != '':
        sb.appendLine('\t' + accumulators)

    parentesis = '('

    globalBindings = []

    for rule in list:

        if 'parentesis' in rule and rule['parentesis'] is True:
            sb.appendLine('\t' + parentesis)

            if parentesis == '(':
                parentesis = ')'
            else:
                parentesis = '('

            continue

        if list.index(rule) > 0:

            if 'connector' in rule and rule['connector'] is not None and rule['connector'] == '||':
                sb.appendLine('\t' + rule['connector'])

        typeName = upcase_first_letter(rule['type'])
        conds = rule['conds']
        sb.appendLine('\t')

        if 'binding' in rule and rule['binding'] != '':
            sb.append(rule['binding'] + ":")
            globalBindings.append(rule['binding'])

            if cCond:
                inyectContCond(rule['binding'], conds, jsonObject['actions'])

            if 'limited' in jsonObject and jsonObject['limited'] is True:
                inyectControl(rule['binding'], conds, globalRuleName)

        sb.append(typeName + '(')
        for cond in conds:

            if conds.index(cond) > 0:
                if 'connector' in cond and cond['connector'] is not None:
                    sb.append(' ' + cond['connector'] + ' ')
                else:
                    sb.append(' && ')

            if 'formula' in cond and cond['formula'] is not None and cond['formula'] != {}:

                attrName = cond['attr']['name'].replace(' ', '_')
                conector = cond['operator']
                value = cond['formula']['formula']

                if 'binding' in cond and cond['binding'] != '':
                    sb.append(cond['binding'] + ':')

                sb.append(attrName + ' ' + conector + ' (' + value + ')')

            elif 'funct' in cond and cond['funct'] is not None and cond['funct'] != {}:

                attrName = cond['attr']['name'].replace(' ', '_')
                conector = cond['operator']
                value = 'f_' + cond['funct']['name'] + '({0})'
                functNames.append(cond['funct']['name'])

                fields = []

                for rep in cond['funct']['fields']:
                    if indexOf(rep['name'], '$PCList') == 0:
                        rep['name'] = rep['name'].split('.', 1)[1]

                        rep['name'] = 'rulzConstant.get("' + rep['name'] + '")'

                    elif indexOf(rep['name'], '$PC') == 0:
                        rep['name'] = rep['name'].split('.', 1)[1]

                        rep['name'] = 'rulzConstant.get("' + rep['name'] + '")[0]'

                    elif indexOf(rep['name'], '$') == 0:
                        pass

                    elif rep['type'] == 'String':
                        rep['name'] = '"' + rep['name'] + '"'

                    fields.append(rep['name'])

                value = value.format(', '.join(fields))

                if 'binding' in cond and cond['binding'] != '':
                    sb.append(cond['binding'] + ':')

                sb.append(attrName + ' ' + conector + ' ' + value)

            elif 'cep' not in cond or cond['cep'] is None or not cond['cep']:

                attrName = cond['attr']['name'].replace(' ', '_')
                attrType = cond['attr']['type']
                value = cond['value']
                conector = cond['operator']

                if conector == 'en':
                    cond['memberOf'] = 'rulzConstant.get("' + cond['memberOf'] + '")'

                    if attrType == 'date':
                        sb.append('(' + attrName + '!=null && ')
                        attrName = attrName + '.getTime()'
                        cond['memberOf'] += ')'

                    sb.append(attrName + " memberOf " + cond['memberOf'])

                elif conector == 'no en':
                    cond['memberOf'] = 'rulzConstant.get("' + cond['memberOf'] + '")'

                    if attrType == 'date':
                        sb.append('(' + attrName + '== null || ')
                        attrName = attrName + '.getTime()'
                        cond['memberOf'] += ')'

                    sb.append(attrName + " not memberOf " + cond['memberOf'])

                elif conector == 'entre':

                    if 'value2' in cond and cond['value2'] is not None:
                        value2 = cond['value2']
                    else:
                        value2 = 0

                    if asNumber(value) < asNumber(value2):
                        sb.append(attrName + ' > ' + str(value) + ' && < ' + str(value2))
                    else:
                        sb.append(attrName + ' > ' + str(value2) + ' && < ' + str(value))

                elif conector == 'contiene':

                    if indexOf(value, '$PC') == 0:
                        value = value.split('.', 1)[1]

                        sb.append('rulzConstant.get("' + value + '") != null && ')
                        value = 'rulzConstant.get("' + value + '").get(0)'

                    elif attrType == 'string':
                        if indexOf(value, '$') != 0:
                            value = '"' + value + '"'

                    sb.append(attrName + ' contains ' + value)

                elif conector == 'comienza con':
                    if indexOf(value, '$PC') == 0:
                        value = value.split('.', 1)[1]

                        sb.append('rulzConstant.get("' + value + '") != null && ')
                        value = 'rulzConstant.get("' + value + '")[0]'

                    elif attrType == 'string':
                        if indexOf(value, '$') != 0:
                            value = '"' + value + '"'

                    sb.append(attrName + ' str[startsWith] ' + value)

                elif conector == 'termina con':
                    if indexOf(value, '$PC') == 0:
                        value = value.split('.', 1)[1]

                        sb.append('rulzConstant.get("' + value + '") != null && ')
                        value = 'rulzConstant.get("' + value + '")[0]'

                    elif attrType == 'string':
                        if indexOf(value, '$') != 0:
                            value = '"' + value + '"'

                    sb.append(attrName + ' str[endsWith] ' + value)

                else:

                    if indexOf(value, '$PC') == 0:
                        value = value.split('.', 1)[1]

                        sb.append('rulzConstant.get("' + value + '") != null && ')
                        value = 'rulzConstant.get("' + value + '").get(0)'

                        if attrType == 'date':
                            sb.append('(' + attrName + '!=null && ')
                            attrName = attrName + '.getTime()'
                            value += ')'

                    elif indexOf(value, '$') == 0 or value == 'null':
                        value = str(value)
                    elif attrType == 'string':
                        value = '"' + value + '"'
                    elif attrType == 'date':
                        value = getFormatedDate(value)

                        if value != 'null':
                            sb.append('(' + attrName + '!=null && ')
                            attrName = attrName + '.getTime()'
                            value += ')'

                    sb.append(attrName + ' ' + conector + ' ' + value)

            else:

                cep = cond['cep']
                start = cep['startTime']
                end = cep['endTime']
                operator = cep['tempOperator']
                binding = cep['bindingTo']
                sb.append('this ' + operator + ' [' + start + ',' + end + '] ' + binding)

        sb.append(')')

        if 'overWindowTime' in rule and rule['overWindowTime'] is not None and rule['overWindowTime'] != '':
            sb.append(" over window:time(" + rule["overWindowTime"] + ")")

    sb.appendLine('then')

    globalRuleName = jsonObject['name']

    sb.appendLine('\tlog.info("Rule: ' + globalRuleName + '");')

    globalRuleName = globalRuleName.replace(' ', '_')

    sb.appendLine('\t$SRC.rulesNames.add("' + globalRuleName + '")')

    for bi in globalBindings:
        sb.appendLine('\t$SRC.rules.add("' + globalRuleName + '|"+' + str(bi) + '.fact_id.toString())')

    sb.appendLine('\tupdate($SRC)')

    if 'actions' in jsonObject and jsonObject['actions'] is not None:

        actions = jsonObject['actions']

        for act in actions:

            if 'message' in act and act['message'] is True:
                sb.appendLine('\tmessages.add(' + str(getMessage(act['value'])) + ');')
                continue

            bind = act['binding']['name'].split('.', 1)

            if 'formula' in act and act['formula'] is not None and act['formula'] != {}:
                sb.appendLine('\tmodify ($' + bind[0] + ') {' + bind[1] + '=(' + act['formula']['formula'] + ')};')
                continue

            if 'funct' in act and act['funct'] is not None and act['funct'] != {}:

                functNames.append(act['funct']['name'])

                value = 'f_' + act['funct']['name'] + '({0})'

                fields = []

                for rep in act['funct']['fields']:

                    if indexOf(rep['name'], '$PCList') == 0:
                        rep['name'] = rep['name'].split('.', 1)[1]

                        rep['name'] = 'rulzConstant.get("' + rep['name'] + '")'

                    elif indexOf(rep['name'], '$PC') == 0:
                        rep['name'] = rep['name'].split('.', 1)[1]

                        rep['name'] = 'rulzConstant.get("' + rep['name'] + '")[0]'

                    elif indexOf(rep['name'], '$') == 0:
                        pass

                    elif rep['type'] == 'String':
                        rep['name'] = '"' + rep['name'] + '"'

                    fields.append(rep['name'])

                value = value.format(','.join(fields))

                sb.appendLine('\tmodify ($' + bind[0] + ') {' + bind[1] + '=' + value + '};')
                continue

            v = act['value']

            if 'code' in act and act['code']:
                v = '(' + str(v) + ')'

                if act['binding']['type'] == 'float':
                    v = '(Float)' + v
                elif act['binding']['type'] == 'integer':
                    v = '(Integer)' + v

            elif indexOf(v, '$') == 0 or v == 'null':
                v = v

            elif act['binding']['type'] == 'string':
                v = '"' + v + '"'

            elif act['binding']['type'] == 'boolean':

                if v == 'True' or v == 'true':
                    v = 'true'
                else:
                    v = 'false'
            else:
                v = str(v)

            sb.appendLine('\tmodify ($' + bind[0] + ') {' + bind[1] + '=' + v + '};')

    if 'halt' in jsonObject and jsonObject['halt']:
        sb.appendLine('\tkcontext.halt();')

    sb.appendLine('end')
    return sb.build()


def getMessage(value):
    try:
        splited = value.split()
        msg = []
        if len(splited) == 1:
            if indexOf(value, '$') == 0:
                return str(value)
            else:
                return '"' + str(value) + '"'
        for i, val in enumerate(splited):

            if indexOf(val, '$') == 0:
                if i != 0 and i != (len(splited) - 1):
                    val = '" + ' + str(val) + ' + "'
                elif i == 0:
                    val = str(val) + ' + "'
                else:
                    val = '" + ' + val
            else:
                if i != 0 and i != (len(splited) - 1):
                    val = str(val)
                elif i == 0:
                    val = '"' + str(val)
                else:
                    val = str(val) + '"'

            msg.append(val)

        return ' '.join(msg)

    except Exception as e:
        current_app.logger.exception(e)
        return '""'


def getField(data):
    datas = data.split('.')
    del datas[0]
    return '.'.join(datas)


def makeDeclares(type, node):

	declares = []
	try:

		declare = declareType(upcase_first_letter(type), node)
		if declare != '':
			declares.append(declare)

		if node is None or len(node) == 0:
			return declares

		for newType in node:

			if node[newType]['type'] == 'object':
				declares.extend(makeDeclares(upcase_first_letter(type) + upcase_first_letter(newType), node[newType]['properties']))

			if node[newType]['type'] == 'array' and 'items' in node and node[newType]['items']['type'] == 'object':
				declares.extend(makeDeclares(newType + 'Elements', node[newType]['items']['properties']))

	except Exception as e:

		current_app.logger.exception(e)

	return declares


def declareType(type, node):

	if type is None or type == '':
		return ''

	sb = getStringBuilder()
	sb.clear()

	sb.appendLine('declare ' + upcase_first_letter(type) + '')

	if node is not None and len(node) != 0:

		for attr in node:

			atr = attr

			sb.appendLine('\t')
			sb.append(atr + ' : ')

			if node[attr]['type'] != 'array' and node[attr]['type'] != 'object' and node[attr]['type'] != 'null':
				sb.append(upcase_first_letter(node[attr]['type']))
			if node[attr]['type'] == 'object':
				sb.append(upcase_first_letter(type) + upcase_first_letter(atr))
			if node[attr]['type'] == 'array':
				sb.append("List = new ArrayList()")
			if node[attr]['type'] == 'null':
				sb.append('Object')

			sb.append('\n')

	sb.append('\n')

	sb.append('end')

	return sb.build()


def upcase_first_letter(s):
	return s[0].upper() + s[1:]


def lowcase_first_letter(s):
	return s[0].lower() + s[1:]


def primitiveType(t):
    if t == 'string':
    	return 'String'
    elif t == 'number':
    	return 'Long'
    elif t == 'integer':
    	return 'Long'
    elif t == 'float':
    	return 'Double'
    elif t == 'boolean':
    	return 'Boolean'
    elif t == 'date':
        return 'Date'
    else:
    	return 'String'

'''
{
    "name": "string",
    "entities": [
        {
            "entity": {
                "name": "string"
            },
            "conds": [
                {
                    "type": "string",
                    "attribute": "string",
                    "connector": "string",
                    "attrType": "string"
                }
            ]
        }
    ],
    "rows": [
        {
            "entities": [
                {
                    "conds": [
                        {
                            "type": "string",
                            "value": "string",
                            "funct": "string"
                        }
                    ]
                }
            ],
            "case": "string",
            "actions": [
                {
                    "type": "string",
                    "attr": "string",
                    "entity": "string"
                    "value": "string",
                    "function": "string",
                    "functionAttr": "string"
                }
            ]
        }
    ]
}

'''


def makeTableMVEL(jsonObject, functNames=[]):
    try:
        rules = []

        rows = jsonObject['rows']

        entities = jsonObject['entities']

        r_names = []

        tptoad = []

        if 'salience' in jsonObject and jsonObject['salience'] is not None:
            salience = jsonObject['salience']
        else:
            salience = 1000

        for row in rows:

            conds = []
            actions = []
            acums = []

            ruleName = jsonObject['name'] + ' | ' + row['case'].encode("utf-8")

            actions.append('log.info("Rule: ' + ruleName + '");')
            actions.append('$SRC.rulesNames.add("' + ruleName + '")')
            r_names.append('"' + ruleName + '" not memberOf rulesNames')

            for entity in entities:
                i = entities.index(entity)

                n = entity['entity']['name'].replace(' ', '_')

                ccab = '$' + n + ':' + n

                cons = []

                for cond in entity['conds']:

                    e = entity['conds'].index(cond)

                    opType = row['entities'][i]['conds'][e]['type']

                    scd = ''

                    if opType == 'none':
                        continue

                    if opType == 'normal':

                        connector = cond['connector']
                        attrName = getField(cond['attribute'])

                        value = row['entities'][i]['conds'][e]['value']
                        attrType = cond['attrType']

                        if connector == 'en':

                            value = 'rulzConstant.get("' + value + '")'

                            if attrType == 'date':
                                scd += '(' + attrName + '!= null && ' + attrName + '.getTime() memberOf ' + value + ')'
                            else:
                                scd += attrName + " memberOf " + value
                        elif connector == 'no en':
                            value = 'rulzConstant.get("' + value + '")'

                            if attrType == 'date':
                                scd += '(' + attrName + '== null || ' + attrName + '.getTime() not memberOf ' + value + ')'
                            else:
                                scd += attrName + " not memberOf " + value
                        elif connector == 'entre':

                            if 'value2' in row['entities'][i]['conds'][e] and row['entities'][i]['conds'][e]['value2'] is not None:
                                value2 = row['entities'][i]['conds'][e]['value2']
                            else:
                                value2 = 0

                            if asNumber(value) < asNumber(value2):
                                scd += attrName + ' > ' + str(value) + ' && <' + str(value2)
                            else:
                                scd += attrName + ' > ' + str(value2) + ' && <' + str(value)

                        elif connector == 'comienza con':
                            if indexOf(value, '$PC') == 0:
                                value = value.split('.', 1)[1]

                                scd += 'rulzConstant.get("' + value + '") != null && '
                                value = 'rulzConstant.get("' + value + '")[0]'

                            elif attrType == 'string':
                                if indexOf(value, '$') != 0:
                                    value = '"' + value + '"'

                            scd += attrName + ' str[startsWith] ' + value
                        elif connector == 'termina con':
                            if indexOf(value, '$PC') == 0:
                                value = value.split('.', 1)[1]

                                scd += 'rulzConstant.get("' + value + '") != null && '
                                value = 'rulzConstant.get("' + value + '")[0]'

                            elif attrType == 'string':
                                if indexOf(value, '$') != 0:
                                    value = '"' + value + '"'

                            scd += attrName + ' str[endsWith] ' + value

                        else:
                            if indexOf(value, '$PC') == 0:
                                value = value.split('.', 1)[1]

                                scd += 'rulzConstant.get("' + value + '") != null && '
                                value = 'rulzConstant.get("' + value + '").get(0)'

                                if attrType == 'date':
                                    scd += '(' + attrName + '!=null && '
                                    attrName = attrName + '.getTime()'
                                    value += ')'

                            elif indexOf(value, '$') == 0 or value == 'null':
                                value = str(value)
                            elif attrType is not None and attrType.lower() == "string":
                                value = '"' + value + '"'
                            elif attrType == "boolean":
                                if value == "True" or value == "true" or value == "verdadero":
                                    value = 'true'
                                else:
                                    value = 'false'
                            elif attrType.lower() == "date":
                                if value != 'null':
                                    cons.append(attrName + '!=null')
                                    attrName = attrName + '.getTime()'

                                value = getFormatedDate(value)
                            else:
                                value = str(value)

                            scd += attrName + connector + value

                    elif opType == 'funct':

                        connector = cond['connector']
                        attrName = getField(cond['attribute'])

                        value = 'f_' + row['entities'][i]['conds'][e]['funct']['name'] + '({0})'

                        functNames.append(row['entities'][i]['conds'][e]['funct']['name'])

                        fields = []

                        for rep in row['entities'][i]['conds'][e]['funct']['fields']:
                            if indexOf(rep['name'], '$PCList') == 0:
                                rep['name'] = rep['name'].split('.', 1)[1]

                                rep['name'] = 'rulzConstant.get("' + rep['name'] + '")'

                            elif indexOf(rep['name'], '$PC') == 0:
                                rep['name'] = rep['name'].split('.', 1)[1]

                                rep['name'] = 'rulzConstant.get("' + rep['name'] + '")[0]'

                            elif indexOf(rep['name'], '$') == 0:
                                pass

                            elif rep['type'] == 'String':
                                rep['name'] = '"' + rep['name'] + '"'

                            fields.append(rep['name'])

                        value = value.format(','.join(fields))

                        scd += attrName + ' ' + connector + ' ' + value

                    elif opType == 'formula':

                        connector = cond['connector']
                        attrName = getField(cond['attribute'])

                        formula = row['entities'][i]['conds'][e]['formula']

                        value = '(' + formula['formula'] + ')'

                        scd += attrName + ' ' + connector + ' ' + value

                        if 'acums' in formula and formula['acums'] is not None and formula['acums'] != '' and formula['acums'] not in acums:
                            acums.append(formula['acums'])

                        for tp in formula['types']:
                            tptoad.append({'entity': {'id': tp}})

                    if scd != '':
                        cons.append(scd)

                cons.append('("' + ruleName + '|"+fact_id.toString()) not memberOf $SRC.rules')

                conds.append(getCondStructure().format(ccab, ', '.join(cons)))

                actions.append('$SRC.rules.add("' + ruleName + '|"+$' + str(n) + '.fact_id.toString())')

            for action in row['actions']:

                act = getActionMVEL(action, acums, tptoad, functNames)

                if act is not None:
                    actions.append(act)

            actions.append('update($SRC);')

            rules.append(getRuleStructure().format(ruleName, str(salience), '\n\t'.join(conds), '\n\t'.join(actions), '\n\t'.join(acums)))

            salience -= 10

        if 'default' in jsonObject and jsonObject['default'] != []:
            defConds = []

            for entity in entities:
                n = entity['entity']['name'].replace(' ', '_')

                ccab = '$' + n + ':' + n

                defConds.append(getCondStructure().format(ccab, ''))

            defActions = []

            defAcums = []

            for action in jsonObject['default']:
                act = getActionMVEL(action, defAcums, tptoad, functNames)

                if act is not None:
                    defActions.append(act)

            ruleName = jsonObject['name'] + ' | DefaultRule'

            rules.append(getRuleStructure().format(ruleName, str(salience), '\n\t'.join(defConds), '\n\t'.join(defActions), '\n\t'.join(defAcums)))

        if 'different' in jsonObject and jsonObject['different'] != []:

            diffConds = []

            diffConds.append('$SRC:SystemControl({0})'.format(', '.join(r_names)))

            for entity in entities:
                n = entity['entity']['name'].replace(' ', '_')

                ccab = '$' + n + ':' + n

                diffConds.append(getCondStructure().format(ccab, ''))

            defActions = []

            defAcums = []

            for action in jsonObject['different']:
                act = getActionMVEL(action, defAcums, tptoad, functNames)

                if act is not None:
                    defActions.append(act)

            ruleName = jsonObject['name'] + ' | DifferentRule'

            rules.append(getRuleStructureNoSRC().format(ruleName, str(salience), '\n\t'.join(diffConds), '\n\t'.join(defActions), '\n\t'.join(defAcums)))

        jsonObject['entities'].extend(tptoad)

        return '\n\n'.join(rules)
    except Exception as e:
        current_app.logger.exception(e)
        return ''


def getActionMVEL(action, acums, tptoad, functNames=[]):
    actType = None

    if 'type' in action:
        actType = action.get('type')

    if actType is None:
        return None

    elif actType == 'modify':

        v = action['value']

        if indexOf(v, '$') == 0 or v == 'null':
            v = str(v)
        elif action['attr']['type'].lower() == 'string':
            v = '"' + v + '"'
        elif action['attr']['type'].lower() == 'boolean':
            if v == 'true' or v == 'True':
                v = 'true'
            else:
                v = 'false'
        else:
            v = str(v)

        act = 'modify($' + action['entity'] + ') {' + action['attr']['name'] + '=' + v + '};'

    elif actType == 'function':

        value = 'f_' + action['funct']['name'] + '({0})'

        functNames.append(action['funct']['name'])

        fields = []

        for rep in action['funct']['fields']:

            if indexOf(rep['name'], '$PCList') == 0:
                rep['name'] = rep['name'].split('.', 1)[1]

                rep['name'] = 'rulzConstant.get("' + rep['name'] + '")'

            elif indexOf(rep['name'], '$PC') == 0:
                rep['name'] = rep['name'].split('.', 1)[1]

                rep['name'] = 'rulzConstant.get("' + rep['name'] + '")[0]'

            elif indexOf(rep['name'], '$') == 0:
                pass

            elif rep['type'] == 'String':
                rep['name'] = '"' + rep['name'] + '"'

            fields.append(rep['name'])

        value = value.format(','.join(fields))

        act = 'modify($' + action['entity'] + ') {' + action['attr']['name'] + '=' + value + '};'

    elif actType == 'formula':

        formula = action['formula']

        value = '(' + formula['formula'] + ')'

        act = 'modify($' + action['entity'] + ') {' + action['attr']['name'] + '=' + value + '};'

        if 'acums' in formula and formula['acums'] is not None and formula['acums'] != '' and formula['acums'] not in acums:
            acums.append(formula['acums'])

        for tp in formula['types']:
            tptoad.append({'entity': {'id': tp}})

    elif actType == 'message':
        act = 'messages.add(' + str(getMessage(action['value'])) + ');'

    else:
        return None

    return act


def getFormatedDate(value):
    if value == 'null':
        return value

    dt = date_parser.parse(value)
    return str(int(round(time.mktime(dt.timetuple()) * 1000)))


def makeFunctionMVEL(data):
    try:
        params = []

        for param in data['params']:
            params.append(param['type'] + ' ' + param['name'])

        params = ', '.join(params)

        function = getFunctionStructure().format(data['returnType'], 'f_' + data['name'], params, data['body'])

        return function
    except Exception, e:
    	current_app.logger.error(e)
    	raise e


def makeFormula(string, name='tmp'):

	acums = []
	index = 0
	outlst = []

	nameToUse = name.replace(' ', '_')

	if string.strip() == '':
		raise BussinessException('Linea vacia')

	tokenlst = string.strip().split()

	for token in tokenlst:

		if asNumber(token) is not None:
			outlst.append(token)
		elif len(token.split('(')) != 0 and ''.join(token.split('(')) != '' and token.split('(')[0] in RESERVED_WORDS:
			sp = token.split('(')
			acum = sp[0]
			val = sp[1].split(')')[0]
			ent = str(val.split('.', 1)[0])
			attr = str(val.split('.', 1)[1])
			acums.append('$' + nameToUse + str(index) + ':' + 'Number() from accumulate (' + ent + '($' + attr.replace('.', '_') + ':' + attr + '),' + str(ACUMULADORES[acum]) + '($' + attr.replace('.', '_') + '))')
			outlst.append('$' + nameToUse + str(index))
			index += 1
		else:
			outlst.append(token)

	return {'acums': '\n\t'.join(acums), 'formula': ' '.join(outlst)}


def getStructure():
    structure = '''package com.leafnoise.pathfinder.analyzer.service
import java.util.*;

dialect "{2}"

global org.apache.log4j.Logger log;
global java.util.List messages;
global com.leafnoise.pathfinder.analyzer.utils.Constants rulzConstant;

declare SystemControl
    rules: List = new LinkedList()
    rulesNames: Set = new HashSet()
end

{0}

{3}

rule "Init"
no-loop true
salience 20000
dialect "{2}"
when
    not SystemControl()
then
    insert (new SystemControl());
end

{1}'''

    return structure


def getFunctionStructure():

    structure = '''function {0} {1}({2}){{
    {3}
}}
    '''

    return structure


def getRuleStructure():

    structure = '''rule "{0}"
no-loop true
salience {1}
when
    $SRC: SystemControl()
    {4}
    {2}
then
    {3}
end'''

    return structure


def getRuleStructureNoSRC():

    structure = '''rule "{0}"
no-loop true
salience {1}
when
    {4}
    {2}
then
    {3}
end'''

    return structure


def getCondStructure():

    structure = '''{0}({1})'''

    return structure
