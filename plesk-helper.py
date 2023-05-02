import questionary
import click
import subprocess
import socket


def get_current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    current_ip = s.getsockname()[0]
    s.close()
    return current_ip


def execute_command(args_array):
    argsString = ' '.join(args_array)
    subprocess.run(argsString, shell=True)


def domain_exists(domain):
    args = ['plesk', 'bin', 'domain', '--info']
    args.append(domain)
    result = subprocess.run(args, capture_output=True)
    return result.returncode == 0


@click.group()
def cli():
    pass


@cli.command()
def domain_create():
    args = ['plesk', 'bin', 'domain', '--create']
    domain = questionary.text("Enter domain name").ask()
    args.append(domain)

    if domain_exists(domain):
        print("Domain already exists")
        return

    enable_hosting = questionary.select("Enable hosting?", choices=["Yes", "No"]).ask()
    if enable_hosting == "Yes":
        args.append("-hosting")
        ip = get_current_ip()
        args.append('-ip')
        args.append(ip)
        # prompt for user
        user = questionary.text("Enter username").ask()
        args.append('-login')
        args.append(user)
        password = questionary.password("Enter password").ask()
        args.append('-passwd')
        args.append(password)

    execute_command(args)


@cli.command()
def domain_delete():
    #get list of domains
    args = ['plesk', 'bin', 'domain', '--list']
    result = subprocess.run(args, capture_output=True)
    domains = result.stdout.decode('utf-8').splitlines()
    domain = questionary.select("Select domain to delete", choices=domains).ask()
    args = ['plesk', 'bin', 'domain', '--delete']
    args.append(domain)
    areyousure = questionary.confirm("Are you sure?").ask()
    if areyousure:
        execute_command(args)

if __name__ == '__main__':
    cli()
