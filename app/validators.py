import re



def regex_validator(pattern: str, string: str):
    return re.match(pattern, string) or None



def validate_field(field_name: str, error_msg: str = '', pattern: str = '') -> str:
    field_name_pat = regex_validator(pattern, field_name)
    if not field_name_pat:
        raise ValueError(
            f"{error_msg}"
        )

    return field_name

