import pytest

import pet_training as pt

SPECIES = {
    "dragon": {
        "stats": {"power": 10, "speed": 8},
        "evolved": "dragonlord",
        "evolve_bonus": {"power": 6, "speed": 2},
    },
    "slime": {
        "stats": {"power": 3, "speed": 2},
        "evolved": None,
        "evolve_bonus": {},
    },
}


def trainer():
    return pt.PetTrainer(SPECIES)


def test_create_pet_sets_base_stats():
    t = trainer()
    t.create_pet("p1", "dragon")
    s = t.status("p1")
    assert s["stats"] == {"power": 10, "speed": 8}
    assert s["level"] == 1
    assert s["stage"] == 1
    assert s["stamina"] == 100


def test_unknown_species_raises():
    t = trainer()
    with pytest.raises(ValueError):
        t.create_pet("p1", "ghost")


def test_duplicate_pet_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    with pytest.raises(ValueError):
        t.create_pet("p1", "slime")


def test_train_increases_stat():
    t = trainer()
    t.create_pet("p1", "dragon")
    t.train("p1", "power", 0)
    assert t.status("p1")["stats"]["power"] == 11


def test_train_unknown_stat_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    with pytest.raises(ValueError):
        t.train("p1", "luck", 0)


def test_train_zero_amount_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    with pytest.raises(ValueError):
        t.train("p1", "power", 0, amount=0)


def test_train_during_cooldown_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    t.train("p1", "power", 0)
    with pytest.raises(ValueError):
        t.train("p1", "power", 29)


def test_train_at_cooldown_end_allowed():
    t = trainer()
    t.create_pet("p1", "dragon")
    t.train("p1", "power", 0)
    t.train("p1", "power", 30)
    assert t.status("p1")["stats"]["power"] == 12


def test_train_consumes_stamina():
    t = trainer()
    t.create_pet("p1", "dragon")
    t.train("p1", "power", 0)
    assert t.status("p1")["stamina"] == 90


def test_insufficient_stamina_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    with pytest.raises(ValueError):
        t.train("p1", "power", 0, amount=11)


def test_train_grants_level_up():
    t = trainer()
    t.create_pet("p1", "dragon")
    for now in (0, 30, 60, 90):
        t.train("p1", "power", now)
    s = t.status("p1")
    assert s["level"] == 2
    assert s["stats"]["power"] == 14


def test_evolve_below_level_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    with pytest.raises(ValueError):
        t.evolve("p1", 0)


def test_evolve_changes_stage_and_stats():
    t = trainer()
    t.create_pet("p1", "dragon")
    for now in (0, 30, 60, 90):
        t.train("p1", "power", now)
    t.evolve("p1", 120)
    s = t.status("p1")
    assert s["stage"] == 2
    assert s["name"] == "dragonlord"
    assert s["stats"] == {"power": 20, "speed": 10}


def test_evolve_twice_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    for now in (0, 30, 60, 90):
        t.train("p1", "power", now)
    t.evolve("p1", 120)
    with pytest.raises(ValueError):
        t.evolve("p1", 150)


def test_evolve_during_cooldown_raises():
    t = trainer()
    t.create_pet("p1", "dragon")
    for now in (0, 30, 60, 90):
        t.train("p1", "power", now)
    with pytest.raises(ValueError):
        t.evolve("p1", 110)
