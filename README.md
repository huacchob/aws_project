# Project Documentation

## Initial Setup

If this is your first time accessing AWS services from the CLI, then follow these steps:

- **Sign-up for AWS account**: Please visit [this](https://signin.aws.amazon.com/signup?request_type=register) website to create an AWS account

- **Install aws-cli**: Please visit [this](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html?sc_channel=el&sc_content=eks-integrate-secrets-manager&sc_country=mult&sc_geo=mult&sc_outcome=acq) website to install the aws-cli tool

- **Create a user**: This step is not necessary, but best practice. There are some actions that your root account can do that other accounts can't.

  - If you are setting up your AWS accout for the first time, please follow the instructions in [this](https://docs.aws.amazon.com/rekognition/latest/dg/setting-up.html) link to create a user.
  - When you create the account, make sure you give the user account programmatic access
  - Make sure to save your **access key** and **secret access key**

- **configure local AWS settings**: You have to configrue your AWS settings to use when you are interacting with aws-cli tool

  - You can do this after you install the aws-cli tool
  - You can use the `aws configure` command to configure your access and secret keys
  - You will also have to select your preferred AWS region
  - You can confirm this by checking the **~/.aws/credentials** file

- **find boto3 documentation**: You can look at boto3 documentation by going to [this](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) page

- **make a copy of key_pair.example.pem**: Then rename it to key_pair.pem and run this command to change the permissions of the .pem file `chmod 400 key_pair.pem`.

## How to use

You can use the `create_key_pair` method to create SSH key pairs.
You can use the `create_stack_with_parameters` method to create the CloudFormation stack.
You can use the `delete_stack` method to delete the stack.
