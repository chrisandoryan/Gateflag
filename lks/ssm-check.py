import boto3
import aws_config
import string
import random

session = boto3.Session(
    aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
    region_name=aws_config.AWS_REGION_NAME,
)
ssm_client = session.client('ssm')

def ssm_check_flag_exists(instance_id, users):
    response = ssm_client.start_session(
        Target=instance_id
    )

    separator = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    commands = []
    for user in users:
        commands.append('sudo runuser -l %s -c \'eval "$(cat ~/.bashrc)"; takeflag; echo -n %s\'' % (user, separator))
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': commands},
    )

    command_id = response['Command']['CommandId']
    ssm_client.get_waiter('command_executed').wait(
        InstanceId=instance_id,
        CommandId=command_id
    )

    output = ssm_client.get_command_invocation(
        InstanceId=instance_id,
        CommandId=command_id
    )
    #print(output)

    flags = output['StandardOutputContent'].strip().split(separator)[:-1]
    if len(flags) != len(users):
        return False
    
    for i in range(len(users)):
        if 'LKS{' not in output['StandardOutputContent']:
            return False
    return True

def ssm_check_code_unchanged(instance_id, paths, parts):
    assert len(paths) == len(parts)
    response = ssm_client.start_session(
        Target=instance_id
    )

    separator = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

    commands = []
    for path in paths:
        commands.append('sudo runuser -l root -c \'sudo cat %s\';echo -n %s' % (path, separator))
        
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': commands},
    )

    command_id = response['Command']['CommandId']
    ssm_client.get_waiter('command_executed').wait(
        InstanceId=instance_id,
        CommandId=command_id
    )

    output = ssm_client.get_command_invocation(
        InstanceId=instance_id,
        CommandId=command_id
    )
    #print(output)

    files = output['StandardOutputContent'].strip().split(separator)[:-1]
    if len(files) != len(parts):
        return False

    for i in range(len(parts)):
        if parts[i] not in files[i]:
            return False
    return True

if __name__ == '__main__':
    instance_id = 'i-0eaf0251e98c95c38'
    print(ssm_check_flag_exists(instance_id, ['root', 'ubuntu']))

    print(ssm_check_code_unchanged(instance_id, ['/usr/local/bin/takeflag', '/usr/local/bin/takeflag'], [
    '''r = requests.get(url, headers=signing_headers(METHOD, url, body))\n    print(r.content.decode("utf-8"))''',
    '''if __name__ == "__main__":\n    METHOD = "GET"''',
    ]))