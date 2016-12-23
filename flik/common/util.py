
def quote(toquote):
    result = toquote
    for character in '& _|':
        result = result.replace(character, '_')
    return result

