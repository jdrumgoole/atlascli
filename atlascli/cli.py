import click


class CommandLineInterface:

    def __init__(self):
        pass

    @click.group()
    @click.option("-o", "--output", help="Output content to a file")
    @click.option("--publickey", help="The Atlas public key used to access the Atlas API")
    @click.option("--privatekey", help="The Atlas private key used to access the Atlas API")
    @click.option("-org", "--organization", help="Which organization should we select fron the config file")
    @click.option("-cfg", "--config", default="atlascli.cfg",  help="The configuration file to use")
    def cli(self, output, publickey, privatekey, organization, config):
        print(output)

    @cli.command()
    @click.option("-org", "--organization")
    def list(self, organization):
        print(organization)

    @cli.command()
    @click.option("-c", "--cluster_name", help="Name of the new cluster to be created")
    def create(self, cluster_name):
        click.echo(f"create: {cluster_name}")


if __name__ == '__main__':
    c = CommandLineInterface()
    c.cli()

