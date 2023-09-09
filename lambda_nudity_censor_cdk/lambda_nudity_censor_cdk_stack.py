from aws_cdk import (
    Duration,
    Fn,
    Stack,
    aws_lambda as lambda_,
    aws_events as eventbridge,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct

class LambdaNudityCensorCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket = s3.CfnBucket(
            scope=self,
            id="NudityCensorBucket",
            notification_configuration=s3.CfnBucket.NotificationConfigurationProperty(
                event_bridge_configuration=s3.CfnBucket.EventBridgeConfigurationProperty(
                    event_bridge_enabled=True
                )
            ),
        )

        censoring_fn = lambda_.DockerImageFunction(
            scope=self,
            id="Nudity_Censoring_Function",
            code=lambda_.DockerImageCode.from_image_asset("src"),
            environment={
                "BUCKET": s3_bucket.ref,
            },
            memory_size=4096,
            timeout=Duration.minutes(2),
        )

        # setup permissions required
        censoring_fn.role.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:*Object*",
                ],
                resources=[Fn.join("", [s3_bucket.attr_arn, "/*"])],
            )
        )

        censoring_fn_l1: lambda_.CfnFunction = (
            censoring_fn.node.default_child
        )
        censoring_fn_l1.add_property_override(
            property_path="EphemeralStorage", value={"Size": 1024}
        )

        # triggering rule
        eventbridge.Rule(
            self,
            "PutObjectRule",
            event_pattern=eventbridge.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"object": {"key": [{"prefix": "raw/"}]}},
            ),
        ).add_target(targets.LambdaFunction(censoring_fn))
