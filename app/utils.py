import json
import os
import subprocess
import webbrowser

import boto3
import click
import requests
from botocore import auth
from botocore.awsrequest import AWSRequest

def log_if_verbose(verbose, message):
    return click.echo(message) if verbose else None


def read_json(data_path):
    with open(data_path, 'r') as data_file:
        data = json.load(data_file)
    return data


def read_csv(data_path):
    payloads = []
    with open(data_path, 'r') as data_file:
        for row in data_file:
            payloads.append(
                row.rstrip('\n')
            )
    return payloads

def read_input_data(data_path, content_type):
    if content_type == "application/json":
        data = read_json(data_path)
        data = json.dumps(data)
    else:
        data = read_csv(data_path)

    return data

def get_aws_auth_headers(sagemaker_config):
    credentials = boto3.Session().get_credentials()
    sagemaker_auth = auth.SigV4Auth(credentials, "sagemaker", sagemaker_config.region)
    data = read_input_data(sagemaker_config.data_path, sagemaker_config.content_type)

    aws_request = AWSRequest(
        method="POST",
        url=sagemaker_config.full_endpoint,
        headers={
            "Content-type": sagemaker_config.content_type
        },
        data=data[0]
    )
    sagemaker_auth.add_auth(aws_request)

    return aws_request.headers


def post_request(headers, sagemaker_config):
    data = read_input_data(sagemaker_config.data_path, sagemaker_config.content_type)

    response = requests.post(
        url=sagemaker_config.full_endpoint,
        json=data, headers=headers)

    return response.raise_for_status()


def format_input_data(sagemaker_config, vegeta_config):
    data = read_input_data(sagemaker_config.data_path, sagemaker_config.content_type)
    with open(vegeta_config.vegeta_config.payload_json_filename, "w") as f:
        f.write(json.dumps(data))

    return


def write_target_list(headers, config):
    target_list = [
                      f"POST {config.sagemaker_config.full_endpoint}"
                  ] \
                  + [f"{header}: {headers[header]}" for header in headers] \
                  + ["@payload.json"]

    with open(config.vegeta_config.target_list_file_name, 'w') as file_object:
        file_object.write("\n".join(target_list))


class VegetaHelper:
    def __init__(self, vegeta_config):
        self.config = vegeta_config

    def run_load_test(self):
        vegeta_command = subprocess.Popen(
            ['vegeta', 'attack', f'-duration={self.config.duration}s', f'-rate={self.config.rate}/s',
             '-targets=targets.list',
             f'-output={self.config.binary_file_path}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        return vegeta_command.communicate()

    def plot(self):
        with open(self.config.html_file_path, 'w') as file_object:
            subprocess.call(['vegeta', 'plot', '--title', self.config.name, self.config.binary_file_path], stdout=file_object)

    def open_browser(self):
        browser = webbrowser.get('chrome')

        return browser.open_new_tab(f"file://{os.path.realpath(self.config.html_file_path)}")

    def write_report(self):
        command = subprocess.Popen(
            [
                'vegeta', 'report', f"{self.config.binary_file_path}"
            ]
        )

        return command.communicate()

    @staticmethod
    def mock_vegeta_call(verbose):
        log_if_verbose(verbose=verbose, message="Checking vegeta installation.")
        try:
            output = subprocess.call(["vegeta", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if output != 0:
                return None
            return True
        except FileNotFoundError:
            return None
