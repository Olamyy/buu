import sys
from dataclasses import dataclass

import click
import yaml

from app.utils import VegetaHelper


@dataclass
class SagemakerConfig:
    data_path: str
    region: str
    endpoint_name: str = None
    endpoint_url: str = None
    content_type: str = "application/json"

    def build_endpoint(self):
        return self.endpoint_url or f"https://runtime.sagemaker.{self.region}.amazonaws.com/endpoints/{self.endpoint_name}/invocations"

    def __post_init__(self):
        if self.endpoint_name and self.endpoint_url:
            raise ValueError(
                "You should only pass the endpoint name or the full url"
            )

        self.full_endpoint = self.build_endpoint()


@dataclass
class VegetaConfig:
    name: str
    rate: str
    duration: str = None
    format: str = "html"
    open: bool = True
    verbose: bool = True
    target_list_file_name: str = "targets.list"
    payload_json_filename: str = "payload.json"
    binary_file_output_name: str = None
    binary_file_path: str = None
    html_file_path: str = None

    def __post_init__(self):
        if not VegetaHelper.mock_vegeta_call(self.verbose):
            click.echo("Vegeta is not installed. Please, install vegeta and rerun buu.")
            sys.exit()
        if self.format not in ("html", "terminal"):
            raise ValueError(
                "Format should be one of html or bin"
            )

        self.binary_file_output_name = self.binary_file_output_name or f"{self.name}_rate_{self.rate}_duration_{self.duration}.bin"

        self.binary_file_path = self.binary_file_path or f"results/{self.binary_file_output_name}"

        self.html_file_path = self.html_file_path or f"html/{self.binary_file_output_name}.html"

@dataclass
class Config:
    config_path: str

    def __post_init__(self):
        self.config_content = self.read_config_yaml()
        self.sagemaker_config = SagemakerConfig(**self.config_content.get('sagemaker'))
        self.vegeta_config = VegetaConfig(**self.config_content.get('vegeta'),
                                          verbose=self.config_content.get('verbose'))

    def read_config_yaml(self):
        with open(self.config_path) as file_object:
            content = file_object.read()
        return yaml.load(content, Loader=yaml.FullLoader)
