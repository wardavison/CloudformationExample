"""  Example stack
"""
from CloudformationBase.BaseVPC import BaseVPC
from CloudformationBase.stack import Stack
from examplevpc import ExampleVPC
from troposphere import Ref


class ExampleStack(Stack):
    """ Example Stack class
    """

    def __init__(self):
        # Initialise the Stack with a Project name and Environment Name
        super(ExampleStack, self).__init__('Example', 'Dev')

        # Create a parameter for taking the VPC CIDR block
        self.par_vpccidrblock = \
            BaseVPC.par_vpccidrblock('BaseVPCCIDR')
        # Do the same from the ExampleVPC class
        self.par_examplevpccidrblock = \
            ExampleVPC.par_vpccidrblock('ExampleVPCCIDR')

        # Create a VPC using the BaseVPC class
        self.res_vpc = \
            BaseVPC.res_vpc('BaseVPC', Ref(self.par_vpccidrblock), True, True,
                            'default', self.projectname, self.environmentname)
        # Create a VPC using the ExampleVPC class (Which overrides BaseVPC)
        self.res_overriden_vpc = \
            ExampleVPC.res_vpc('ExampleVPC', Ref(self.par_examplevpccidrblock),
                               True, True, 'default', self.projectname,
                               self.environmentname)

    def populate_template(self):
        self.parameters.append(self.par_vpccidrblock)
        self.parameters.append(self.par_examplevpccidrblock)

        self.resources.append(self.res_vpc)
        self.resources.append(self.res_overriden_vpc)


def main():
    thestack = ExampleStack()
    thestack.populate_template()
    thestack.output_template()

if __name__ == "__main__":
    main()