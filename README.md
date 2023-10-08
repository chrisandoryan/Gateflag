# Gateflag for CTF A&D
**Gateflag** (practically read as *getflag*) is an IaaC-enabled project that allows easy deployment of Attack & Defense CTF instances with **user/root flag** obtained from IAM-controlled API endpoints. 

This allows for a subtle tick implementation: easily rotates user/root flag between ticks. 

## Cloud Environments
Currently built for AWS environment with CloudFormation stack.
The stack consists of:
- AWS API Gateway (REST)
- AWS EC2
- AWS IAM & Managed Policies
- VPC, Subnet & Routing, and other networking configurations.

## How It Works
Instead of directly update the value of the user/root flag inside the CTF instance on every ticks, **Gateflag** sets up two specific API endpoints that the players can call to get their user/root flag. These endpoints are protected with IAM and ACL policies, so the endpoint that emits **root flag** can only be called by the **root user**, and endpoint that emits **user flag** can only be called by the **normal user**.

### POV: CTF Administrator
As the administrator, TBA.

### POV: CTF Participants
As a participant, after *pwning* your way into the machine, you just have to execute `/usr/local/bin/takeflag` binary. You'll get the flag depending on what user you're currently on: if you're **root**, you'll get the **root flag**, and vice versa.

## Future Improvements
- Implements Access Key / Secret Key rotation with CloudWatch and Lambda function.
- 