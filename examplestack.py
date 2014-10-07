"""  Example stack
"""
from troposphere.constants import QUAD_ZERO
from CloudformationBase.constants import REGION_AZ_MAP
from CloudformationBase.BaseEC2 import BaseEC2
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
        # Create a parameter for allowing SSH access
        self.par_ssh_ip = \
            BaseVPC.par_cidrblock('SSHaccessIP',
                                  'An IP allowed to SSH to the instance',
                                  '127.0.0.1/32')
        # Create a parameter for specifying the type of instance to launch
        self.par_instance_type = \
            self.par_custom('InstanceType',
                            'String',
                            't2.micro',
                            'The Instance type')
        # Create a parameter for specifying the instance ami id to launch
        self.par_instance_ami = \
            self.par_custom('InstanceAMI',
                            'String',
                            'ami-2c90315b',
                            'The ami id to launch the instance as')
        # Create a parameter for specifying the KeyPair Name to launch instances
        self.par_keyname = \
            self.par_custom('KeyName',
                            'String',
                            'example_key',
                            'The name of the KeyPair to launch the instance')

        # Create a VPC using the BaseVPC class
        self.res_stackvpc = \
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
                               Ref(self.res_stackvpc),
                               self.projectname, self.environmentname
                               )
        self.res_subnetb = \
            BaseVPC.res_subnet('PublicSubnetB', 'PublicB',
                               FindInMap(REGION_AZ_MAP,
                                         Ref(AWS_REGION), 'B'),
                               Ref(self.par_subnetb_cidrblock),
                               Ref(self.res_stackvpc),
                               self.projectname, self.environmentname
                               )

        # Create an Internet Gateway and VPC Gateway attachment
        self.res_igw = \
            BaseVPC.res_internet_gateway('InternetGateway')
        self.res_vpcgatewayattachment = \
            BaseVPC.res_vpc_gateway_attachment('VPCGatewayAttachment',
                                               Ref(self.res_igw),
                                               Ref(self.res_stackvpc))

        # Create a RouteTable and add some basic routes
        self.res_routetbl = \
            BaseVPC.res_route_table('RouteTable',
                                    Ref(self.res_stackvpc),
                                    self.projectname, self.environmentname,
                                    'Main')
        self.res_routeout = \
            BaseVPC.res_route('Route',
                              QUAD_ZERO,
                              Ref(self.res_igw),
                              Ref(self.res_routetbl),
                              self.res_vpcgatewayattachment.title)
        self.res_subrouteassoca = \
            BaseVPC.res_subnet_routetable_association('SubRouteAssocA',
                                                      Ref(self.res_routetbl),
                                                      Ref(self.res_subneta))
        self.res_subrouteassocb = \
            BaseVPC.res_subnet_routetable_association('SubRouteAssocB',
                                                      Ref(self.res_routetbl),
                                                      Ref(self.res_subnetb))

        # Create NetworkACLs
        self.res_nacl = \
            BaseVPC.res_networkacl('NetworkACL',
                                   Ref(self.res_stackvpc),
                                   self.projectname, self.environmentname,
                                   'Main')
        self.res_naclentryout = \
            BaseVPC.res_networkaclentry('OutboundNaclEntry',
                                        QUAD_ZERO,
                                        True,
                                        Ref(self.res_nacl),
                                        BaseVPC.portrange(-1, -1),
                                        -1,
                                        'allow',
                                        100)
        self.res_naclentryin = \
            BaseVPC.res_networkaclentry('InboundNaclEntry',
                                        QUAD_ZERO,
                                        False,
                                        Ref(self.res_nacl),
                                        BaseVPC.portrange(-1, -1),
                                        -1,
                                        'allow',
                                        100)
        self.res_naclassoca = \
            BaseVPC.res_subnet_networkacl_association('NaclAssocA',
                                                      Ref(self.res_nacl),
                                                      Ref(self.res_subneta))
        self.res_naclassocb = \
            BaseVPC.res_subnet_networkacl_association('NaclAssocB',
                                                      Ref(self.res_nacl),
                                                      Ref(self.res_subnetb))

        # Create SecurityGroups
        self.res_mainsg = \
            BaseEC2.res_security_group(
                'MainSecurityGroup',
                [BaseEC2.res_cidr_security_group_rule_out(-1, -1, '-1',
                                                          QUAD_ZERO)],
                [BaseEC2.res_cidr_security_group_rule_in(22, 22, '6',
                                                         Ref(self.par_ssh_ip))],
                self.projectname, self.environmentname, 'Main',
                Ref(self.res_stackvpc),
                'The Main Security Group'
            )

        # Create an Instance
        self.res_instance = \
            BaseEC2.res_instance(
                'DemoInstance',
                Ref(self.par_instance_ami),
                Ref(self.par_instance_type),
                Ref(self.par_keyname),
                [BaseEC2.res_networkinterfaceproperty(True, '0',
                                                      [Ref(self.res_mainsg)],
                                                      Ref(self.res_subneta)
                                                      )],
                self.projectname, self.environmentname, 'Demo'
            )

    def populate_template(self):
        self.parameters.append(self.par_projname)
        self.parameters.append(self.par_envname)
        self.parameters.append(self.par_vpc_cidrblock)
        self.parameters.append(self.par_examplevpc_cidrblock)
        self.parameters.append(self.par_subneta_cidrblock)
        self.parameters.append(self.par_subnetb_cidrblock)
        self.parameters.append(self.par_ssh_ip)
        self.parameters.append(self.par_instance_ami)
        self.parameters.append(self.par_instance_type)
        self.parameters.append(self.par_keyname)

        self.resources.append(self.res_stackvpc)
        self.resources.append(self.res_overridden_vpc)

        self.resources.append(self.res_subneta)
        self.resources.append(self.res_subnetb)

        self.resources.append(self.res_igw)
        self.resources.append(self.res_vpcgatewayattachment)

        self.resources.append(self.res_routetbl)
        self.resources.append(self.res_routeout)
        self.resources.append(self.res_subrouteassoca)
        self.resources.append(self.res_subrouteassocb)

        self.resources.append(self.res_nacl)
        self.resources.append(self.res_naclentryin)
        self.resources.append(self.res_naclentryout)
        self.resources.append(self.res_naclassoca)
        self.resources.append(self.res_naclassocb)

        self.resources.append(self.res_mainsg)

        self.resources.append(self.res_instance)


def main():
    thestack = ExampleStack()
    thestack.populate_template()
    thestack.output_template()

if __name__ == "__main__":
    main()