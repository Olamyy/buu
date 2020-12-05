import click

from app.config import Config
from app.utils import get_aws_auth_headers, post_request, format_input_data, write_target_list, VegetaHelper


@click.command()
@click.option(
    "--config",
    required=True
)
def cli(config: str):
    config = Config(config_path=config)

    aws_auth_headers = get_aws_auth_headers(
        sagemaker_config=config.sagemaker_config
    )

    if post_request(headers=aws_auth_headers, sagemaker_config=config.sagemaker_config):
        format_input_data(
            sagemaker_config=config.sagemaker_config,
            vegeta_config=config.vegeta_config
        )

        write_target_list(headers=aws_auth_headers,
                          config=config)

        vegeta_helper = VegetaHelper(config.vegeta_config)

        vegeta_helper.run_load_test()

        if config.vegeta_config.format == "html":
            vegeta_helper.plot()

            if config.vegeta_config.open:
                vegeta_helper.open_browser()

        else:
            vegeta_helper.write_report()
