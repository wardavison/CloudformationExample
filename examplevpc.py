""" Example VPC with overrides
"""
from troposphere import Join
from troposphere.ec2 import VPC, Tag
from CloudformationBase.BaseVPC import BaseVPC


class ExampleVPC(BaseVPC):

    def __init__(self):
        super(ExampleVPC, self).__init__()

    @staticmethod
    def res_vpc(title, cidrblock, dnssupport, dnshostnames,
                instancetenancy, projectname, environmentname):
        """
        :param title: Title for the JSON VPC resource (string)
        :param cidrblock: CIDR block for the VPC e.g. 10.0.0.0/16 (string)
        :param dnssupport: The VPC has DNS support (boolean)
        :param dnshostnames: Enable DNS hostnames (boolean)
        :param instancetenancy: default or dedicated instance tenancy (string)
        :param projectname: Name of project (used to form name) (string)
        :param environmentname: Name of environment (used to form name) (string)
        :return: Troposphere VPC resource object
        """
        return VPC(
            title,
            CidrBlock=cidrblock,
            EnableDnsSupport=dnssupport,
            EnableDnsHostnames=dnshostnames,
            InstanceTenancy=instancetenancy,
            Tags=[Tag('Name', Join('', [projectname,
                                        '-',
                                        environmentname,
                                        '-overridenVPC']))]
        )