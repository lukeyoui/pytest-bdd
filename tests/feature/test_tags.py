"""Test tags."""
import textwrap

import pytest

from pytest_bdd.parser import get_tags


def test_tags_selector(pytester):
    """Test tests selection by tags."""
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers =
        feature_tag_1
        feature_tag_2
        scenario_tag_01
        scenario_tag_02
        scenario_tag_10
        scenario_tag_20
    """
        ),
    )
    pytester.makefile(
        ".feature",
        test="""
    @feature_tag_1 @feature_tag_2
    Feature: Tags

    @scenario_tag_01 @scenario_tag_02
    Scenario: Tags
        Given I have a bar

    @scenario_tag_10 @scenario_tag_20
    Scenario: Tags 2
        Given I have a bar

    """,
    )
    pytester.makepyfile(
        """
        import pytest
        from pytest_bdd import given, scenarios

        @given('I have a bar')
        def _():
            return 'bar'

        scenarios('test.feature')
    """
    )
    result = pytester.runpytest("-m", "scenario_tag_10 and not scenario_tag_01", "-vv")
    outcomes = result.parseoutcomes()
    assert outcomes["passed"] == 1
    assert outcomes["deselected"] == 1

    result = pytester.runpytest("-m", "scenario_tag_01 and not scenario_tag_10", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1

    result = pytester.runpytest("-m", "feature_tag_1", "-vv").parseoutcomes()
    assert result["passed"] == 2

    result = pytester.runpytest("-m", "feature_tag_10", "-vv").parseoutcomes()
    assert result["deselected"] == 2


def test_multiline_tags(pytester):
    """Test tests selection by multiline tags."""
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers =
        feature_tag_1
        feature_tag_2
        scenario_tag_01
        scenario_tag_02
        scenario_tag_10
        scenario_tag_20
        scenario_tag_30
    """
        ),
    )
    pytester.makefile(
        ".feature",
        test="""
    @feature_tag_1
    @feature_tag_2
    Feature: Tags

    @scenario_tag_01 @scenario_tag_02
    Scenario: Tags
        Given I have a bar

    @scenario_tag_10
    @scenario_tag_20
    @scenario_tag_30
    Scenario: Tags 2
        Given I have a bar

    """,
    )
    pytester.makepyfile(
        """
        import pytest
        from pytest_bdd import given, scenarios

        @given('I have a bar')
        def _():
            return 'bar'

        scenarios('test.feature')
    """
    )
    result = pytester.runpytest("-m", "scenario_tag_10 and not scenario_tag_01", "-vv")
    outcomes = result.parseoutcomes()
    assert outcomes["passed"] == 1
    assert outcomes["deselected"] == 1

    result = pytester.runpytest("-m", "scenario_tag_01 and not scenario_tag_10", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1

    result = pytester.runpytest("-m", "feature_tag_1", "-vv").parseoutcomes()
    assert result["passed"] == 2

    result = pytester.runpytest("-m", "feature_tag_10", "-vv").parseoutcomes()
    assert result["deselected"] == 2

    result = pytester.runpytest("-m", " scenario_tag_02", "-vv").parseoutcomes()
    assert result["passed"] == 1

    result = pytester.runpytest("-m", " scenario_tag_10", "-vv").parseoutcomes()
    assert result["passed"] == 1

    result = pytester.runpytest("-m", " scenario_tag_20", "-vv").parseoutcomes()
    assert result["passed"] == 1

    result = pytester.runpytest("-m", " scenario_tag_30", "-vv").parseoutcomes()
    assert result["passed"] == 1


def test_example_tags(pytester):
    """Test example selection by tags."""
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers =
        feature_tag_1
        scenario_tag_01
        example_tag_01
        example_tag_02
        example_tag_03
    """
        ),
    )
    pytester.makefile(
        ".feature",
        test="""
    @feature_tag_1
    Feature: Tags
        @scenario_tag_01
        Scenario Outline: Outlined with empty example values
            Given there are <start> cucumbers
            When I eat <eat> cucumbers
            Then I should have <left> cucumbers

            @example_tag_01
            Examples:
                | start | eat | left |
                | 1     | 1   | 0    |

            @example_tag_02
            @example_tag_03
            Examples:
                | start | eat | left |
                | 3     | 2   | 1    |

    """,
    )
    pytester.makepyfile(
        """
        import pytest
        from pytest_bdd import given, when, then, scenario
        from pytest_bdd.parsers import parse

        @scenario("test.feature", "Outlined with empty example values")
        def test_outline():
            pass

        @given(parse('there are {start} cucumbers'))
        def _():
            pass

        @when(parse('I eat {eat} cucumbers'))
        def _():
            pass

        @then(parse('I should have {left} cucumbers'))
        def _():
            pass
    """
    )
    result = pytester.runpytest("-m", "example_tag_01", "-vv").parseoutcomes()
    assert result["passed"] == 1

    result = pytester.runpytest("-m", "example_tag_02", "-vv").parseoutcomes()
    assert result["passed"] == 1

    result = pytester.runpytest("-m", "example_tag_01 or example_tag_02", "-vv").parseoutcomes()
    assert result["passed"] == 2

    result = pytester.runpytest("-m", "example_tag_01 and example_tag_02", "-vv").parseoutcomes()
    assert result["deselected"] == 2

    result = pytester.runpytest("-m", "scenario_tag_01 and example_tag_03", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1

    result = pytester.runpytest("-m", "scenario_tag_01 and example_tag_02", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1

    result = pytester.runpytest("-m", "feature_tag_1", "-vv").parseoutcomes()
    assert result["passed"] == 2

    result = pytester.runpytest("-m", "feature_tag_1 and not example_tag_02", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1

    result = pytester.runpytest("-m", "scenario_tag_01 and not example_tag_01", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1


def test_tags_after_background_issue_160(pytester):
    """Make sure using a tag after background works."""
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers = tag
    """
        ),
    )
    pytester.makefile(
        ".feature",
        test="""
    Feature: Tags after background

        Background:
            Given I have a bar

        @tag
        Scenario: Tags
            Given I have a baz

        Scenario: Tags 2
            Given I have a baz
    """,
    )
    pytester.makepyfile(
        """
        import pytest
        from pytest_bdd import given, scenarios

        @given('I have a bar')
        def _():
            return 'bar'

        @given('I have a baz')
        def _():
            return 'baz'

        scenarios('test.feature')
    """
    )
    result = pytester.runpytest("-m", "tag", "-vv").parseoutcomes()
    assert result["passed"] == 1
    assert result["deselected"] == 1


