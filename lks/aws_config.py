import os

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION_NAME = 'ap-southeast-1'

ENVIRONMENT_NAME = 'GateflagLKS'
GLOBAL_TEMPLATE_FILE = 'global.yaml'

GLOBAL_TEMPLATE_PARAMETERS = {
    'EnvironmentName': ENVIRONMENT_NAME,
    'FlagServerHost': os.getenv('FLAG_SERVER_HOST', 'https://flaggy.free.beeceptor.com'),
}