

class Flag:
    def __init__(self, name, default, help, choices):
        self.name = name
        self.default = default
        self.help = help
        self.choices = choices

class ArgumentParser:

    def __init__(self, modulename='Module'):
        self.flags = []
        self.modulename = modulename

    def add_argument(self, name='', default='', help='', choices={}):
        self.flags.append(Flag(name, default, help, choices))

    def parse_args(self, arguments):
        parsed = {}
        i = 0

        if 'h' in arguments or 'help' in arguments:
            self.print_help()

        for flag in self.flags:

            value = arguments.get(flag.name, flag.default)

            if flag.choices:
                if flag.name in arguments and value not in flag.choices:
                    print(f'Invalid Argument: \'{arguments[flag.name]}\' not in {set(flag.choices)}')
                    self.print_help()
                if type(flag.choices) == dict:
                    value= flag.choices[value]
            parsed[flag.name] = value

        return parsed

    def print_help(self):
        print(f'{self.modulename} options: ')
        for flag in self.flags:
            if flag.choices != {}:
                print(f'  {flag.name}={set(flag.choices)} {flag.help}')
            else:
                print(f'  {flag.name} {flag.help}')
        exit(0)