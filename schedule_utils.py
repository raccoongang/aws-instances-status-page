from calendar import monthrange
import datetime


def volume_cost(volume_type, size, iops=None):
    """Volumes price by type - https://aws.amazon.com/ebs/pricing"""
    stable_price = 12 / (24 * 30)

    if volume_type == 'gp2':
        cost = 0.10 * size * 1024 * stable_price
    elif volume_type == 'io1':
        cost = 0.10 * iops * 1000 * 30 / 30
    elif volume_type == 'st1':
        cost = 0.045 * size * 1024 * stable_price
    else:  # 'sc1'
        cost = 0.025 * size * 1024 * stable_price

    return cost


def total_month_cost(volumes_total, ec2_total):
    """Get count of days in month, that have passed with monthrange(count of days in month)
    and subtraction of the remainder. Example, now 23-th, month has 30 days.
    Exit value is: 30 - (30 - 23) => 30 - 7 = 23."""
    volume_cost_by_day = volumes_total / 30
    instance_cost_by_day = ec2_total * 24
    now = datetime.datetime.now()

    days_in_month = monthrange(now.year, now.month)
    days_have_passed = days_in_month[1] - (days_in_month[1] - now.day)
    month_cost = days_have_passed * (instance_cost_by_day + volume_cost_by_day)

    return round(month_cost, 2)


def overall_instance_cost(volumes_total, ec2_by_hour, created_date):
    """Get count of all used hours by instance and then multiplication with price."""
    created_date += datetime.timedelta(hours=2)
    volume_cost_by_hour = volumes_total / 30 / 24
    total_hours = (datetime.datetime.now() - created_date.replace(tzinfo=None)).days * 24
    instance_all_time_cost = total_hours * (volume_cost_by_hour + ec2_by_hour)

    return round(instance_all_time_cost, 2)
