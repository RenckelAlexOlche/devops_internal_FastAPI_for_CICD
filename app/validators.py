import re
from fastapi import HTTPException

def password_check(passwd: str, **parameters: dict[bool]) -> bool:
    SpecialSym =['$', '@', '#', '%']

    errors = []

    val = True
    
    if len(passwd) < 6:
        errors.append(
            {
                'title': 'PasswordTooShort',
                'description': 'Length should be at least 6'
                }
            )
        val = False
         
    if len(passwd) > 255:
        errors.append(
            {
                'title': 'PasswordTooLong',
                'description': 'Length should be not be greater than 255'
                }
            )
        val = False
         
    if not any(char.isdigit() for char in passwd):
        errors.append(
            {
                'title': 'PasswordRequiresDigits',
                'description': 'Password should have at least one numeral'
                }
            )
        val = False
         
    if not any(char.isupper() for char in passwd):
        errors.append(
            {
                'title': 'PasswordRequiresUppercaseLiteral',
                'description': 'Password should have at least one uppercase letter'
                }
            )
        val = False
         
    if not any(char.islower() for char in passwd):
        errors.append(
            {
                'title': 'PasswordRequiresLowercaseLiteral',
                'description': 'Password should have at least one lowercase letter'
                }
            )
        val = False
         
    if not any(char in SpecialSym for char in passwd) and not parameters.get('skip_specific_literals'):
        errors.append(
            {
                'title': 'PasswordRequiresSpecificLiterals',
                'description': 'Password should have at least one of the symbols $, @, #, %'
                }
            )
        val = False


    if not val:
        raise HTTPException(status_code=400, detail=errors)

    return val


def username_check(username) -> bool:
    pattern = r"^(?=.{6,30}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"

    val = bool(re.fullmatch(pattern, username))

    if not val:
        raise HTTPException(status_code=400, detail=[{'title': 'InvalidUsername', 'description': 'Username contains special characters or its length isn\'t between 6 and 30 characters inclusive'}])

    return val

    
def email_check(email) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.]+[^-]$"

    val = bool(re.fullmatch(pattern, email))

    if not val:
        raise HTTPException(status_code=400, detail=[{'title': 'InvalidEmail', 'description': 'The email contains special characters or an incorrect entry'}])

    return val


