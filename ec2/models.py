from __future__ import unicode_literals
from django.db import models

from datetime import datetime

class Instance(models.Model):
    name = models.CharField(max_length=250)
    instance_id = models.CharField(max_length=250)
    instance_type = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    public_ip_address = models.CharField(max_length=250, null=True)
    private_ip_address = models.CharField(max_length=250, null=True)
    vpc_id = models.CharField(max_length=250)
    security_group = models.CharField(max_length=250)
    volumes = models.CharField(max_length=250)

    ec2_cost_by_hour = models.FloatField(default=0)
    volumes_cost_by_month = models.FloatField(default=0)
    overall_cost_by_month = models.FloatField(default=0)
    overall_cost_all_time = models.FloatField(default=0)

    datetime_of_creation = models.DateTimeField(null=True, blank=True)
    datetime_of_current_ec2_info = models.DateTimeField(default=datetime.now(), null=True, blank=True)

    def __str__(self):
        return self.name
