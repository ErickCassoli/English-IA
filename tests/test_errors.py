from app.services.evaluation.errors import detect_errors


def test_detects_common_patterns():
    errors = detect_errors("I am agree with the peoples and it is more better.")
    categories = {error.category.value for error in errors}
    assert "grammar" in categories
    assert "vocab" in categories
    assert any(error.corrected_text == "I agree" for error in errors)


def test_detects_fluency_flag():
    errors = detect_errors("Hi. Ok. Bye. Yo.")
    assert any(error.category.value == "fluency" for error in errors)
