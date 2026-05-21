import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

API_URL = "http://127.0.0.1:8000/api/v1/jarvis/ask"

console = Console()

def ask_jarvis(query: str):
    response = requests.post(API_URL, json={"query": query, "mode": "auto"}, timeout=60)

    response.raise_for_status()
    return response.json()

def display_response(data: dict):
    console.print(
        Panel.fit(
            f"[bold cyan]Intent:[/bold cyan] {data.get('intent')}\n"
            f"[bold cyan]Entity:[/bold cyan] {data.get('entity')}\n"
            f"[bold cyan]Time Range:[/bold cyan] {data.get('time_range')}",
            title="Jarvis Understanding",
        )
    )

    summary = data.get("summary", "No summary available.")
    console.print(Panel(Markdown(summary), title="Jarvis Response"))

    sources = data.get("sources", [])

    if sources:
        console.print("\n[bold yellow]Sources:[/bold yellow]")
        for index, source in enumerate(sources, start=1):
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            published = source.get("published", "Unknown date")

            console.print(f"{index}. [bold]{title}[/bold]")
            console.print(f"   Published: {published}")
            console.print(f"   URL: {url}")

def main():
    console.print(
        Panel.fit(
            "[bold green]Jarvis CLI is online.[/bold green]\n"
            "Type your question below.\n"
            "Type [bold red]exit[/bold red] to quit.",
            title="Jarvis",
        )
    )

    while True:
        query = console.input("\n[bold blue]You:[/bold blue] ")

        if query.lower().strip() in ["exit", "quit", "q"]:
            console.print("[bold red]Jarvis shutting down.[/bold red]")
            break

        if not query.strip():
            continue

        try:
            console.print("[dim]Jarvis is thinking...[/dim]")
            data = ask_jarvis(query)
            display_response(data)

        except requests.exceptions.ConnectionError:
            console.print(
                "[bold red]Could not connect to Jarvis backend.[/bold red]\n"
                "Make sure FastAPI is running with:\n"
                "[yellow]uvicorn app.main:app --reload[/yellow]"
            )

        except requests.exceptions.HTTPError as error:
            console.print(f"[bold red]HTTP error:[/bold red] {error}")

        except Exception as error:
            console.print(f"[bold red]Unexpected error:[/bold red] {error}")

if __name__ == "__main__":
    main()