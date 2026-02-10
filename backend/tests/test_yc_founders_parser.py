from app.infrastructure.yc.sync import FoundersHTMLParser
from tests.utils.yc_founders_html import NANGO_FOUNDERS_HTML


def test_founders_html_parser_extracts_founders() -> None:
    parser = FoundersHTMLParser()
    parser.feed(NANGO_FOUNDERS_HTML)
    parser.close()
    founders = parser.founders()

    assert len(founders) == 2
    assert founders[0]["name"] == "Alice Founder"
    assert founders[0]["twitter_url"] == "https://twitter.com/alice"
    assert founders[0]["linkedin_url"] == "https://www.linkedin.com/in/alice/"
    assert founders[0]["role"] == "Founder"
    assert "Alice bio line 1" in (founders[0]["bio"] or "")

    assert founders[1]["name"] == "Bob Builder"
    assert founders[1]["twitter_url"] == "https://x.com/bob"
    assert founders[1]["linkedin_url"] is None
    assert founders[1]["role"] == "Co-Founder"

