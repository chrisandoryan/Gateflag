import boto3
import aws_config

session = boto3.Session(
    aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
    region_name=aws_config.AWS_REGION_NAME,
)
ssm_client = session.client('ssm')

def ssm_check_flag_exists(instance_id, user):
    response = ssm_client.start_session(
        Target=instance_id
    )

    command = 'sudo runuser -l %s -c \'eval "$(cat ~/.bashrc)"; takeflag\'' % user
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]},
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
    if 'LKS{' in output['StandardOutputContent']:
        return True
    return False

def ssm_check_code_unchanged(instance_id, path, part):
    response = ssm_client.start_session(
        Target=instance_id
    )

    command = 'sudo runuser -l root -c \'eval "$(cat ~/.bashrc)"; sudo cat %s\'' % (path)
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]},
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

    if part in output['StandardOutputContent']:
        return True
    return False

if __name__ == '__main__':
    instance_id = 'i-0eaf0251e98c95c38'
    ssm_check_flag_exists(instance_id, 'root')
    ssm_check_flag_exists(instance_id, 'ubuntu')

    print(ssm_check_code_unchanged(instance_id, '/usr/local/bin/takeflag', '''r = requests.get(url, headers=signing_headers(METHOD, url, body))
    print(r.content.decode("utf-8"))'''))