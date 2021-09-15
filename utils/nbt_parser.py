# https://notes.eatonphil.com/writing-a-simple-json-parser.html but like for nbt i guess

NBT_COMMA = ','
NBT_COLON = ':'
NBT_LEFTBRACKET = '['
NBT_RIGHTBRACKET = ']'
NBT_LEFTBRACE = '{'
NBT_RIGHTBRACE = '}'
NBT_QUOTE = '"'
NBT_WHITESPACE = [' ', '\t', '\b', '\n', '\r']
NBT_SYNTAX = [NBT_COMMA, NBT_COLON, NBT_LEFTBRACKET, NBT_RIGHTBRACKET,
               NBT_LEFTBRACE, NBT_RIGHTBRACE]

class NBTParseError(Exception):
    def __init__(self, msg):
        super(msg)


def lex_tag(string):
    nbt_tag = ''

    viable_characters = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + ['_']

    if string[0] in viable_characters:
        nbt_tag += string[0]
        string = string[1:]
    else:
        return None, string

    while string[0] in viable_characters:
        try:
            nbt_tag += string[0]
            string = string[1:]
        except IndexError:
            raise NBTParseError('Tag does not end before end of file')

    return nbt_tag, string


def lex_string(string):
    nbt_string = ''

    if string[0] == NBT_QUOTE:
        string = string[1:]
    else:
        return None, string

    for c in string:
        if c == NBT_QUOTE:
            return nbt_string, string[len(nbt_string)+1:]
        else:
            nbt_string += c

    raise NBTParseError('Expected end-of-string quote')


def lex_number(string):
    nbt_number = ''

    number_characters = [str(d) for d in range(0, 10)] + ['-', 'e', '.']

    for c in string:
        if c in number_characters:
            nbt_number += c
        else:
            break

    rest = string[len(nbt_number):]

    if not len(nbt_number):
        return None, string

    if '.' in nbt_number:
        return float(nbt_number), rest

    return int(nbt_number), rest


def lex(string):
    tokens = []

    while len(string):
        nbt_tag, string = lex_tag(string)
        if nbt_tag is not None:
            tokens.append(nbt_tag)
            continue

        nbt_string, string = lex_string(string)
        if nbt_string is not None:
            tokens.append(nbt_string)
            continue

        nbt_number, string = lex_number(string)
        if nbt_number is not None:
            tokens.append(nbt_number)
            continue

        if string[0] in NBT_WHITESPACE:
            string = string[1:]
        elif string[0] in NBT_SYNTAX:
            tokens.append(string[0])
            string = string[1:]
        else:
            raise NBTParseError(f'Unexpected character: {string[0]}')
    
    return tokens

def parse_array(tokens):
    nbt_array = []

    t = tokens[0]
    if t == NBT_RIGHTBRACKET:
        return nbt_array, tokens[1:]

    while True:
        index, colon, *tokens = tokens

        if not isinstance(index, int):
            raise NBTParseError(f'Expected index in list, got: {index}')

        if colon != NBT_COLON:
            raise NBTParseError(f'Expected colon after index, got: {colon}')

        nbt, tokens = parse(tokens)
        nbt_array.append(nbt)

        t = tokens[0]
        if t == NBT_RIGHTBRACKET:
            return nbt_array, tokens[1:]
        elif t != NBT_COMMA:
            raise NBTParseError('Expected comma after object in array')
        else:
            tokens = tokens[1:]

    raise NBTParseError('Expected end-of-array bracket')

def parse_object(tokens):
    json_object = {}

    t = tokens[0]
    if t == NBT_RIGHTBRACE:
        return json_object, tokens[1:]

    while True:
        json_key = tokens[0]
        if type(json_key) is str:
            tokens = tokens[1:]
        else:
            raise Exception(f'Expected string key, got: {json_key}')

        if tokens[0] != NBT_COLON:
            raise Exception(f'Expected colon after key in object, got: {t}')

        json_value, tokens = parse(tokens[1:])

        json_object[json_key] = json_value

        t = tokens[0]
        if t == NBT_RIGHTBRACE:
            return json_object, tokens[1:]
        elif t != NBT_COMMA:
            raise Exception('Expected comma after pair in object, got: {}'.format(t))

        tokens = tokens[1:]

    raise Exception('Expected end-of-object brace')


def parse(tokens):
    t = tokens[0]

    if t == NBT_LEFTBRACKET:
        return parse_array(tokens[1:])
    elif t == NBT_LEFTBRACE:
        return parse_object(tokens[1:])
    else:
        return t, tokens[1:]

def from_string(string):
    tokens = lex(string)
    return parse(tokens)[0]
