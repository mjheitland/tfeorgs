#---------------
# Data Providers
#---------------

data "aws_region" "current" { }

data "aws_caller_identity" "current" {}


#-------------------
# Locals and variables
#-------------------

locals {
  region       = data.aws_region.current.name
  account      = data.aws_caller_identity.current.account_id
  project_name = "tfeorgs"
}

variable "TFE_API_TOKEN" { 
  type = string
  description = "TFE API Token is passed from TFE environment variable TF_VAR_TFE_API_TOKEN to allow lambda to access TFE" 
}

variable "GHE_API_TOKEN" { 
  type = string
  description = "GHE API Token is passed from TFE environment variable TF_VAR_GHE_API_TOKEN to allow lambda to access GHE" 
}

#-------------------
# Roles and Policies
#-------------------

resource "aws_iam_role" "lambda_logging" {
    name = format("%s_lambda_logging", local.project_name)

    tags = { 
      Name = format("%s_lambda_logging", local.project_name)
      project_name = local.project_name
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
                "arn:aws:logs:${local.region}:${local.account}:log-group:/aws/lambda/*:*"
            ]
        }
    ]
}
POLICY
}


#--------------
# Lambda Layer
#--------------

data "archive_file" "zip_layer" {
  type        = "zip"
  source_dir  = "./layers"
  output_path = "my_lambda_layer.zip"
}

resource "aws_lambda_layer_version" "my_lambda_layer" {
  filename            = "my_lambda_layer.zip"
  layer_name          = "my_lambda_layer"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.zip_layer.output_base64sha256
}


#----------------
# Lambda Function
#----------------

#--- list_tfe_orgs

data "archive_file" "list_tfe_orgs" {
  type        = "zip"
  source_file = "./lambda/list_tfe_orgs.py"
  output_path = "list_tfe_orgs.zip"
}

resource "aws_lambda_function" "list_tfe_orgs" {
  filename          = "list_tfe_orgs.zip"
  function_name     = "list_tfe_orgs"
  role              = aws_iam_role.lambda_logging.arn
  handler           = "list_tfe_orgs.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to list a TFE org."
  source_code_hash  = data.archive_file.list_tfe_orgs.output_base64sha256
  timeout           = 30
  layers            = [aws_lambda_layer_version.my_lambda_layer.arn]

  environment {
    variables = {
      "account_id"    = local.account
      "region"        = local.region
      "TFE_API_TOKEN" = var.TFE_API_TOKEN
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_list_tfe_orgs", local.project_name)
    project_name = local.project_name
  }
}

#--- get_tfe_org

data "archive_file" "get_tfe_org" {
  type        = "zip"
  source_file = "./lambda/get_tfe_org.py"
  output_path = "get_tfe_org.zip"
}

resource "aws_lambda_function" "get_tfe_org" {
  filename          = "get_tfe_org.zip"
  function_name     = "get_tfe_org"
  role              = aws_iam_role.lambda_logging.arn
  handler           = "get_tfe_org.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to list a TFE org."
  source_code_hash  = data.archive_file.get_tfe_org.output_base64sha256
  timeout           = 30
  layers            = [aws_lambda_layer_version.my_lambda_layer.arn]

  environment {
    variables = {
      "account_id"    = local.account
      "region"        = local.region
      "TFE_API_TOKEN" = var.TFE_API_TOKEN
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_get_tfe_org", local.project_name)
    project_name = local.project_name
  }
}

#--- create_tfe_org

data "archive_file" "create_tfe_org" {
  type        = "zip"
  source_file = "./lambda/create_tfe_org.py"
  output_path = "create_tfe_org.zip"
}

resource "aws_lambda_function" "create_tfe_org" {
  filename          = "create_tfe_org.zip"
  function_name     = "create_tfe_org"
  role              = aws_iam_role.lambda_logging.arn
  handler           = "create_tfe_org.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to create a TFE org."
  source_code_hash  = data.archive_file.create_tfe_org.output_base64sha256
  timeout           = 30
  layers            = [aws_lambda_layer_version.my_lambda_layer.arn]

  environment {
    variables = {
      "account_id"    = local.account
      "region"        = local.region
      "TFE_API_TOKEN" = var.TFE_API_TOKEN
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_create_tfe_org", local.project_name)
    project_name = local.project_name
  }
}

#--- delete_tfe_org

data "archive_file" "delete_tfe_org" {
  type        = "zip"
  source_file = "./lambda/delete_tfe_org.py"
  output_path = "delete_tfe_org.zip"
}

resource "aws_lambda_function" "delete_tfe_org" {
  filename          = "delete_tfe_org.zip"
  function_name     = "delete_tfe_org"
  role              = aws_iam_role.lambda_logging.arn
  handler           = "delete_tfe_org.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to delete a TFE org."
  source_code_hash  = data.archive_file.delete_tfe_org.output_base64sha256
  timeout           = 30
  layers            = [aws_lambda_layer_version.my_lambda_layer.arn]

  environment {
    variables = {
      "account_id"    = local.account
      "region"        = local.region
      "TFE_API_TOKEN" = var.TFE_API_TOKEN
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_delete_tfe_org", local.project_name)
    project_name = local.project_name
  }
}


#--- full_setup: create tfe org if it does not exist, add a workspace, connect it to GitHub, add TFE vars

data "archive_file" "full_setup" {
  type        = "zip"
  source_file = "./lambda/full_setup.py"
  output_path = "full_setup.zip"
}

resource "aws_lambda_function" "full_setup" {
  filename          = "full_setup.zip"
  function_name     = "full_setup"
  role              = aws_iam_role.lambda_logging.arn
  handler           = "full_setup.lambda_handler"
  runtime           = "python3.8"
  description       = "A function to create a TFE org."
  source_code_hash  = data.archive_file.full_setup.output_base64sha256
  timeout           = 30
  layers            = [aws_lambda_layer_version.my_lambda_layer.arn]

  environment {
    variables = {
      "account_id"    = local.account
      "region"        = local.region
      "TFE_API_TOKEN" = var.TFE_API_TOKEN
      "GHE_API_TOKEN" = var.GHE_API_TOKEN
    }
  }

#  vpc_config {
#    subnet_ids         = var.subprv_ids
#    security_group_ids = aws_security_group.sg_log_event.*.id
#  }

  tags = { 
    Name = format("%s_full_setup", local.project_name)
    project_name = local.project_name
  }
}
