#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deployment.deployment_stack import PyISRUFlaskAppDeploymentStack


app = cdk.App()
PyISRUFlaskAppDeploymentStack(
    app, 
    "PyISRUFlaskAppDeploymentStack",
)

app.synth()
