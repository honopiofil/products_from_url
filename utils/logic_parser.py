def attrib_logic_parser(logic_string):
    attrib_name, attrib_value = logic_string.split(',')
    operators = {'AND': 'and', 'OR': 'or', 'NOT': 'not'}
    converted_string = f"tag.get('{attrib_name}') and "
    for token in attrib_value.split():
        if token in operators:
            converted_string += f' {token.lower()} '
        else:
            bra = '(' if token.startswith('(') else ''
            ket = ')' if token.endswith(')') else ''
            token = token.replace("(", "").replace(")", "")
            converted_string += bra + f"any('{token}' in cls for cls in tag.get('{attrib_name}'))" + ket
    return converted_string


def tag_name_logic_parser(logic_string):
    converted_string = f"tag.name and tag.name in ['"
    converted_string += "' ,'".join(logic_string.split(','))
    converted_string += "'] and "
    return converted_string


def get_tag_list(tag_string):
    return eval("['" + "' ,'".join(tag_string.split(',')) + "']")


def product_rule_parser(tag_name, attribute):
    tag_logic_string = tag_name_logic_parser(tag_name)
    attribute_logic_string = attrib_logic_parser(attribute)
    return tag_logic_string + attribute_logic_string
