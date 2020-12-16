from aws_cdk import (
    aws_dynamodb as _dynamodb,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_ssm as _ssm,
    core
)



class DemystifyingStarPermissions(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

        table = _dynamodb.Table(
            self, 'policy',
            partition_key={'name': 'pk', 'type': _dynamodb.AttributeType.STRING},
            sort_key={'name': 'sk', 'type': _dynamodb.AttributeType.STRING},
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute='token',
            removal_policy=core.RemovalPolicy.DESTROY
        )

        table.add_global_secondary_index(
            index_name='action',
            partition_key={'name': 'pk', 'type': _dynamodb.AttributeType.STRING},
            sort_key={'name': 'bk', 'type': _dynamodb.AttributeType.STRING}
        )

        db_param = _ssm.StringParameter(
            self, 'db_param',
            description='magicianCDK-TableName',
            parameter_name='/magicianCDK/TableName',
            string_value=table.table_name,
            tier=_ssm.ParameterTier.STANDARD,
        )

        amazon_role = _iam.Role(self, 'amazon_role', assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))
        amazon_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'))
        amazon_role.add_to_policy(_iam.PolicyStatement(actions=['dynamodb:PutItem'],resources=['*']))

        with open('download.py') as f:
            download_code_body = f.read()
        f.close()

        amazon_lambda = _lambda.Function(
            self, 'amazon_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(download_code_body),
            handler='index.handler',
            role=amazon_role,
            timeout=core.Duration.seconds(900),
            environment=dict(
                DYNAMODB_TABLE=table.table_name
            )
        )

        amazon_logs = _logs.LogGroup(
            self, 'amazon_logs',
            log_group_name='/aws/lambda/'+amazon_lambda.function_name,
            retention=_logs.RetentionDays.ONE_DAY,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        amazon_event = _events.Rule(
            self, 'amazon_event',
            schedule=_events.Schedule.cron(
                minute='0',
                hour='11',
                month='*',
                week_day='*',
                year='*'
            )
        )
        amazon_event.add_target(_targets.LambdaFunction(amazon_lambda))

        action_begins_role = _iam.Role(self, 'action_begins_role', assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))
        action_begins_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'))
        action_begins_role.add_to_policy(_iam.PolicyStatement(actions=['dynamodb:Query'],resources=['*']))

        with open('actionbegins.py') as f:
            action_begins_code_body = f.read()
        f.close()

        action_begins_lambda = _lambda.Function(
            self, 'action_begins_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(action_begins_code_body),
            handler='index.handler',
            role=action_begins_role,
            timeout=core.Duration.seconds(30),
            environment=dict(
                DYNAMODB_TABLE=table.table_name
            )
        )

        action_begins_logs = _logs.LogGroup(
            self, 'action_begins_logs',
            log_group_name='/aws/lambda/'+action_begins_lambda.function_name,
            retention=_logs.RetentionDays.ONE_DAY,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        service_begins_role = _iam.Role(self, 'service_begins_role', assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))
        service_begins_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'))
        service_begins_role.add_to_policy(_iam.PolicyStatement(actions=['dynamodb:Query'],resources=['*']))

        with open('servicebegins.py') as f:
            service_begins_code_body = f.read()
        f.close()

        service_begins_lambda = _lambda.Function(
            self, 'service_begins_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(service_begins_code_body),
            handler='index.handler',
            role=service_begins_role,
            timeout=core.Duration.seconds(30),
            environment=dict(
                DYNAMODB_TABLE=table.table_name
            )
        )

        service_begins_logs = _logs.LogGroup(
            self, 'service_begins_logs',
            log_group_name='/aws/lambda/'+service_begins_lambda.function_name,
            retention=_logs.RetentionDays.ONE_DAY,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        service_list_role = _iam.Role(self, 'service_list_role', assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'))
        service_list_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'))
        service_list_role.add_to_policy(_iam.PolicyStatement(actions=['dynamodb:Query'],resources=['*']))

        with open('servicelist.py') as f:
            service_list_code_body = f.read()
        f.close()

        service_list_lambda = _lambda.Function(
            self, 'service_list_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(service_list_code_body),
            handler='index.handler',
            role=service_list_role,
            timeout=core.Duration.seconds(30),
            environment=dict(
                DYNAMODB_TABLE=table.table_name
            )
        )

        service_list_logs = _logs.LogGroup(
            self, 'service_list_logs',
            log_group_name='/aws/lambda/'+service_list_lambda.function_name,
            retention=_logs.RetentionDays.ONE_DAY,
            removal_policy=core.RemovalPolicy.DESTROY
        )



app = core.App()

DemystifyingStarPermissions(app, 'demystifying-star-permissions')

core.Tags.of(app).add('demystifying-star-permissions', 'demystifying-star-permissions')

app.synth()