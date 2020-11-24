#---------------
# Data Providers
#---------------

data "aws_region" "current" { }

data "aws_caller_identity" "current" {}

data "archive_file" "create_tfe_org" {
  type        = "zip"
  source_file = "./lambda/create_tfe_org.py"
  output_path = "create_tfe_org.zip"
}


#-------------------
# Locals
#-------------------

variable "region" {
  type = "string"
  description = "AWS region we want to deploy to"  
}

variable "account" {
  type = "string"
  description = "AWS account we want to deploy to"  
}

locals {
  region  = data.aws_region.current.name
  account = data.aws_caller_identity.current.account_id
}


#-------------------
# Roles and Policies
#-------------------

resource "aws_iam_role" "lambda_logging" {
    name = format("%s_lambda_logging", var.project_name)

    tags = { 
      Name = format("%s_lambda_logging", var.project_name)
      project_name = var.project_name
    }

    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy" "lambda_logging" {
    name   = "lambda_logging"
    role   = aws_iam_role.lambda_logging.id
    policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:${local.region}:${local.account}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:${local.region}:${local.account}:log-group:/aws/lambda/log_event:*"
            ]
        }
    ]
}
POLICY
}


#----------------
# Lambda Function
#----------------

resource "aws_lambda_function" "create_tfe_org" {
  filename          = "create_tfe_org.zip"
  function_name     = "create_tfe_org"
  role              = aws_iam_role.create_tfe_org.arn
  handler           = "create_tfe_org.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to create a TFE org."
  source_code_hash  = data.archive_file.create_tfe_org.output_base64sha256
  timeout           = 30

  environment {
    variables = {
      "account_id"  = local.account
      "region"      = local.region
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_create_tfe_org", var.project_name)
    project_name = var.project_name
  }
}
