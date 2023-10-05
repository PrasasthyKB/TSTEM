# Terraform

The resources declared here represents different resources in AWS or credentials required by the services on top of the VM.
For instance, the specification of VMs, security group, route table, VPC, etc.
Terraform does not responsible for deploying/installing the software dependencies/code/configuration inside the VM.
Please refer to [Ansible](../ansible/README.md) section for that.

Some configuration such as VM size, default AMI, and default region are declared in `cluster.tfvars`, albeit some other are spread on where it is used e.g. `root_block_device` on `main.tf`.

The [state about the managed infrastructure](https://www.terraform.io/language/state) is stored on S3 bucket as configured on `backend.tf`.

## Applying a change

Applying a configuration change towards AWS resources can be performed with:
```sh
terraform apply -var-file=cluster.tfvars
```

where Terraform will read required configuration from `cluster.tfvars`.
User will be asked to confirm the planned change by typing `yes`.

If the user performed it for the first time for this project, Terraform will ask to perform an init step first.
This step is usually straightforward and can be performed by `terraform init`.

## SSH to VM

One can connect to a VM via SSH:
```sh
# ssh <username>@<public-ip> -i <path-to-private-key>
ssh ubuntu@x.y.z.a -i thor-infrastructure.pem
```
## Example

### Basic example

For example, user need to scale down the Twitter crawler instance to 0.
Thus, change `twitter_crawler_num` in `cluster.tfvars` to 0 and do `terraform apply ...` as mentioned above.

Should the crawler is needed in the future, change the `twitter_crawler_num` to desired number, such as 1, and do the `terraform apply ...` again.
The terminal will show the plan to create 1 new VM.

Remember, Terraform will only create the VM.
To deploy the crawler service inside, please refer to [Ansible](../ansible/README.md).

### Adding new VM(s)

For a more comprehensive example, please refer [pull#3](https://github.com/IDUNN-project/WP4_Thor/pull/3).
To add new VM(s), there are some modified files under `terraform` folder:
1. `cluster.tfvars`: the type and number of wanted replica for this VM
2. `main.tf`:
    1. `resource "aws_instance" "foobar"`: specification of the VM
    2. under `resource "local_sensitive_file" "hosts_ini"`: we need to pass the `foobar` instance to `host_ini` as part of Ansible inventory template
    3. `resource "local_sensitive_file" "foobar_env"`: pass information to the service that will live on top of this VM, in this case we are passing the name and value of `ENV_NAME`
3. `templates/inventory.tpl`: template for Ansible inventory. Notice that `foobar` on line 42 is passed from Point 2.2 above.
4. `variables.tf`: declare the required variables
5. `vpc.tf`: security group or firewall configuration for this new VM

## Deploying an independent copy

To deploy an independent copy of the infrastructure (which contains VMs, VPC, subnet, etc.), user is required to make his/her own change on `backend.tf` file.
This is required so Terraform can write infrastructure state to a different location, instead of changing the original one.

For instance, create a new S3 bucket from AWS console e.g. `foo-bucket`, and put this name on `bucket` key in `backend.tf` file.
User need to reconfigure Terraform to use the new state:
```sh
# reconfigure
terraform init -reconfigure

# create the resources
terraform apply -var-file=cluster.tfvars
```

Notice that on the terminal Terraform plans to create everything, as on this new copy no resources has been created yet.

## Secrets

Credentials that are required by the running services are stored in [AWS Secrets Manager](https://eu-central-1.console.aws.amazon.com/secretsmanager/listsecrets?region=eu-central-1).
Upon executing `terraform apply ...`, Terraform will read the credentials from AWS, integrate into local sensitive file templates, and write them to files in a form that can be read by the services.
Ultimately, these files will be uploaded together with the code via [Ansible](../ansible/README.md).

This decision was taken because there has to be a secure place where credentials can be stored without passing it to others via email or chat.
Try to change the region in your browser if you cannot find the secret.
