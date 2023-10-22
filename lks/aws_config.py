import os

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION_NAME = 'ap-southeast-1'

ENVIRONMENT_NAME = 'GateflagLKS'
GLOBAL_TEMPLATE_FILE = 'global.yaml'
TEAM_TEMPLATE_FILE = 'team.yaml'

GLOBAL_TEMPLATE_PARAMETERS = {
    'EnvironmentName': ENVIRONMENT_NAME,
    'FlagServerHost': os.getenv('FLAG_SERVER_HOST', 'https://flaggy.free.beeceptor.com'),
}

TEAM_TEMPLATE_PARAMETERS = {
    'EnvironmentName': ENVIRONMENT_NAME,
    'CTFMachineAMI1': 'ami-0015ec7d1ef8504ee',
    'CTFMachineAMI2': 'ami-0a1e7a1a9eaf0fdba',
    'CTFEC2KeyPair': 'test-infra-lks',
}

TEAMS = [
    {
        'name': 'Team01',
        'ip': '10.0.1.101',
    },
    {
        'name': 'Team02',
        'ip': '10.0.1.102',
    },
]