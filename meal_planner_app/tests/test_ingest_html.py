"""HTML / JSON-LD extraction for recipe ingest (no LLM)."""

from meal_planner_app.ingest.html_extract import (
    extract_jsonld_recipe,
    extract_visible_text,
    jsonld_partial,
    looks_like_html,
)

POLISH_JSONLD_HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
  <title>Ads and nav</title>
  <script>window.ads = true;</script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org/",
    "@type": "Recipe",
    "name": "Kurczak z jarmużem i ryżem",
    "description": "Obiad na szybko",
    "recipeIngredient": [
      "500 g filet z kurczaka",
      "2 szt cebula",
      "sól"
    ],
    "recipeInstructions": [
      {"@type": "HowToStep", "text": "Drobno pokroić cebulę"},
      {"@type": "HowToStep", "text": "Smażyć kurczaka"}
    ]
  }
  </script>
</head>
<body>
  <nav>Home | Przepisy | Reklama</nav>
  <h1>Kurczak z jarmużem i ryżem</h1>
  <ul>
    <li>500 g filet z kurczaka</li>
  </ul>
  <p>Drobno pokroić cebulę</p>
  <footer>Copyright 2026</footer>
</body>
</html>
"""

GRAPH_JSONLD_HTML = """
<html><head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "WebSite", "name": "Blog kuchenny"},
    {
      "@type": ["Recipe", "Thing"],
      "name": "Placki ziemniaczane",
      "recipeIngredient": "1 kg ziemniaki",
      "recipeInstructions": "Zetrzeć ziemniaki. Smażyć na oleju."
    }
  ]
}
</script>
</head><body><p>Placki ziemniaczane</p></body></html>
"""


def test_looks_like_html_detects_markup():
    assert looks_like_html(POLISH_JSONLD_HTML) is True
    assert looks_like_html("<div>składniki</div>") is True
    assert looks_like_html("1. Pokroić cebulę\n2. Smażyć") is False


def test_extract_visible_text_drops_script_nav_footer():
    text = extract_visible_text(POLISH_JSONLD_HTML)
    assert "window.ads" not in text
    assert "Home | Przepisy" not in text
    assert "Copyright 2026" not in text
    assert "Kurczak z jarmużem i ryżem" in text
    assert "500 g filet z kurczaka" in text
    assert "Drobno pokroić cebulę" in text


def test_extract_visible_text_plain_passthrough():
    raw = "1. Pokroić cebulę\n2. Smażyć kurczaka"
    assert extract_visible_text(raw) == raw


def test_extract_jsonld_recipe_from_script():
    node = extract_jsonld_recipe(POLISH_JSONLD_HTML)
    assert node is not None
    assert node["name"] == "Kurczak z jarmużem i ryżem"
    assert len(node["recipeIngredient"]) == 3


def test_extract_jsonld_recipe_from_graph():
    node = extract_jsonld_recipe(GRAPH_JSONLD_HTML)
    assert node is not None
    assert node["name"] == "Placki ziemniaczane"


def test_extract_jsonld_recipe_missing():
    assert extract_jsonld_recipe("<html><body><p>zupa</p></body></html>") is None
    assert extract_jsonld_recipe("zwykły tekst przepisu") is None


def test_jsonld_partial_maps_name_steps_and_ingredient_lines():
    node = extract_jsonld_recipe(POLISH_JSONLD_HTML)
    partial = jsonld_partial(node)
    assert partial["name"] == "Kurczak z jarmużem i ryżem"
    assert partial["description"] == "Obiad na szybko"
    assert "1. Drobno pokroić cebulę" in partial["instructions"]
    assert "2. Smażyć kurczaka" in partial["instructions"]
    assert partial["ingredient_lines"] == [
        "500 g filet z kurczaka",
        "2 szt cebula",
        "sól",
    ]


def test_jsonld_partial_string_instructions():
    node = extract_jsonld_recipe(GRAPH_JSONLD_HTML)
    partial = jsonld_partial(node)
    assert partial["instructions"] == "Zetrzeć ziemniaki. Smażyć na oleju."
    assert partial["ingredient_lines"] == ["1 kg ziemniaki"]
