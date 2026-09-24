from android_llm_gnn.preprocess.dalvik_normalizer import DalvikNormalizer


def test_normalize_instruction_rewrites_method_reference_tokens() -> None:
    normalizer = DalvikNormalizer()
    normalized = normalizer.normalize_instruction(
        "invoke-virtual",
        "v0, v1, Lcom/example/Foo;->bar(Ljava/lang/String;)V",
    )
    assert normalized.opcode == "invoke-virtual"
    assert "class_foo" in normalized.tokens
    assert "api_bar" in normalized.tokens
    assert "param_string" in normalized.tokens
    assert "return_void" in normalized.tokens


def test_normalize_external_method_emits_external_api_prefix() -> None:
    normalizer = DalvikNormalizer()
    normalized = normalizer.normalize_external_method(
        "Lcom/example/Foo;",
        "qux",
        "(I)Ljava/lang/String;",
    )
    assert normalized.tokens[0] == "external_api"
    assert "class_foo" in normalized.tokens
    assert "api_qux" in normalized.tokens
    assert "param_int" in normalized.tokens
    assert "return_string" in normalized.tokens
