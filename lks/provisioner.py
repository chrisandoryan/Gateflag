import boto3
import aws_config

session = boto3.Session(
    aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
    region_name=aws_config.AWS_REGION_NAME,
)

cf_client = session.client('cloudformation')

# enum
GLOBAL = 0
TEAM = 1
stack_suffixes = {
    GLOBAL: 'global',
    TEAM: 'team',
}

def get_stack_name(stack_type, suffix=''):
    if suffix != '':
        return '%s-%s-%s' % (aws_config.ENVIRONMENT_NAME, stack_suffixes[stack_type], suffix)
    return '%s-%s' % (aws_config.ENVIRONMENT_NAME, stack_suffixes[stack_type])

def deploy(stack_name, template_body, params):
    parameters = [{'ParameterKey': x, 'ParameterValue': params[x]} for x in params.keys()]

    print('Deploying stack %s' % stack_name)

    stack_exists = False
    try:
        cf_client.describe_stacks(StackName=stack_name)
        stack_exists = True
    except cf_client.exceptions.ClientError as e:
        stack_exists = False
    
    try:
        if stack_exists:
            print('Stack exists, updating...')
            response = cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_AUTO_EXPAND', 'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                Parameters=parameters,
            )
            
            print('Waiting until stack %s deployed...' % stack_name)
            cf_client.get_waiter('stack_update_complete').wait(StackName=stack_name)
            
            stack_info = cf_client.describe_stacks(StackName=stack_name)
            if stack_info['Stacks'][0]['StackStatus'] == 'UPDATE_COMPLETE':
                print(f'Stack {stack_name} updated successfully!')
                return stack_info['Stacks'][0]['Outputs']
            else:
                print(f'Stack update failed. Status: {stack_info["Stacks"][0]["StackStatus"]}')
        else:
            print('Stack not exists, creating...')
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_AUTO_EXPAND', 'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                Parameters=parameters,
            )

            print('Waiting until stack %s deployed...' % stack_name)
            cf_client.get_waiter('stack_create_complete').wait(StackName=stack_name)
            
            stack_info = cf_client.describe_stacks(StackName=stack_name)
            if stack_info['Stacks'][0]['StackStatus'] == 'CREATE_COMPLETE':
                print(f'Stack {stack_name} created successfully!')
                return stack_info['Stacks'][0]['Outputs']
            else:
                print(f'Stack creation failed. Status: {stack_info["Stacks"][0]["StackStatus"]}')
                return None
    except Exception as e:
        print(f'Stack creation failed. Status: %s' % e)
        return None

def delete_stack(stack_name):
    try:
        cf_client.delete_stack(StackName=stack_name)
        print(f'Stack {stack_name} deletion initiated.')
    except cf_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Stack {stack_name} does not exist.')
        return

    print('Waiting until stack %s deleted...' % stack_name)
    cf_client.get_waiter('stack_delete_complete').wait(StackName=stack_name)

    try:
        stack_info = cf_client.describe_stacks(StackName=stack_name)
        if stack_info['Stacks'][0]['StackStatus'] == 'DELETE_COMPLETE':
            print(f'Stack {stack_name} deleted successfully!')
        else:
            print(f'Stack deletion failed. Status: {stack_info["Stacks"][0]["StackStatus"]}')
    except cf_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Stack {stack_name} deleted successfully!')
        else:
            print('Stack deletion failed.')


if __name__ == '__main__':
    DEPLOY = 1 # change this

    if DEPLOY:
        f = open(aws_config.GLOBAL_TEMPLATE_FILE)
        template = f.read()
        f.close()

        template = template.replace('__GATEFLAG__', aws_config.ENVIRONMENT_NAME)

        outputs = deploy(get_stack_name(GLOBAL), template, aws_config.GLOBAL_TEMPLATE_PARAMETERS)
        print(outputs)
        print()

        team_parameters = aws_config.TEAM_TEMPLATE_PARAMETERS

        for output in outputs:
            team_parameters[output['OutputKey']] = output['OutputValue']

        for team in aws_config.TEAMS:
            f = open(aws_config.TEAM_TEMPLATE_FILE)
            template = f.read()
            f.close()
            template = template.replace('__GATEFLAG__', aws_config.ENVIRONMENT_NAME)
            template = template.replace('__TEAM__', team)
            outputs = deploy(get_stack_name(TEAM, team), template, team_parameters)
            print(outputs)
            print()
    else:
        for team in aws_config.TEAMS:
            delete_stack(get_stack_name(TEAM, team))
        delete_stack(get_stack_name(GLOBAL))