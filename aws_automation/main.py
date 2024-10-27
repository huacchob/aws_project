"""Script to create and delete AWS CloudFormation stack."""

import typing as t
from pathlib import Path
from time import sleep

import boto3.session
from botocore.exceptions import ClientError


class AWSClient:
    """AWSClient class."""

    def __init__(
        self,
        profile_name: t.Optional[str] = "default",
        template_file_name: str = "launch_ec2.yml",
        ssh_key_file_name: str = "key_pair.pem",
        source_file_path: str = __file__,
        stack_name: str = "my-cloudformation-stack",
    ) -> None:
        """Initialize AWSClient

        Args:
            profile_name (t.Optional[str], optional): Name of the profile.
                Defaults to "default".
            template_file_name (str, optional): Name of the template file.
                Defaults to "launch_ec2.yml".
            ssh_key_file_name (str, optional): Name of the ssh key file.
                Defaults to "key_pair.pem".
            source_file_path (str, optional): Path to the source file.
                Defaults to __file__.
            stack_name (str, optional): Name of the stack.
                Defaults to "my-cloudformation-stack".
        """
        self.session: boto3.session.Session = self.open_session(
            profile_name=profile_name,
        )
        self.template_file_name: str = template_file_name
        self.ssh_key_file_name: str = ssh_key_file_name
        self.source_file_path: str = source_file_path
        self.stack_name: str = stack_name
        self.ec2: t.Any = self.session.client(service_name="ec2")
        self.cf: t.Any = self.session.client(service_name="cloudformation")

    def find_file_path(
        self,
        target_file_name: str,
    ) -> str:
        """Find the path to the file

        Args:
            target_file_name (str): The name of the target file.

        Raises:
            ValueError: Source file name is not specified
            ValueError: File `target_file_name` exists in multiple directories
            ValueError: File `target_file_name` not found

        Returns:
            str: The path to the file
        """
        source_file_path: Path = Path(self.source_file_path)

        # Check in the same directory, parent directory, and grandparent directory
        for directory in [
            source_file_path.parent,
            source_file_path.parent.parent,
            source_file_path.parent.parent.parent,
        ]:
            if directory.joinpath(target_file_name).exists():
                return str(object=directory.joinpath(target_file_name))

        raise ValueError(f"File {target_file_name} not found")

    def read_template(self) -> t.Any:
        """Read a template file.

        Args:
            template_file (str): The template file name.
            template_file_path (str): The path to the template file.

        Returns:
            t.Any: The template yaml file content.
        """
        template_file: str = self.find_file_path(
            target_file_name=self.template_file_name,
        )

        with open(file=template_file, mode="r", encoding="utf-8") as f:
            raw_data: str = f.read()

        return raw_data

    def open_session(
        self, profile_name: t.Optional[str] = "default"
    ) -> boto3.session.Session:
        """Open a boto3 session to AWS console

        Args:
            profile_name (str, optional): Name of the profile. Defaults to "default".

        Returns:
            boto3.session.Session: _boto3.session.Session_
        """
        console = boto3.session.Session(
            profile_name=profile_name,
            region_name="us-east-2",
        )
        return console

    def create_key_pair(self, key_name: str) -> None:
        """Generate a key pair in AWS

        Args:
            key_name (str): Name of the key pair

        Exceptions:
            ClientError: Key pair already exists

        Returns:
            None
        """
        try:
            key_pair: t.Dict[t.Any, t.Any] = self.ec2.create_key_pair(
                KeyName=key_name,
            )
            private_key: str = key_pair["KeyMaterial"]

            # Write the private key to a file
            with open(file=self.ssh_key_file_name, mode="w", encoding="utf-8") as f:
                f.write(private_key)

        except ClientError:
            print(f"Key pair '{key_name}' already exists.")

    def wait_for_completion(self, status: str) -> None:
        """Wait for the stack to complete processing

        Args:
            status (str): The status of the stack

        Returns:
            None
        """
        stack_description = self.cf.describe_stack_events(StackName=self.stack_name)
        all_events: t.List[t.Dict[str, t.Any]] = stack_description.get("StackEvents")
        statuses = [event.get("ResourceStatus") for event in all_events]
        while status not in statuses:
            sleep(5)
            stack_description = self.cf.describe_stack_events(StackName=self.stack_name)
            all_events: t.List[t.Dict[str, t.Any]] = stack_description.get(
                "StackEvents"
            )
            statuses = [event.get("ResourceStatus") for event in all_events]
            print("...")
        print(f"Stack {self.stack_name} is {status}.")

    def create_stack_with_parameters(self) -> None:
        """Create a stack with parameters

        Returns:
            None

        Exceptions:
            ClientError: Stack already exists
        """
        parameters: t.List[t.Dict[str, str]] = [
            {
                "ParameterKey": "InstanceType",
                "ParameterValue": "t2.micro",
            },
            {
                "ParameterKey": "KeyName",
                "ParameterValue": "test_key_pair",
            },
        ]

        try:
            self.cf.create_stack(
                StackName=self.stack_name,
                TemplateBody=self.read_template(),
                Parameters=parameters,
            )

            self.wait_for_completion(status="CREATE_COMPLETE")
        except ClientError:
            print(f"Stack '{self.stack_name}' already exists.")

    def delete_stack(self) -> None:
        """Delete the stack

        Exceptions:
            ClientError: Stack does not exist

        Returns:
            None
        """
        try:
            self.cf.delete_stack(StackName=self.stack_name)
            self.wait_for_completion(status="DELETE_COMPLETE")
        except ClientError:
            print(f"Stack '{self.stack_name}' does not exist.")


if __name__ == "__main__":
    console = AWSClient(
        profile_name="default",
        template_file_name="launch_ec2.yml",
        source_file_path=Path(__file__),
        ssh_key_file_name="key_pair.pem",
    )
    # console.create_stack_with_parameters()
    console.delete_stack()
