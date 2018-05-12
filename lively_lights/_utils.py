from pygments import highlight, lexers, formatters
import json

def colorful_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)

    return highlight(
        formatted_json,
        lexers.JsonLexer(),
        formatters.TerminalFormatter()
    )


def print_request(mode, address, data):
    print()
    print(mode)
    print(address)
    if data:
        print(colorful_json(data))
