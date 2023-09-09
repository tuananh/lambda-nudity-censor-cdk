import aws_cdk as core
import aws_cdk.assertions as assertions

from lambda_nudity_censor_cdk.lambda_nudity_censor_cdk_stack import LambdaNudityCensorCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in lambda_nudity_censor_cdk/lambda_nudity_censor_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LambdaNudityCensorCdkStack(app, "lambda-nudity-censor-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
