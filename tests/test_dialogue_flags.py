import pytest

import dialogue_flags as df

NODES = {
    "entry": {"options": [
        {"goto": "elder", "if": {}, "set": {"met_elder": True}},
        {"goto": "market", "if": {}, "set": {"has_coin": True}},
    ]},
    "elder": {"options": [
        {"goto": "quest", "if": {"met_elder": True}, "set": {"quest_taken": True}},
        {"goto": "market", "if": {"has_coin": False}, "set": {"has_coin": True}},
    ]},
    "market": {"options": [
        {"goto": "blacksmith", "if": {"has_coin": True}, "set": {}},
        {"goto": "ending", "if": {}, "set": {"has_coin": False}},
    ]},
    "quest": {"options": [
        {"goto": "ending", "if": {"quest_taken": True}, "set": {"armed": True}},
    ]},
    "blacksmith": {"options": [
        {"goto": "ending", "if": {"has_coin": True}, "set": {"armed": True}},
    ]},
    "ending": {"options": []},
}


def graph():
    return df.DialogueGraph(NODES)


def test_entry_options_all_visible():
    assert graph().visible_options("entry") == [0, 1]


def test_conditional_option_hidden_before_flag_set():
    assert graph().visible_options("market") == [1]


def test_select_applies_set_effects():
    d = graph()
    assert d.select("entry", 1) == "market"
    assert d.flags()["has_coin"] is True


def test_select_returns_goto_target():
    d = graph()
    d.select("entry", 0)
    assert d.select("elder", 1) == "market"


def test_select_hidden_option_is_rejected():
    with pytest.raises(ValueError):
        graph().select("market", 0)


def test_select_unknown_node_is_rejected():
    with pytest.raises(ValueError):
        graph().select("lane", 0)


def test_option_index_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        graph().select("entry", 7)


def test_constructor_rejects_unknown_target():
    bad = {"a": {"options": [{"goto": "ghost", "if": {}, "set": {}}]}}
    with pytest.raises(ValueError):
        df.DialogueGraph(bad)


def test_constructor_rejects_cycles():
    cyclic = {
        "a": {"options": [{"goto": "b", "if": {}, "set": {}}]},
        "b": {"options": [{"goto": "a", "if": {}, "set": {}}]},
    }
    with pytest.raises(ValueError):
        df.DialogueGraph(cyclic)
    with pytest.raises(ValueError):
        df.DialogueGraph({"solo": {"options": [{"goto": "solo", "if": {}, "set": {}}]}})


def test_diamond_graph_is_accepted_and_walkable():
    d = graph()
    assert d.select("entry", 0) == "elder"
    assert d.select("elder", 1) == "market"
    assert d.select("market", 0) == "blacksmith"
    assert d.select("blacksmith", 0) == "ending"
    assert d.flags()["armed"] is True


def test_setting_flag_false_hides_option():
    d = graph()
    d.select("entry", 1)
    assert d.visible_options("market") == [0, 1]
    d.select("market", 1)
    assert d.flags()["has_coin"] is False
    assert d.visible_options("market") == [1]


def test_flags_returns_copy():
    d = graph()
    d.select("entry", 1)
    f = d.flags()
    f["has_coin"] = False
    f["injected"] = True
    assert d.flags()["has_coin"] is True
    assert "injected" not in d.flags()


def test_node_without_options_returns_empty_list():
    assert graph().visible_options("ending") == []


def test_multi_flag_condition_needs_all():
    g = df.DialogueGraph({
        "hub": {"options": [
            {"goto": "vault", "if": {"key": True, "badge": True}, "set": {}},
            {"goto": "shop", "if": {}, "set": {"key": True}},
        ]},
        "shop": {"options": []},
        "vault": {"options": []},
    })
    assert g.visible_options("hub") == [1]
    g.select("hub", 1)
    assert g.visible_options("hub") == [1]


def test_negative_option_index_is_rejected():
    with pytest.raises(ValueError):
        graph().select("entry", -1)
