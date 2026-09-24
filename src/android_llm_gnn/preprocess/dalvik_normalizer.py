from __future__ import annotations

import re
from dataclasses import dataclass


REGISTER_RE = re.compile(r"^[vp]\d+$")
HEX_RE = re.compile(r"^[+-]?0x[0-9a-fA-F]+$")
INT_RE = re.compile(r"^[+-]?\d+$")
STRING_RE = re.compile(r'"[^"]*"')
METHOD_REF_RE = re.compile(r"(L[^;]+;)->([^\(\s]+)\((.*?)\)(\S+)")
FIELD_REF_RE = re.compile(r"(L[^;]+;)->([^\s:]+)\s+(\S+)")
TYPE_DESC_RE = re.compile(r"L[^;]+;")
SYMBOL_SPLIT_RE = re.compile(r"[\s,\[\]\(\)\{\}:;+*/=-]+")


PRIMITIVE_TYPES = {
    "V": "void",
    "Z": "boolean",
    "B": "byte",
    "S": "short",
    "C": "char",
    "I": "int",
    "J": "long",
    "F": "float",
    "D": "double",
}


def _safe_token(text: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z_]+", "_", text.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unk"


def _split_descriptor_params(params: str) -> list[str]:
    values: list[str] = []
    i = 0
    while i < len(params):
        current = params[i]
        if current == "[":
            start = i
            while i < len(params) and params[i] == "[":
                i += 1
            if i < len(params) and params[i] == "L":
                end = params.find(";", i)
                values.append(params[start : end + 1])
                i = end + 1
            else:
                values.append(params[start : i + 1])
                i += 1
        elif current == "L":
            end = params.find(";", i)
            values.append(params[i : end + 1])
            i = end + 1
        else:
            values.append(current)
            i += 1
    return values


def descriptor_to_type_token(descriptor: str) -> str:
    array_depth = descriptor.count("[")
    base = descriptor[array_depth:]
    if base in PRIMITIVE_TYPES:
        name = PRIMITIVE_TYPES[base]
    elif base.startswith("L") and base.endswith(";"):
        name = base[1:-1].split("/")[-1].split("$")[-1]
    else:
        name = base
    prefix = "array_" * array_depth
    return f"type_{_safe_token(prefix + name)}"


def method_signature_tokens(
    class_name: str, method_name: str, descriptor: str
) -> list[str]:
    tokens = [
        f"class_{_safe_token(class_name[1:-1].split('/')[-1].split('$')[-1])}"
        if class_name.startswith("L") and class_name.endswith(";")
        else f"class_{_safe_token(class_name)}",
        f"api_{_safe_token(method_name)}",
    ]
    match = re.fullmatch(r"\((.*?)\)(.+)", descriptor)
    if match:
        params, ret = match.groups()
        param_types = _split_descriptor_params(params)
        tokens.append(f"argc_{len(param_types)}")
        tokens.append(f"return_{descriptor_to_type_token(ret)[5:]}")
        for param in param_types[:4]:
            tokens.append(f"param_{descriptor_to_type_token(param)[5:]}")
    return tokens


@dataclass
class NormalizedInstruction:
    opcode: str
    tokens: list[str]
    text: str


class DalvikNormalizer:
    """Normalize Dalvik instructions into stable, LLM-friendly token strings."""

    def normalize_instruction(self, opcode: str, output: str = "") -> NormalizedInstruction:
        tokens = [opcode.lower()]
        remainder = output.strip()

        if remainder:
            remainder = STRING_RE.sub(" string_const ", remainder)
            remainder = METHOD_REF_RE.sub(self._replace_method_ref, remainder)
            remainder = FIELD_REF_RE.sub(self._replace_field_ref, remainder)
            remainder = TYPE_DESC_RE.sub(
                lambda match: " " + descriptor_to_type_token(match.group(0)) + " ",
                remainder,
            )

            parts = [part for part in SYMBOL_SPLIT_RE.split(remainder) if part]
            tokens.extend(self._normalize_token(part) for part in parts if part)

        tokens = [token for token in tokens if token]
        return NormalizedInstruction(opcode=opcode.lower(), tokens=tokens, text=" ".join(tokens))

    def normalize_external_method(
        self, class_name: str, method_name: str, descriptor: str
    ) -> NormalizedInstruction:
        tokens = ["external_api", *method_signature_tokens(class_name, method_name, descriptor)]
        return NormalizedInstruction(
            opcode="external_api",
            tokens=tokens,
            text=" ".join(tokens),
        )

    def normalize_method_instructions(
        self,
        instructions: list[tuple[str, str]],
        max_instructions: int | None = None,
    ) -> list[str]:
        rows: list[str] = []
        for opcode, output in instructions:
            rows.append(self.normalize_instruction(opcode, output).text)
            if max_instructions is not None and len(rows) >= max_instructions:
                break
        return rows

    def _replace_method_ref(self, match: re.Match[str]) -> str:
        class_name, method_name, params, ret = match.groups()
        descriptor = f"({params}){ret}"
        return " " + " ".join(method_signature_tokens(class_name, method_name, descriptor)) + " "

    def _replace_field_ref(self, match: re.Match[str]) -> str:
        class_name, field_name, field_type = match.groups()
        class_token = (
            f"class_{_safe_token(class_name[1:-1].split('/')[-1].split('$')[-1])}"
            if class_name.startswith("L") and class_name.endswith(";")
            else f"class_{_safe_token(class_name)}"
        )
        return (
            " "
            + " ".join(
                [
                    class_token,
                    f"field_{_safe_token(field_name)}",
                    descriptor_to_type_token(field_type),
                ]
            )
            + " "
        )

    def _normalize_token(self, token: str) -> str:
        lowered = token.strip().lower()
        if not lowered:
            return ""
        if REGISTER_RE.fullmatch(lowered):
            return "reg"
        if lowered == "string_const":
            return lowered
        if HEX_RE.fullmatch(lowered):
            value = lowered.lstrip("+-")
            return "address_like" if len(value) > 6 else "hex_int"
        if INT_RE.fullmatch(lowered):
            try:
                value = abs(int(lowered))
            except ValueError:
                return "int"
            return "small_int" if value < 32 else "large_int"
        if lowered.startswith("0x"):
            return "hex_int"
        if "@" in lowered:
            return "annotation_ref"
        if lowered.startswith("class_") or lowered.startswith("api_") or lowered.startswith("field_"):
            return lowered
        if lowered.startswith("type_") or lowered.startswith("param_") or lowered.startswith("return_"):
            return lowered
        if lowered.startswith("+") or lowered.startswith("-"):
            return "branch_offset"
        return _safe_token(lowered)

