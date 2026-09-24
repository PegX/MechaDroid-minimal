from android_llm_gnn.preprocess.method_keys import coalesce_node_metadata, parse_method_key


def test_parse_method_key_extracts_expected_fields() -> None:
    parsed = parse_method_key("Lcom/example/Foo$Inner;->bar(Ljava/lang/String;I)V")
    assert parsed["class_name"] == "Lcom/example/Foo$Inner;"
    assert parsed["method_name"] == "bar"
    assert parsed["descriptor"] == "(Ljava/lang/String;I)V"
    assert parsed["class_simple_name"] == "Inner"
    assert parsed["class_package"] == "com/example"


def test_coalesce_node_metadata_fills_missing_parts() -> None:
    payload = {"key": "Lcom/example/Foo;->baz()V", "method_name": ""}
    enriched = coalesce_node_metadata(payload)
    assert enriched["class_name"] == "Lcom/example/Foo;"
    assert enriched["method_name"] == "baz"
    assert enriched["descriptor"] == "()V"
