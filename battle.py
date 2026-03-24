import pandas as pd
from api import get_type


def extract_stats(pokemon_json):
    stats = {}
    for s in pokemon_json.get("stats", []):
        stats[s["stat"]["name"]] = s["base_stat"]
    return stats


def extract_types(pokemon_json):
    return [t["type"]["name"] for t in pokemon_json.get("types", [])]


def type_multiplier(attack_type, defender_types):
    if not attack_type or not defender_types:
        return 1.0

    type_json = get_type(attack_type)
    if not type_json:
        return 1.0

    rel = type_json.get("damage_relations", {})
    double_to = {t["name"] for t in rel.get("double_damage_to", [])}
    half_to   = {t["name"] for t in rel.get("half_damage_to", [])}
    no_to     = {t["name"] for t in rel.get("no_damage_to", [])}

    mult = 1.0
    for d in defender_types:
        if d in no_to:
            mult *= 0.0
        elif d in double_to:
            mult *= 2.0
        elif d in half_to:
            mult *= 0.5

    return mult


def effectiveness_label(mult):
    """BONUS: human-readable effectiveness message."""
    if mult == 0:
        return "No effect!"
    elif mult >= 4:
        return "Super effective!! (x4)"
    elif mult >= 2:
        return "Super effective! (x2)"
    elif mult < 1:
        return f"Not very effective... (x{mult})"
    return ""


def compute_damage(attacker_stats, defender_stats, move_power, mult):
    attack  = attacker_stats.get("attack", 50)
    defense = defender_stats.get("defense", 50)
    base = (move_power * (attack / max(defense, 1))) / 5
    dmg  = int(max(1, base * mult))
    return dmg


def simulate_battle(p1, p2, move1, move2, max_turns=50):
    p1_name = p1["name"]
    p2_name = p2["name"]

    s1 = extract_stats(p1)
    s2 = extract_stats(p2)

    t1 = extract_types(p1)
    t2 = extract_types(p2)

    hp1 = int(s1.get("hp", 100))
    hp2 = int(s2.get("hp", 100))

    speed1 = s1.get("speed", 50)
    speed2 = s2.get("speed", 50)

    battle_log   = []
    hp_over_time = []

    turn = 1

    def record_hp(turn_num):
        hp_over_time.append({"Turn": turn_num, "Pokemon": p1_name, "HP": max(hp1, 0)})
        hp_over_time.append({"Turn": turn_num, "Pokemon": p2_name, "HP": max(hp2, 0)})

    record_hp(0)

    while hp1 > 0 and hp2 > 0 and turn <= max_turns:
        order = ["p1", "p2"] if speed1 >= speed2 else ["p2", "p1"]

        for who in order:
            if hp1 <= 0 or hp2 <= 0:
                break

            if who == "p1":
                attacker_name  = p1_name
                attacker_stats = s1
                defender_name  = p2_name
                defender_stats = s2
                defender_types = t2
                move           = move1
            else:
                attacker_name  = p2_name
                attacker_stats = s2
                defender_name  = p1_name
                defender_stats = s1
                defender_types = t1
                move           = move2

            move_power = int(move["power"])
            move_type  = move["type"]

            mult  = type_multiplier(move_type, defender_types)
            dmg   = compute_damage(attacker_stats, defender_stats, move_power, mult)
            label = effectiveness_label(mult)           # ✅ BONUS

            if who == "p1":
                hp2 -= dmg
                defender_hp = max(hp2, 0)
            else:
                hp1 -= dmg
                defender_hp = max(hp1, 0)

            battle_log.append({
                "Turn":          turn,
                "Attacker":      attacker_name,
                "Move":          move["name"],
                "Move Type":     move_type,
                "Power":         move_power,
                "Multiplier":    mult,
                "Effectiveness": label,                # ✅ BONUS
                "Damage":        dmg,
                "Defender":      defender_name,
                "Defender HP":   defender_hp,
            })

        record_hp(turn)
        turn += 1

    winner = p1_name if hp1 >= hp2 else p2_name
    return winner, pd.DataFrame(battle_log), pd.DataFrame(hp_over_time)