# tfeorgs

Terraform templates to deal with TF Organizations

## TF API calls 
[TF Cloud API - Organizations](https://www.terraform.io/docs/cloud/api/organizations.html)

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