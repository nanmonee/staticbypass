

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
            if flag.name in arguments:
                if flag.choices:
                    if arguments[flag.name] not in flag.choices:
                        print(f'Invalid Argument: {arguments[flag.name]} not in {flag.choices}')
                        self.print_help()
                    if type(flag.choices) == dict:
                        parsed[flag.name] = flag.choices[arguments[flag.name]]
                    else:
                        parsed[flag.name] = arguments[flag.name]
                else:
                    parsed[flag.name] = arguments[flag.name]
            else:
                if type(flag.choices) == dict:
                    parsed[flag.name] = flag.choices[flag.default]
                else:
                    parsed[flag.name] = flag.default
        """
        while i < len(argv):
            if argv[i] in ['help', 'h']:
                self.print_help()
            for flag in self.flags:
                if argv[i] == flag.name:
                    if flag.choices != {}:
                        if argv[i+1] not in flag.choices:
                            self.print_help()
                        else:
                            parsed[flag.name] = argv[i+1]
                            i += 1
                            break
                    else:
                        parsed[flag.name] = argv[i+1]
                        i += 1
                        break
            i += 1
        return parsed
        """
        return parsed

    def print_help(self):
        print(f'{self.modulename} options: ')
        for flag in self.flags:
            if flag.choices != {}:
                print(f'  {flag.name}={flag.choices} {flag.help}')
            else:
                print(f'  {flag.name} {flag.help}')
        exit(0)