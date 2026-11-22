"""Phase 0 smoke test: package modules import cleanly."""


def test_package_version():
    import src

    assert src.__version__ == "0.1.0"


def test_core_modules_import():
    from src.data import ingest, store
    from src.preferences import schema
    from src.filtering import filter as filter_mod
    from src.llm import client, parser, prompt
    from src.recommend import engine
    from src.api import routes
    from src.ui import app

    assert callable(ingest.ingest)
    assert callable(store.load_restaurants)
    assert callable(schema.validate_preferences)
    assert callable(filter_mod.filter_candidates)
    assert callable(prompt.build_recommendation_prompt)
    assert callable(client.LLMClient.complete)
    assert callable(parser.parse_recommendations)
    assert callable(engine.recommend)
    assert callable(routes.create_app)
    assert callable(app.main)
