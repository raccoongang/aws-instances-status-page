"""
Models for EC-2 Instances.
"""

from django.db import models
from datetime import datetime


class Instance(models.Model):
    """
    This model represents instance from AWS.

    `name` is a name of instance.
    `instance_id` is an id of instance.
    `instance_type` is a type of instance.
    `state` is a state of instance.
    `public_ip_address` is public IP address type of instance.
    `private_ip_address` is private IP address type of instance.
    `vpc_id` is a VPC id of instance.
    `security_group` is a security group of instance.
    `volumes` is a list of volumes, that instance contains.

    `ec2_cost_by_hour` is an EC-2 instance`s cost by hour.
    `volumes_cost_by_month` is an instance`s volumes cost by month.
    `overall_cost_by_month` is a total cost of volumes and EC-2 instance for current month.
    `overall_cost_all_time` is a sum of volumes and EC-2 hours by instance from started date.

    `datetime_of_creation` is a date and time of instance`s creation.
    `datetime_of_current_ec2_info` is a date and time of last instance`s info update.
    """
    name = models.CharField(max_length=250)
    instance_id = models.CharField(max_length=250)
    instance_type = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    public_ip_address = models.CharField(max_length=250, null=True)
    private_ip_address = models.CharField(max_length=250, null=True)
    vpc_id = models.CharField(max_length=250, null=True)
    security_group = models.CharField(max_length=250, null=True)
    volumes = models.CharField(max_length=250, null=True)

    ec2_cost_by_hour = models.FloatField(default=0)
    volumes_cost_by_month = models.FloatField(default=0)
    overall_cost_by_month = models.FloatField(default=0)
    overall_cost_all_time = models.FloatField(default=0)

    datetime_of_creation = models.DateTimeField(null=True, blank=True)
    datetime_of_current_ec2_info = models.DateTimeField(default=datetime.now(), null=True, blank=True)

    def __str__(self):
        """
        String representation of the instance`s name.
        """
        return self.name
