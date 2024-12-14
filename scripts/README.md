# Automatic Challenge Solver

This scripts where built to automatically solve the [Exploiting NoSQL operator injection to extract unknown fields](https://portswigger.net/web-security/nosql-injection/lab-nosql-injection-extract-unknown-fields) challenge automatically.

### Installation
Launch the following command to install the dependencies:
```bash
pip install -r requirements.txt
```

### extract_fields.py
This script will extract all the MongoDB fields name.

**Usage**
```bash
python3 extract_fields.py [base_url: str] [session_cookie: str] (optional --pool-size: int)
```
**Arguments**
 - `base_url`: The base challenge url, ex: `https://0a9500ba041cb22184c53150005800e8.web-security-academy.net`
 - `session_cookie`: The value of the `session` cookie, ex: `42bLN0ruWjxrBVB2ZfwYXRaXJupwIdCB`
 - optional `--pool-size`: How many workers should be used for guessing

### brute_force_token.py
This script will extract the token value from the MongoDB server.

**Usage**
```bash
python3 brute_force_token.py [base_url: str] [session_cookie: str] [field_name: str] (optional --pool-size: int)
```

**Arguments**
 - `base_url`: The base challenge url, ex: `https://0a9500ba041cb22184c53150005800e8.web-security-academy.net`
 - `session_cookie`: The value of the `session` cookie, ex: `42bLN0ruWjxrBVB2ZfwYXRaXJupwIdCB`
 - `field_name`: The name of the MongoDB `reset token` column, this is needed as the field name could be randomized.
 - optional `--pool-size`: How many workers should be used for guessing