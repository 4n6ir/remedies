from aws_cdk import (
    core,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_ssm as _ssm,
)


class DeleteAllDefaultVPCs(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

        role = _iam.Role(
            self, 'role', 
            assumed_by=_iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )
        
        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )
        
        role.add_to_policy(
            _iam.PolicyStatement(
                actions=[
                    'ec2:DescribeRegions',
                    'ec2:DescribeVpcs',
                    'ec2:DeleteVpc',
                    'ec2:DescribeInternetGateways',
                    'ec2:DetachInternetGateway',
                    'ec2:DeleteInternetGateway',
                    'ec2:DescribeSubnets',
                    'ec2:DeleteSubnet',
                    'events:DisableRule',
                    'ssm:GetParameter'
                ],
                resources=['*']
            )
        )

        with open('remedy.py') as f:
            code_body = f.read()
        f.close()

        compute = _lambda.Function(
            self, 'compute',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(code_body),
            handler='index.handler',
            role=role,
            timeout=core.Duration.seconds(60),
            environment=dict(
                RULE='delete-all-default-vpcs'
            ),
        )
        
        logs = _logs.LogGroup(
            self, 'logs',
            log_group_name='/aws/lambda/'+compute.function_name,
            retention=_logs.RetentionDays.ONE_DAY,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        rule = _events.Rule(
            self, 'rule',
            schedule=_events.Schedule.cron(
                minute='*',
                hour='*',
                month='*',
                week_day='*',
                year='*'
            )
        )
        rule.add_target(_targets.LambdaFunction(compute))

        parameter = _ssm.StringParameter(
            self, 'parameter',
            description='Delete All Default VPCs Remedy',
            parameter_name='delete-all-default-vpcs',
            string_value=rule.rule_name,
            tier=_ssm.ParameterTier.STANDARD
        )


app = core.App()

DeleteAllDefaultVPCs(app, 'delete-all-default-vpcs')

core.Tags.of(app).add('delete-all-default-vpcs', 'delete-all-default-vpcs')

app.synth()