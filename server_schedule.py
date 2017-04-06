"""
Scheduler, that updates overall and billing information about own EC2 instances from AWS-account.
"""

import datetime
import json
import os
import re

import boto3
from botocore.exceptions import ClientError
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import django

from schedule_utils import volume_cost, total_month_cost, overall_instance_cost
from ec2.models import Instance as EC2Instance


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webservices.settings")
django.setup()

sched = BlockingScheduler()

AWS_KEY, AWS_SECRET, REGION = os.environ['AWS_KEY'], os.environ['AWS_SECRET'], os.environ['REGION']
PRICE_URL = 'http://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js'


def regions_we_have():
    """
    Method checks corresponding region to each instance.

    Returns:
        own_regions (dict): {'instance.id': 'region', ...}
        instance.id (str): Instance`s id.
        region (str): Instance`s region.
    """
    client = boto3.client('ec2', aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, region_name=REGION)

    all_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    own_regions = {}

    for region in all_regions:
        ec2 = boto3.resource('ec2', aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, region_name=region)
        try:
            own_regions = {instance.id: region for instance in ec2.instances.all()}
        except ClientError:
            pass

    return own_regions


def get_current_ec2_prices(own_regions):
    """
    Method gets current price for list of own EC2`s regions.

    Arguments:
        own_regions (dict): Data as region as value by instance as key.

    Reference:
        http://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js

    Returns:
        regions_prices (dict): Nested dictionary with regions and corresponding type-price counts.
    """
    own_regions_list = list(set([key for key in own_regions.values()]))

    request = requests.get(PRICE_URL).text

    if 'callback(' in request:
        request = request.split('callback(')[1][:-2]

    request = re.sub(r"{\s*(\w)", r'{"\1', request)
    request = re.sub(r",\s*(\w)", r',"\1', request)
    request = re.sub(r"(\w):", r'\1":', request)

    regions_prices = {region: {} for region in own_regions_list}

    aws_regions_data = [region for region in json.loads(request)['config']['regions']]

    regions_by_types = [region['instanceTypes'] for region in aws_regions_data if region['region'] in own_regions_list]

    for region, sizes in zip(own_regions_list, regions_by_types):
        for size in sizes[0]['sizes']:
            regions_prices[region][size['size']] = size['valueColumns'][0]['prices']['USD']

    return regions_prices


def refresh_instances_info():
    """
    Method create overall and billing data for each new AWS`s EC-2 instance and/or update for each instance
    already exists. Also if existing instances are out of date, method deletes them all.

    Fields for instance data are:
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
    regions_by_instance = regions_we_have()

    current_price = get_current_ec2_prices(regions_by_instance)

    ec2 = boto3.resource('ec2', aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, region_name=REGION)

    instances = [instance.id for instance in ec2.instances.all()]

    db_instances = [db_instance.instance_id for db_instance in EC2Instance.objects.all()]

    data_to_delete = list(set(db_instances) - set(instances))

    if data_to_delete:
        for old_instance_id in data_to_delete:
            EC2Instance.objects.get(instance_id=old_instance_id).delete()

    for instance_id in instances:
        instance = ec2.Instance(instance_id)

        month_volumes_cost = 0
        for volume in instance.volumes.all():
            month_volumes_cost += volume_cost(volume.volume_type, volume.size, volume.iops)

        ec2_hour_cost = float(current_price[regions_by_instance[instance_id]][instance.instance_type])

        instance_data = {
            'name': instance.tags[0]['Value'],
            'instance_id': instance_id,
            'instance_type': instance.instance_type,
            'state': instance.state['Name'],
            'public_ip_address': instance.public_ip_address,
            'private_ip_address': instance.private_ip_address,
            'vpc_id': instance.vpc_id,
            'security_group': instance.security_groups[0]['GroupId'],
            'volumes': ', '.join([volume.id for volume in instance.volumes.all()]),
            'ec2_cost_by_hour': ec2_hour_cost,
            'volumes_cost_by_month': round(month_volumes_cost, 2),
            'overall_cost_by_month': total_month_cost(month_volumes_cost, ec2_hour_cost),
            'overall_cost_all_time': overall_instance_cost(month_volumes_cost, ec2_hour_cost, instance.launch_time),
            'datetime_of_creation': (instance.launch_time.replace(tzinfo=None) + datetime.timedelta(hours=2)),
            'datetime_of_current_ec2_info': datetime.datetime.now()
        }

        try:
            ec2_instance = EC2Instance.objects.get(instance_id=instance_id)
            for key, value in instance_data.items():
                setattr(ec2_instance, key, value)
            ec2_instance.save()
        except EC2Instance.DoesNotExist:
            ec2_instance = EC2Instance(**instance_data)
            ec2_instance.save()


sched.add_job(refresh_instances_info, 'interval', minutes=25)
sched.start()
