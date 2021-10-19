from scanner.scanner import Scanner

if __name__ == '__main__':
    with open('input.txt') as f:
        Scanner(content=f).scan_through()
