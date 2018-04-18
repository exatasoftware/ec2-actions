import logging
import os
import sys
import boto3

LOGGER = logging.getLogger()
for h in LOGGER.handlers:
    LOGGER.removeHandler(h)

HANDLER = logging.StreamHandler(sys.stdout)
FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
HANDLER.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

INSTANCE_ID = os.environ['INSTANCE_ID']

EC2 = boto3.resource('ec2')
EC2INSTANCE = EC2.Instance(INSTANCE_ID)
EC2CLIENT = EC2.meta.client

def ec2start():
    """
    EC2 instance start.
    """
    response = EC2CLIENT.describe_instance_status(InstanceIds=[INSTANCE_ID], IncludeAllInstances=True)
    instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Status']
    system_status = response['InstanceStatuses'][0]['SystemStatus']['Status']

    if EC2INSTANCE.state['Name'] == 'running' and instance_status == 'ok' and system_status == 'ok':
        LOGGER.info('Aborts. Istance is running.')
        return
    elif EC2INSTANCE.state['Name'] == 'stopped':
        EC2INSTANCE.start()
        LOGGER.info('Start InstanceID: ' + INSTANCE_ID)
        EC2CLIENT.get_waiter('instance_running').wait(
            InstanceIds=[
                INSTANCE_ID
            ],
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 30
            }
        )
        LOGGER.info("Completed!")
        return
    else:
        LOGGER.info('Not started InstanceID: ' + INSTANCE_ID)

def ec2stop():
    """
    EC2 instance stop
    """
    response = EC2CLIENT.describe_instance_status(InstanceIds=[INSTANCE_ID])
    instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Status']
    system_status = response['InstanceStatuses'][0]['SystemStatus']['Status']

    if instance_status == 'initializing' or system_status == 'initializing':
        LOGGER.info('Aborts. Currently InstanceStatus Checking')
        return
    elif EC2INSTANCE.state['Name'] == 'running' and instance_status == 'ok' and system_status == 'ok':
        EC2INSTANCE.stop()
        LOGGER.info('Stop InstanceID： ' + INSTANCE_ID)
        EC2CLIENT.get_waiter('instance_stopped').wait(
            InstanceIds=[
                INSTANCE_ID
            ],
            WaiterConfig={
                'Delay': 5,  # Default: 15
                'MaxAttempts': 30  # Default: 40
            }
        )
        LOGGER.info("Completed!")
        return
    else:
        LOGGER.info('Not Running InstanceID： ' + INSTANCE_ID)

def start(event, context):
    """
    start function
    """
    try:
        ec2start()
    except Exception as error:
        LOGGER.exception(error)

def stop(event, context):
    """
    stop function
    """
    try:
        ec2stop()
    except Exception as error:
        LOGGER.exception(error)

