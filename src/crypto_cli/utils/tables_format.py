from tabulate import tabulate

def format_table(table: list[dict]) -> str:

    return tabulate(table,
                    headers="keys",
                    tablefmt="pretty",
               numalign="right", stralign="left",
               showindex=range(1, len(table) + 1))
