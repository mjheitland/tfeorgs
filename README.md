# tfeorgs

Terraform templates to deal with TF Organizations

## Lambda functions
+ list_tfe_org
+ create_tfe_org
+ delete_tfe_org

## TF API calls 
[TF Cloud API - Organizations](https://www.terraform.io/docs/cloud/api/organizations.html)
Generate a TFE API token under "User Settings/Token" and assign it to "TOKEN".
Set environment variables in TFE for
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY (tick 'sensitive')
- AWS_DEFAULT_REGION

### List all organisations
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request GET \
  https://app.terraform.io/api/v2/organizations
```

### Get organization's meta data
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request GET \
  https://app.terraform.io/api/v2/organizations/mjhorg1
```

### Create organization
```
create-org-payload.json:
{
  "data": {
    "type": "organizations",
    "attributes": {
      "name": "mjhorg2",
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
### Delete organization
```
curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request DELETE \
  https://app.terraform.io/api/v2/organizations/mjhorg1
```