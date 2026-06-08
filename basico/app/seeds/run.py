import typer

from basico.app.seeds.service import run_all, run_categories, run_tags, run_users

app = typer.Typer(help="Seeds: users, categories, tags")


@app.command("all")
def all_():
    run_all()
    typer.echo("Todos los seeds cargados")


@app.command("users")
def users():
    run_users()
    typer.echo("Usuarios Cargados")


def categories():
    run_categories()
    typer.echo("Categorias Cargadas")


def tags():
    run_tags()
    typer.echo("Etiquetas Cargadas")
