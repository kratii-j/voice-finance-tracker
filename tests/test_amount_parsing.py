from voice_module import parse_expense


def test_parse_plain_four_digit_amount():
    info = parse_expense("Add 5000 to food")
    assert info["action"] == "add"
    assert info["amount"] == 5000
    assert info["category"] == "food"


def test_parse_space_separated_thousands():
    info = parse_expense("Add 5 000 to food")
    assert info["action"] == "add"
    # Accept 5000 as parsed; if fallback captures 5, that would be a bug
    assert info["amount"] == 5000


def test_parse_currency_prefix_rupee():
    info = parse_expense("Add ₹10,000 to transport")
    assert info["action"] == "add"
    assert info["amount"] == 10000
    assert info["category"] == "transport"


def test_parse_currency_suffix_rs():
    info = parse_expense("Add 1200 rs to entertainment")
    assert info["action"] == "add"
    assert info["amount"] == 1200
    assert info["category"] == "entertainment"