def test_apply_tag_hook(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.hookimpl(tryfirst=True)
        def pytest_bdd_apply_tag(tag, function):
            if tag == 'todo':
                marker = pytest.mark.skipif(True, reason="Not implemented yet")
                marker(function)
                return True
            else:
                # Fall back to pytest-bdd's default behavior
                return None
    """
    )
    pytester.makefile(
        ".feature",
        test="""
    Feature: Customizing tag handling

        @todo
        Scenario: Tags
            Given I have a bar

        @xfail
        Scenario: Tags 2
            Given I have a bar
    """,
    )
    pytester.makepyfile(
        """
        from pytest_bdd import given, scenarios

        @given('I have a bar')
        def _():
            return 'bar'

        scenarios('test.feature')
    """
    )
    result = pytester.runpytest("-rsx")
    result.stdout.fnmatch_lines(["SKIP*: Not implemented yet"])
    result.stdout.fnmatch_lines(["*= 1 skipped, 1 xpassed * =*"])


def test_tag_with_spaces(pytester):
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers =
        test with spaces
    """
        ),
    )
    pytester.makeconftest(
        """
        import pytest

        @pytest.hookimpl(tryfirst=True)
        def pytest_bdd_apply_tag(tag, function):
            assert tag == 'test with spaces'
    """
    )
    pytester.makefile(
        ".feature",
        test="""
    Feature: Tag with spaces

        @test with spaces
        Scenario: Tags
            Given I have a bar
    """,
    )
    pytester.makepyfile(
        """
        from pytest_bdd import given, scenarios

        @given('I have a bar')
        def _():
            return 'bar'

        scenarios('test.feature')
    """
    )
    result = pytester.runpytest_subprocess()
    result.stdout.fnmatch_lines(["*= 1 passed * =*"])


def test_at_in_scenario(pytester):
    pytester.makefile(
        ".feature",
        test="""
    Feature: At sign in a scenario

        Scenario: Tags
            Given I have a foo@bar

        Scenario: Second
            Given I have a baz
    """,
    )
    pytester.makepyfile(
        """
        from pytest_bdd import given, scenarios

        @given('I have a foo@bar')
        def _():
            return 'foo@bar'

        @given('I have a baz')
        def _():
            return 'baz'

        scenarios('test.feature')
    """
    )
    strict_option = "--strict-markers"
    result = pytester.runpytest_subprocess(strict_option)
    result.stdout.fnmatch_lines(["*= 2 passed * =*"])


@pytest.mark.parametrize(
    "line, expected",
    [
        ("@foo @bar", {"foo", "bar"}),
        ("@with spaces @bar", {"with spaces", "bar"}),
        ("@double @double", {"double"}),
        ("    @indented", {"indented"}),
        (None, set()),
        ("foobar", set()),
        ("", set()),
    ],
)
def test_get_tags(line, expected):
    assert get_tags(line) == expected
