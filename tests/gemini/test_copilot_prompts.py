from app.gemini.advanced_prompts import PromptEngineer


def test_market_prompt_nonempty():
    market_data = {"price": 100.0, "volume": 1000}
    prompt = PromptEngineer.get_market_analysis_prompt(market_data, timeframe="1h", use_cot=True)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
