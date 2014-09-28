"""  Example stack
"""
from CloudformationBase.BaseVPC import BaseVPC
from CloudformationBase.stack import Stack


class ExampleStack(Stack):
    """ Example Stack class
    """

    def __init__(self):
        super(ExampleStack, self).__init__('Example', 'Dev')

    def populate_template(self):
        examplevpc = BaseVPC(self.projectname, self.environmentname)
        for resource in examplevpc.resources:
            self.template.add_resource(resource)

    def output_template(self):
        super(ExampleStack, self).output_template()


def main():
    thestack = ExampleStack()
    thestack.populate_template()
    thestack.output_template()

if __name__ == "__main__":
    main()