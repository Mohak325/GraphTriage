"""
Wires API Gateway u1257f2grb to Lambda function telecom-rca-ml-inference-dev.
"""

import boto3

apigw = boto3.client('apigatewayv2', region_name='us-east-1')
l = boto3.client('lambda', region_name='us-east-1')

api_id = 'u1257f2grb'
fn_name = 'telecom-rca-ml-inference-dev'
fn_arn = f'arn:aws:lambda:us-east-1:397669520479:function:{fn_name}'

# 1. Create Integration
try:
    integration = apigw.create_integration(
        ApiId=api_id,
        IntegrationType='AWS_PROXY',
        IntegrationUri=fn_arn,
        IntegrationMethod='POST',
        PayloadFormatVersion='2.0',
        Description='Integration for Carrier-Grade Serverless RCA Inference'
    )
    integration_id = integration['IntegrationId']
    print(f'Created API Gateway Integration: {integration_id}')
except Exception as e:
    print('Integration error:', e)
    # Check existing integrations
    integrations = apigw.get_integrations(ApiId=api_id)['Items']
    integration_id = integrations[0]['IntegrationId']
    print(f'Using existing integration: {integration_id}')

# 2. Create Routes
routes_to_add = [
    'POST /api/v1/rca/analyze',
    'POST /api/v1/incident',
    'GET /api/v1/health'
]

for route_key in routes_to_add:
    try:
        route = apigw.create_route(
            ApiId=api_id,
            RouteKey=route_key,
            Target=f'integrations/{integration_id}'
        )
        print(f'Created Route: {route_key} -> {route["RouteId"]}')
    except Exception as e:
        print(f'Route {route_key} error:', e)

# 3. Grant API Gateway permission to invoke Lambda
try:
    l.add_permission(
        FunctionName=fn_name,
        StatementId='ApiGatewayInvokePermission',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:397669520479:{api_id}/*/*'
    )
    print('Granted API Gateway permission to invoke Lambda.')
except Exception as e:
    print('Lambda permission:', e)

# 4. Check deployment / stages
stages = apigw.get_stages(ApiId=api_id)['Items']
if not stages:
    stage = apigw.create_stage(
        ApiId=api_id,
        StageName='$default',
        AutoDeploy=True,
        Description='Default Auto-Deploy Stage'
    )
    print('Created Stage: $default')
else:
    print('Stages:', [s['StageName'] for s in stages])

