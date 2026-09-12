import lief

class resourcecopy:

    def __init__(self, arguments: dict) -> None:
        if 'inputfile' in arguments:
            self.inputfile = arguments['inputfile']
        else:
            print('Inputfile required')
            exit(0)

    def apply(self, outfile: str) -> None:
        source_binary = lief.PE.parse(self.inputfile)
        target_binary = lief.PE.parse(outfile)

        target_binary.set_resources(source_binary.resources)
        target_binary.write(outfile)