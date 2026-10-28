"""A whole-section comment argument such as `--pr_description={...}` merges into the section.

Repository settings already merge into a section key by key; comment arguments used to replace the
whole section, which dropped every key the argument did not name.
"""
import pytest

from pr_agent.algo.utils import update_settings_from_args
from pr_agent.config_loader import get_settings


@pytest.fixture
def pr_description_settings():
    """Put the section back after the test, whatever it changed."""
    settings = get_settings()
    saved = dict(settings.pr_description)
    yield settings
    settings.set("PR_DESCRIPTION", saved)


def test_a_mapping_changes_only_the_keys_it_names(pr_description_settings):
    settings = pr_description_settings
    before = dict(settings.pr_description)
    assert "enable_pr_diagram" in before and len(before) > 1

    update_settings_from_args(["--pr_description={'publish_labels': false}"])

    after = dict(settings.pr_description)
    assert after["publish_labels"] is False
    assert {k: v for k, v in after.items() if k != "publish_labels"} == {
        k: v for k, v in before.items() if k != "publish_labels"
    }


def test_the_keys_that_were_not_named_keep_their_configured_values(pr_description_settings):
    settings = pr_description_settings
    expected = settings.pr_description.collapsible_file_list_threshold

    update_settings_from_args(["--pr_description={'publish_labels': false}"])

    assert settings.pr_description.collapsible_file_list_threshold == expected
    # an attribute read of a key the argument did not name still works
    assert settings.pr_description.enable_pr_diagram is not None


def test_a_nested_mapping_merges_too(pr_description_settings):
    settings = pr_description_settings
    settings.set("PR_DESCRIPTION.nested_probe", {"a": 1, "b": 2})

    update_settings_from_args(["--pr_description={'nested_probe': {'a': 5}}"])

    assert settings.pr_description.nested_probe.a == 5
    assert settings.pr_description.nested_probe.b == 2


def test_a_section_argument_that_is_not_a_mapping_is_ignored(pr_description_settings):
    settings = pr_description_settings
    before = dict(settings.pr_description)

    update_settings_from_args(["--pr_description=x"])

    assert dict(settings.pr_description) == before


def test_a_dotted_key_still_sets_one_value(pr_description_settings):
    settings = pr_description_settings

    update_settings_from_args(["--pr_description.publish_labels=false"])

    assert settings.pr_description.publish_labels is False
