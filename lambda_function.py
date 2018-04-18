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

def handler(event, context):
    """
    main function
    """
    try:
        ec2start()
    except Exception as error:
        LOGGER.exception(error)

