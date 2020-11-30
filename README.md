# tfeorgs

Terraform templates to automate creation of TFE Organizations and TFE Workspaces

## Lambda functions
+ list_tfe_orgs
+ get_tfe_org
+ create_tfe_org
+ delete_tfe_org
+ full_setup (creates a TFE Organization with a TFE Workspace pointing to source in GitHub)

## Pre-requisites

1. Create PAT in Github (Settings/Developer Settings/Personal Access Token, check 'repo')

2. Generate a TFE API token under "User Settings/Token" and assign it to env variable "TOKEN".

3. Set environment variables in https://app.terraform.io/app/mjhorg1/workspaces/tfeorgs/variables for
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY (tick 'sensitive')
- AWS_DEFAULT_REGION
- TF_VAR_TFE_API_TOKEN (tick 'sensitive')
- TF_VAR_GHE_API_TOKEN (i.e. GHE Personal Access Token, tick 'sensitive')

## TFE API calls 

### TFE Organizations

Test event for full_setup lambda:
```
{
  "org_name": "mjhorg0",
  "user_email": "mjheitland@gmail.com",
  "workspace_name": "dev",
  "repo_name": "mjheitland/tfeorgs"
}
```

#### List all organisations
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request GET \
  https://app.terraform.io/api/v2/organizations
```

#### Get organization's meta data
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request GET \
  https://app.terraform.io/api/v2/organizations/mjhorg1
```

#### Create organization
```
create-org-payload.json:
{
  "data": {
    "type": "organizations",
    "attributes": {
      "name": "mjhorg0",
      "email": "mjheitland@gmail.com"
    }
  }
}

curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @create-org-payload.json \
```
#### Delete organization
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request DELETE \
  https://app.terraform.io/api/v2/organizations/mjhorg1
```

### TFE OAuth Clients (i.e. connection TFE-VCS)

#### Create OAuth Client
```
create-oauth-client-payload.json
{
  "data": {
    "type": "oauth-clients",
    "attributes": {
      "service-provider": "github",
      "http-url": "https://github.com",
      "api-url": "https://api.github.com",
      "oauth-token-string": <GHE Personal Access Token>
    }
  }
}

curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @./create-oauth-client-payload.json \
  https://app.terraform.io/api/v2/organizations/<org_name>/oauth-clients
```

#### Get OAuth Client
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request GET \
  https://app.terraform.io/api/v2/organizations/mjhorg0/oauth-clients
```

### TFE Workspace

#### Create TFE Workspace
```
create-workspace.json:
{
  "data": {
    "attributes": {
      "name": <workspace_name>,
      "terraform_version": "0.13.3",
      "working-directory": "",
      "vcs-repo": {
        "identifier": <Github project, e.g. mjheitland/tfeorgs>,
        "oauth-token-id": <OAuth client token id, e.g. ot-oFVehjRewpmCMY7R>,
        "branch": "",
        "default-branch": true
      }
    },
    "type": "workspaces"
  }
}
```

#### Get workspace
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  https://app.terraform.io/api/v2/organizations/<org_name>/workspaces/<workspace_name>
```

### TFE Workspace Variables

#### Create Workspace Variable
```
variable.json:
{
  "data": {
    "type":"vars",
    "attributes": {
      "key":"some_key",
      "value":"some_value",
      "description":"some description",
      "category":"terraform",
      "hcl":false,
      "sensitive":false
    }
  }
}

curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @pvariable.json \
  https://app.terraform.io/api/v2/workspaces/<workspace_id>/vars
```

#### List Workspace Variables
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
"https://app.terraform.io/api/v2/workspaces/<workspace_id>/vars"
```

## Links
[TFE Cloud API - Organizations](https://www.terraform.io/docs/cloud/api/organizations.html)
