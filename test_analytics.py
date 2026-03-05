from analytics import prepare_dataframe, calculate_portfolio_value, calculate_weight
import pandas as pd
import pytest

def test_calc_portfolio_value():
    df = pd.DataFrame({
        "total_value": [100,200,300]
    })

    result = calculate_portfolio_value(df)

    assert result == 600

def test_prepare_dataframe():
    df = pd.DataFrame({
        "id": ["bitcoin", "ethereum", "cardano"],
        "name": ["Bitcoin", "Ethereum", "Cardano"],
        "current_price": [10000, 2000, 100],
        "price_change_percentage_24h": [1.0, 2.0, 3.0]
    })

    portfolio = {
        "bitcoin": 1,
        "ethereum": 3,
        "cardano": 10
    }

    result = prepare_dataframe(df, portfolio)

    assert result["quantity"].to_list() == [1, 3, 10]
    assert result["total_value"].to_list() == [10000, 6000, 1000]

def test_calculate_weight():
    df = pd.DataFrame({
        "id": ["bitcoin", "ethereum", "cardano"],
        "name": ["Bitcoin", "Ethereum", "Cardano"],
        "current_price": [10000, 2000, 100],
        "price_change_percentage_24h": [1.0, 2.0, 3.0],
        "total_value": [10000, 6000, 1000]
})
        
    result = calculate_weight(df)

    assert result["weight_%"].to_list()[0] == pytest.approx(58.82, abs=0.01)
    assert result["weight_%"].to_list()[1] == pytest.approx(35.29, abs=0.01)
    assert result["weight_%"].to_list()[2] == pytest.approx(5.88, abs=0.01)