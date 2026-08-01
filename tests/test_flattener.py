"""Unit tests for MenuFlattener (tree flattening and sibling/cyclic links)."""


def test_flatten_real_config(menu_flattener):
    flat = menu_flattener.flatten()
    assert len(flat) == 18


def test_root_node_is_branch_with_cyclic_navigation(menu_flattener):
    flat = menu_flattener.flatten()
    root = flat[0]
    assert root.id == "root"
    assert root.is_branch
    assert not root.is_leaf
    # root_navigate: cyclic comes from menu.yaml.
    assert root.navigate == "cyclic"


def test_get_node_by_id(menu_flattener):
    menu_flattener.flatten()
    start = menu_flattener.get_node_by_id("start")
    assert start is not None
    assert start.id == "start"
    assert menu_flattener.get_node_by_id("missing") is None


def test_leaf_and_branch_flags(menu_flattener):
    menu_flattener.flatten()
    start = menu_flattener.get_node_by_id("start")
    settings = menu_flattener.get_node_by_id("settings")
    assert start.is_leaf
    assert not start.is_branch
    assert settings.is_branch
    assert not settings.is_leaf


def test_cyclic_links_under_root(menu_flattener):
    menu_flattener.flatten()
    start = menu_flattener.get_node_by_id("start")
    settings = menu_flattener.get_node_by_id("settings")
    # root.navigate == cyclic => first and last children link to each other.
    assert start.prev_sibling.id == "settings"
    assert settings.next_sibling.id == "start"


def test_siblings_under_limit_branch(menu_flattener):
    menu_flattener.flatten()
    pwm = menu_flattener.get_node_by_id("pwm_frequency")
    # settings has navigate == limit, so its children are not cyclic.
    assert pwm.sibling_count == 3
    assert pwm.sibling_index == 0
    assert not pwm.has_cyclic_siblings
    assert pwm.prev_sibling is None
    assert pwm.next_sibling.id == "hi_channel"


def test_explicit_and_default_navigate(menu_flattener):
    menu_flattener.flatten()
    # Explicit navigate values are preserved.
    assert menu_flattener.get_node_by_id("start").navigate == "cyclic"
    assert menu_flattener.get_node_by_id("regimes").navigate == "cyclic"
    assert menu_flattener.get_node_by_id("settings").navigate == "limit"
    # Nodes without explicit navigate get default_navigate ("limit").
    assert menu_flattener.get_node_by_id("version").navigate == "limit"


def test_branch_without_explicit_navigate_gets_default(menu_flattener):
    """
    Branches without an explicit navigate receive default_navigate ("limit").

    ``_process_node`` assigns ``default_navigate`` to every node before the
    branch rule runs, so ``default_branch_navigate`` ("cyclic") is not applied
    and the children of such a branch are not cyclic-linked.
    """
    menu_flattener.flatten()
    hi_channel = menu_flattener.get_node_by_id("hi_channel")
    hi_on = menu_flattener.get_node_by_id("hi_on")
    hi_duty = menu_flattener.get_node_by_id("hi_duty")

    assert hi_channel.navigate == "limit"
    assert hi_on.sibling_count == 5
    assert hi_on.sibling_index == 0
    assert not hi_on.has_cyclic_siblings
    assert hi_on.prev_sibling is None
    assert hi_duty.next_sibling is None


def test_flatten_empty_list_returns_root_only(menu_flattener):
    flat = menu_flattener.flatten([])
    assert len(flat) == 1
    assert flat[0].id == "root"
    assert flat[0].children == []
