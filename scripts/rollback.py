from dist.provision import get_stack_name, deploy, TEAM, delete_stack
import aws_config
import boto3
import json

session = boto3.Session(
    aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
    region_name=aws_config.AWS_REGION_NAME,
)

cf_client = session.client('cloudformation')

def rollback(team_name):
    stack_name = get_stack_name(TEAM, team_name)
    
    response = cf_client.describe_stacks(StackName=stack_name)
    stack_parameters = response['Stacks'][0]['Parameters']

    response = cf_client.get_template(StackName=stack_name)
    template_body = response['TemplateBody']
    if template_body['Resources']['CTFMachineEC2Instance']['Properties']['ImageId']['Ref'] == 'CTFMachineAMI1':
        template_body['Resources']['CTFMachineEC2Instance']['Properties']['ImageId']['Ref'] = 'CTFMachineAMI2'
    else:
        template_body['Resources']['CTFMachineEC2Instance']['Properties']['ImageId']['Ref'] = 'CTFMachineAMI1'

    parameters = {x['ParameterKey']: x['ParameterValue'] for x in stack_parameters}
    modified = json.dumps(template_body)

    print('Rollback instance for %s' % team_name)
    delete_stack(stack_name)
    outputs = deploy(stack_name, modified, parameters)
    print(outputs)

if __name__ == '__main__':
    # example
    rollback('Team01')