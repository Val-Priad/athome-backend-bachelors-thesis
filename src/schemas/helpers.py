from types import UnionType
from typing import get_args, get_origin


def _is_list_annotation(annotation) -> bool:
    origin = get_origin(annotation)

    if origin is list:
        return True

    if origin is UnionType:
        return any(get_origin(arg) is list for arg in get_args(annotation))

    return False


def parse_query_params(schema_cls, args):
    data = {}

    for field_name in args.keys():
        values = args.getlist(field_name)

        if not values:
            continue

        field_info = schema_cls.model_fields.get(field_name)

        if field_info is not None and _is_list_annotation(
            field_info.annotation
        ):
            data[field_name] = values
        else:
            data[field_name] = values[-1]

    return data
