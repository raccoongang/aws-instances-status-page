"""
Scheduler`s helpers, oriented on calculating AWS`s using cost.
"""

from calendar import monthrange
import datetime


def volume_cost(volume_type, size, iops=None):
    """
    Method calculate cost of volume by type and size.

    Arguments:
        volume_type (str): Instance`s volume type.
        size (int): Instance`s volume size.
        iops (int): Instance`s volume iops count (look below at reference).

    Reference:
        https://aws.amazon.com/ebs/pricing

    Return:
        Float value, that equals total instance`s volume cost in dollars ($).
    """
    coefficients = {'gp2': 0.10, 'st1': 0.045, 'sc1': 0.025}

    if volume_type in ('gp2', 'st1', 'sc1'):
        return coefficients[volume_type] * size * 1024 * 12 / (24 * 30)

    if volume_type == 'io1':
        return 0.10 * iops * 1000 * 30 / 30


def total_month_cost(volumes_total, ec2_by_hour):
    """
    Method calculate total cost of volumes and EC-2 instance for current month.

    Arguments:
        volumes_total (float): Amount of all volumes cost by instance.
        ec2_by_hour (float): Instance`s cost by one hour.

    Return:
        Float value, that equals month total instance`s cost in dollars ($).
    """
    volume_cost_by_day = volumes_total / 30
    instance_cost_by_day = ec2_by_hour * 24
    now = datetime.datetime.now()

    days_in_month = monthrange(now.year, now.month)
    days_have_passed = days_in_month[1] - (days_in_month[1] - now.day)
    month_cost = days_have_passed * (instance_cost_by_day + volume_cost_by_day)

    return round(month_cost, 2)


def overall_instance_cost(month_volumes_cost, ec2_by_hour, created_date):
    """
    Method provides multiplication of volumes and EC-2 hours by instance from started date.

    Arguments:
        month_volumes_cost (float): Month volumes count by instance.
        ec2_by_hour (float): Instance`s cost by one hour.
        created_date (datetime): Datetime of instance`s creation.

    Return:
        Float value, that equals overall instance`s cost from started date in dollars ($).
    """
    created_date += datetime.timedelta(hours=2)
    volume_cost_by_hour = month_volumes_cost / 30 / 24
    total_hours = (datetime.datetime.now() - created_date.replace(tzinfo=None)).days * 24
    instance_all_time_cost = total_hours * (volume_cost_by_hour + ec2_by_hour)

    return round(instance_all_time_cost, 2)
