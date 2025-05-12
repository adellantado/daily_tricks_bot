import click
import logging
import asyncio

import bot

logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@click.command()
def python():
    try:
        click.echo("Starting to send Python tip...")
        asyncio.run(bot.send_python_tip())
        click.echo("Python tip sent successfully")
    except Exception as e:
        click.echo(f"Error sending Python tip: {e}")

@click.command()
def js():
    try:
        click.echo("Starting to send JS tip...")
        asyncio.run(bot.send_js_tip())
        click.echo("JS tip sent successfully")
    except Exception as e:
        click.echo(f"Error sending JS tip: {e}")

@click.command()
def trader():
    try:
        click.echo("Starting to send trader tip...")
        asyncio.run(bot.send_trader_tip())
        click.echo("Trader tip sent successfully")
    except Exception as e:
        click.echo(f"Error sending trader tip: {e}")

@click.command()
def blockchain():
    try:
        click.echo("Starting to send blockchain tip...")
        asyncio.run(bot.send_blockchain_tip())
        click.echo("Blockchain tip sent successfully")
    except Exception as e:
        click.echo(f"Error sending blockchain tip: {e}")

cli.add_command(python)
cli.add_command(js)
cli.add_command(trader)
cli.add_command(blockchain)

if __name__ == '__main__':
    cli()