import asyncio
import aiohttp
import random
import time
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# --- CONFIGURATION ---
console = Console()
OUTPUT_FOLDER = "results"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

SOURCES = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt"
]

class ProxyStorm:
    def __init__(self):
        self.raw_proxies = set()
        self.valid_proxies = []
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

    async def scrape(self):
        console.print("[bold cyan]🌀 INITIALIZING PROXY_STORM ENGINE...[/bold cyan]")
        async with aiohttp.ClientSession() as session:
            for url in SOURCES:
                try:
                    async with session.get(url, timeout=15) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            lines = text.splitlines()
                            count = 0
                            for line in lines:
                                line = line.strip()
                                if ":" in line:
                                    self.raw_proxies.add(line)
                                    count += 1
                            console.print(f"[dim white] → Fetched {count} from {url[:30]}...[/dim white]")
                except:
                    continue
        console.print(f"[bold green]✅ TOTAL RAW COLLECTED: {len(self.raw_proxies)}[/bold green]\n")

    async def check_proxy(self, session, proxy, progress, task_id):
        test_url = "http://httpbin.org/ip"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            start = time.time()
            async with session.get(test_url, proxy=f"http://{proxy}", headers=headers, timeout=8) as resp:
                if resp.status == 200:
                    latency = round((time.time() - start) * 1000)
                    self.valid_proxies.append((proxy, latency))
                    # console.print(f"[bold green]LIVE[/bold green] | {proxy} | {latency}ms")
        except:
            pass
        finally:
            progress.update(task_id, advance=1)

    async def run_validator(self):
        max_conn = 250
        connector = aiohttp.TCPConnector(limit=max_conn, ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)
        
        console.print(f"[bold yellow]⚡ STARTING HIGH-SPEED VALIDATION (Threads: {max_conn})[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, pulse_style="bright_cyan"),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Checking Proxies...", total=len(self.raw_proxies))
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = [self.check_proxy(session, p, progress, task) for p in self.raw_proxies]
                await asyncio.gather(*tasks)

    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_FOLDER}/active_{timestamp}.txt"
        
        # Sort by latency (fastest first)
        self.valid_proxies.sort(key=lambda x: x[1])
        
        with open(filename, "w") as f:
            for p, lat in self.valid_proxies:
                f.write(f"{p}\n")
        
        table = Table(title="STORM_REPORT Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value", style="bold cyan")
        table.add_row("Total Scraped", str(len(self.raw_proxies)))
        table.add_row("Alive Proxies", str(len(self.valid_proxies)))
        table.add_row("Efficiency", f"{(len(self.valid_proxies)/len(self.raw_proxies)*100):.2f}%")
        table.add_row("Output File", filename)
        
        console.print("\n", table)

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    engine = ProxyStorm()
    await engine.scrape()
    if engine.raw_proxies:
        await engine.run_validator()
        engine.save_results()
    else:
        console.print("[bold red]❌ No proxies found to check.[/bold red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 PROCESS TERMINATED BY USER[/bold red]")
