from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    Duration,
)
import aws_cdk as cdk
from constructs import Construct


class PyISRUFlaskAppDeploymentStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Parameters for your domain and instance
        instance_key_name = "pyISRUFlaskApp"

        # Look up the existing hosted zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id="Z051372722QIZEIL0YS1U",
            zone_name="mathewkirby.com",
        )

        # Define the VPC and Security Group
        vpc = ec2.Vpc(
            self,
            "PyISRUVPC",
            max_azs=2,
            nat_gateways=0,  # No NAT gateways, so no additional Elastic IPs
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                )
            ],
        )

        security_group = ec2.SecurityGroup(
            self,
            "InstanceSecurityGroup",
            vpc=vpc,
            description="Allow SSH and HTTP",
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH"
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP"
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS"
        )

        # Define the EC2 instance
        ami = "ami-0866a3c8686eaeeba"
        instance = ec2.Instance(
            self,
            "FlaskAppInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.generic_linux(ami_map={"us-east-1": ami}),
            vpc=vpc,
            key_name=instance_key_name,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )                         

        instance.user_data.add_commands(
            # Update and upgrade packages
            "sudo apt update -y",
            "sudo apt upgrade -y",
            "sudo apt install -y git nginx python3-pip python3-venv",
            # Clone the GitHub repository
            "cd /home/ubuntu",
            "git clone https://github.com/mkirby42/pyisru.git",
            "cd pyisru",
            # Run the setup script
            "sudo chmod +x deploy/setup.sh",
            "sudo ./deploy/setup.sh",
            # Copy the systemd service and Nginx configuration files
            "sudo chmod o+x /home/ubuntu",
            "sudo cp deploy/pyisru.service /etc/systemd/system/pyisru.service",
            "sudo cp deploy/pyisru_nginx.conf /etc/nginx/sites-available/pyisru",
            "sudo ln -s /etc/nginx/sites-available/pyisru /etc/nginx/sites-enabled",
            "sudo rm -f /etc/nginx/sites-enabled/default",
            # Set permissions
            "sudo chown -R ubuntu:www-data /home/ubuntu/pyisru",
            "sudo chmod -R 755 /home/ubuntu/pyisru",
            # Start and enable Gunicorn service
            "sudo systemctl daemon-reload",
            "sudo systemctl start pyisru",
            "sudo systemctl enable pyisru",
            # Test Nginx configuration and restart service
            "sudo nginx -t",
            "sudo systemctl restart nginx",
        )

        # certificate = acm.Certificate(
        #     self, "SiteCertificate",
        #     domain_name=domain_name,
        #     validation=acm.CertificateValidation.from_dns(hosted_zone)
        # )

        # Add A record in Route 53 to point to the EC2 instance
        route53.ARecord(
            self,
            "SiteARecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_ip_addresses(instance.instance_public_ip),
            ttl=Duration.minutes(5),
        )

        # Attach SSL certificate to the Nginx config (you may need to SSH to make final adjustments)
