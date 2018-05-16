from pygments import highlight, lexers, formatters
import json


def set_light_multiple(bridge, light_id, data):
    return bridge.request(
        mode='PUT',
        address='/api/{}/lights/{}/state'.format(bridge.username, light_id),
        data=data,
    )


class RestDebug(object):

    def __init__(self, verbosity_level=0, colorize_output=False):
        self.verbosity_level = verbosity_level
        self.colorize_output = colorize_output

    def _format_json(self, data):
        if self.verbosity_level == 1:
            formatted_json = json.dumps(data)
        else:
            formatted_json = json.dumps(data, sort_keys=True, indent=4)

        if self.colorize_output:
            return highlight(
                formatted_json,
                lexers.JsonLexer(),
                formatters.TerminalFormatter()
            )
        else:
            return formatted_json

    def print_json(self, data):
        if not self.verbosity_level:
            return
        print(self._format_json(data))

    def print_request(self, mode, address, data):
        if not self.verbosity_level:
            return

        if self.verbosity_level >= 2:
            join_phrase = '\n'
        else:
            join_phrase = ' '

        out = [mode, address]

        if data:
            out.append(self._format_json(data))

        print(join_phrase.join(out))
