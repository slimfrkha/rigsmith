"""Drive the real screens headlessly with Textual's pilot."""

import asyncio

from test_runner import P, cfg  # noqa: F401  (fixture re-export)

from rigsmith.tui import Flow, PickerScreen, questionnaire


def drive(job, keys: list[str]):
    async def main():
        app = Flow(job)
        async with app.run_test(size=(140, 50)) as pilot:
            await pilot.pause()
            for k in keys:
                await pilot.press(k)
                await pilot.pause()
        return app.return_value

    return asyncio.run(main())


def test_questionnaire_flows_through_profile_sections_and_roles(cfg):
    async def job(app):
        return await questionnaire(app, cfg, P, [], None, [])

    answers, sections = drive(job, ["down", "enter", "enter", "down", "enter"])
    assert answers["profile"] == "standard" and answers["prompt"] == "p2" and sections == ["s"]


def test_questionnaire_back_and_quit(cfg):
    async def job(app):
        return await questionnaire(app, cfg, P, [], None, [])

    assert drive(job, ["escape"]) is None  # esc on the first question quits
    answers, _ = drive(job, ["enter", "escape", "down", "enter", "enter", "enter"])
    assert answers["profile"] == "standard"  # went back and changed the profile


def picker(cfg, keys, ticked=(), mode="install"):
    async def job(app):
        return await app.push_screen_wait(PickerScreen(cfg, P, cfg.entries, set(ticked), mode=mode))

    return drive(job, keys)


# tree lines: s, a, alpha, beta, gamma, hooked, editor, p, p1, p2
def test_picker_toggles_and_keeps_config_order(cfg):
    assert picker(cfg, ["down", "down", "down", "space", "enter"], ticked={"gamma"}) == ["beta", "gamma"]


def test_picker_group_toggle_and_radio_roles(cfg):
    assert picker(cfg, ["down", "space", "enter"]) == ["alpha", "beta", "gamma", "hooked", "editor"]
    keys = ["down"] * 8 + ["space", "down", "space", "enter"]
    assert picker(cfg, keys) == ["p2"]  # ticking p2 unticks p1: one prompt


def test_picker_search_help_and_cancel(cfg):
    assert picker(cfg, ["slash", "g", "a", "m", "enter", "down", "down", "space", "enter"]) == ["gamma"]
    assert picker(cfg, ["down", "down", "h", "escape", "space", "enter"]) == ["alpha"]
    assert picker(cfg, ["escape"]) is None


def test_picker_init_mode_sets_profiles(cfg):
    out = picker(cfg, ["down", "down", "2", "enter"], ticked={"alpha"}, mode="init")
    assert out["picked"] == ["alpha"] and out["profiles"]["alpha"] == "standard"
    out = picker(cfg, ["down", "down", "2", "enter"], ticked={"alpha"})  # profile keys only in init
    assert out == ["alpha"]


def test_first_run_picks_a_preset_or_a_file(home):
    from rigsmith import config
    from rigsmith.tui import choose_base

    bases = config.available()  # presets…, example, reference (default), then "a YAML file"

    async def job(app):
        return await choose_base(app, bases)

    name, cfg = drive(job, ["up", "up", "up", "enter"])
    assert name == "server" and cfg.name.endswith("server.yaml")

    mine = home / "mine.yaml"
    mine.write_text("profiles: [minimal]\nsections:\n  cli:\n    search: {ripgrep: minimal}\n")
    name, cfg = drive(job, ["down", "enter", *str(mine), "enter"])
    assert name == str(mine) and cfg.ids == ["ripgrep"]

    assert drive(job, ["down", "enter", *"/nope.yaml", "enter", "escape", "escape"]) is None  # bad path → asked again
