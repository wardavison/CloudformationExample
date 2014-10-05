"""  Example stack
"""
from CloudformationBase.constants import REGION_AZ_MAP
from CloudformationBase.BaseVPC import BaseVPC
from CloudformationBase.stack import Stack
from examplevpc import ExampleVPC
from troposphere import Ref, FindInMap, AWS_REGION


class ExampleStack(Stack):
    """ Example Stack class
    """

    def __init__(self):
        # Create a parameter for specifying the Project Name
        self.par_projname = self.par_custom('ProjectName', 'String', 'Example',
                                   'Name of the Project')

        # Create a parameter for specifying the Environment
        self.par_envname = self.par_custom('EnvironmentName', 'String', 'Dev',
                                  'Name of the Environment, e.g. Dev, Test,'
                                  'UAT, Staging, Prod')

        # Initialise the Stack referencing the Project name and Environment Name
        super(ExampleStack, self).__init__(Ref(self.par_projname),
                                           Ref(self.par_envname))

        # Create a parameter for taking the VPC CIDR block
        self.par_vpc_cidrblock = \
            BaseVPC.par_cidrblock('BaseVPCCIDR',
                                  'The CIDR for the Base VPC',
                                  '10.0.0.0/23')
        # Do the same from the ExampleVPC class
        self.par_examplevpc_cidrblock = \
            ExampleVPC.par_cidrblock('ExampleVPCCIDR',
                                     'The CIDR for the Example VPC',
                                     '172.16.0.0/23')
        # Create a parameter for the Base VPC Subnet A
        self.par_subneta_cidrblock = \
            BaseVPC.par_cidrblock('BaseSubnetA',
                                  'The CIDR for Base Subnet A',
                                  '10.0.0.0/24')
        # Create a parameter for the Base VPC Subnet A
        self.par_subnetb_cidrblock = \
            BaseVPC.par_cidrblock('BaseSubnetB',
                                  'The CIDR for Base Subnet B',
                                  '10.0.1.0/24')

        # Create a VPC using the BaseVPC class
        self.res_vpc = \
            BaseVPC.res_vpc('BaseVPC', Ref(self.par_vpc_cidrblock), True, True,
                            'default', self.projectname, self.environmentname)
        # Create a VPC using the ExampleVPC class (Which overrides BaseVPC)
        self.res_overridden_vpc = \
            ExampleVPC.res_vpc('ExampleVPC', Ref(self.par_examplevpc_cidrblock),
                               True, True, 'default', self.projectname,
                               self.environmentname)

        # Create two subnets, in alternate availability zones.
        self.res_subneta = \
            BaseVPC.res_subnet('PublicSubnetA', 'PublicA',
                               FindInMap(REGION_AZ_MAP,
                                         Ref(AWS_REGION), 'A'),
                               Ref(self.par_subneta_cidrblock),
                               Ref(self.res_vpc),
                               self.projectname, self.environmentname
                               )
        self.res_subnetb = \
            BaseVPC.res_subnet('PublicSubnetB', 'PublicB',
                               FindInMap(REGION_AZ_MAP,
                                         Ref(AWS_REGION), 'B'),
                               Ref(self.par_subnetb_cidrblock),
                               Ref(self.res_vpc),
                               self.projectname, self.environmentname
                               )

    def populate_template(self):
        self.parameters.append(self.par_projname)
        self.parameters.append(self.par_envname)
        self.parameters.append(self.par_vpc_cidrblock)
        self.parameters.append(self.par_examplevpc_cidrblock)
        self.parameters.append(self.par_subneta_cidrblock)
        self.parameters.append(self.par_subnetb_cidrblock)

        self.resources.append(self.res_vpc)
        self.resources.append(self.res_overridden_vpc)

        self.resources.append(self.res_subneta)
        self.resources.append(self.res_subnetb)


def main():
    thestack = ExampleStack()
    thestack.populate_template()
    thestack.output_template()

if __name__ == "__main__":
    main()