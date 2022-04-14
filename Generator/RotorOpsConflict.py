import dcs
import random

jtf_red = "Combined Joint Task Forces Red"
jtf_blue = "Combined Joint Task Forces Blue"



def triggerSetup(rops, options):
    # get the boolean value from ui option and convert to lua string
    def lb(var):
        return str(options[var]).lower()


    game_flag = 100
    # Add the first trigger
    trig = dcs.triggers.TriggerOnce(comment="RotorOps Setup Scripts")
    trig.rules.append(dcs.condition.TimeAfter(1))
    #trig.actions.append(dcs.action.DoScriptFile(rops.scripts["mist_4_4_90.lua"]))
    trig.actions.append(dcs.action.DoScriptFile(rops.scripts["mist_4_5_107_grimm.lua"]))
    trig.actions.append(dcs.action.DoScriptFile(rops.scripts["Splash_Damage_2_0.lua"]))
    trig.actions.append(dcs.action.DoScriptFile(rops.scripts["CTLD.lua"]))
    trig.actions.append(dcs.action.DoScriptFile(rops.scripts["RotorOps.lua"]))
    script = ""
    script = ("--OPTIONS HERE!\n\n" +
              "RotorOps.CTLD_crates = " + lb("crates") + "\n\n" +
              "RotorOps.CTLD_sound_effects = true\n\n" +
              "RotorOps.force_offroad = " + lb("force_offroad") + "\n\n" +
              "RotorOps.voice_overs = " + lb("voiceovers") + "\n\n" +
              "RotorOps.zone_status_display = " + lb("game_display") + "\n\n" +
              "RotorOps.inf_spawn_messages = true\n\n" +
              "RotorOps.inf_spawns_per_zone = " + lb("inf_spawn_qty") + "\n\n" +
              "RotorOps.apcs_spawn_infantry = " + lb("apc_spawns_inf") + " \n\n")
    if not options["smoke_pickup_zones"]:
        script = script + 'RotorOps.pickup_zone_smoke = "none"\n\n'
    trig.actions.append(dcs.action.DoScript(dcs.action.String((script))))
    rops.m.triggerrules.triggers.append(trig)

    # Add the second trigger
    trig = dcs.triggers.TriggerOnce(comment="RotorOps Setup Zones")
    trig.rules.append(dcs.condition.TimeAfter(2))
    for s_zone in rops.staging_zones:
        trig.actions.append(dcs.action.DoScript(dcs.action.String("RotorOps.addStagingZone('" + s_zone + "')")))
    for c_zone in rops.conflict_zones:
        zone_flag = rops.conflict_zones[c_zone].flag
        trig.actions.append(
            dcs.action.DoScript(dcs.action.String("RotorOps.addZone('" + c_zone + "'," + str(zone_flag) + ")")))

    trig.actions.append(dcs.action.DoScript(dcs.action.String("RotorOps.setupConflict('" + str(game_flag) + "')")))

    rops.m.triggerrules.triggers.append(trig)

    # Add the third trigger
    trig = dcs.triggers.TriggerOnce(comment="RotorOps Conflict Start")
    trig.rules.append(dcs.condition.TimeAfter(10))
    trig.actions.append(dcs.action.DoScript(dcs.action.String("RotorOps.startConflict(100)")))
    rops.m.triggerrules.triggers.append(trig)

    # Add generic zone-based triggers
    for index, zone_name in enumerate(rops.conflict_zones):
        z_active_trig = dcs.triggers.TriggerOnce(comment=zone_name + " Active")
        z_active_trig.rules.append(dcs.condition.FlagEquals(game_flag, index + 1))
        z_active_trig.actions.append(dcs.action.DoScript(dcs.action.String("--Add any action you want here!")))
        rops.m.triggerrules.triggers.append(z_active_trig)

    # # Add CTLD beacons - this might be cool but we'd need to address placement of the 3D objects
    # trig = dcs.triggers.TriggerOnce(comment="RotorOps CTLD Beacons")
    # trig.rules.append(dcs.condition.TimeAfter(5))
    # trig.actions.append(dcs.action.DoScript(dcs.action.String("ctld.createRadioBeaconAtZone('STAGING','blue', 1440,'STAGING/LOGISTICS')")))
    # for c_zone in rops.conflict_zones:
    #     trig.actions.append(
    #         dcs.action.DoScript(dcs.action.String("ctld.createRadioBeaconAtZone('" + c_zone + "','blue', 1440,'" + c_zone + "')")))
    # rops.m.triggerrules.triggers.append(trig)

    # Zone protection SAMs
    if options["zone_protect_sams"]:
        for index, zone_name in enumerate(rops.conflict_zones):
            z_sams_trig = dcs.triggers.TriggerOnce(comment="Deactivate " + zone_name + " SAMs")
            z_sams_trig.rules.append(dcs.condition.FlagEquals(game_flag, index + 1))
            z_sams_trig.actions.append(dcs.action.DoScript(
                dcs.action.String("Group.destroy(Group.getByName('Static " + zone_name + " Protection SAM'))")))
            rops.m.triggerrules.triggers.append(z_sams_trig)

    # Zone FARPS always
    if options["zone_farps"] == "farp_always" and not options["defending"]:
        for index, zone_name in enumerate(rops.conflict_zones):
            if index > 0:
                previous_zone = list(rops.conflict_zones)[index - 1]
                if not rops.m.country(jtf_blue).find_group(previous_zone + " FARP Static"):
                    continue
                z_farps_trig = dcs.triggers.TriggerOnce(comment="Activate " + previous_zone + " FARP")
                z_farps_trig.rules.append(dcs.condition.FlagEquals(game_flag, index + 1))
                z_farps_trig.actions.append(
                    dcs.action.ActivateGroup(rops.m.country(jtf_blue).find_group(previous_zone + " FARP Static").id))
                # z_farps_trig.actions.append(dcs.action.SoundToAll(str(rops.res_map['forward_base_established.ogg'])))
                z_farps_trig.actions.append(dcs.action.DoScript(dcs.action.String(
                    "RotorOps.farpEstablished(" + str(index) + ")")))
                rops.m.triggerrules.triggers.append(z_farps_trig)

    # Zone FARPS conditional on staged units remaining
    if options["zone_farps"] == "farp_gunits" and not options["defending"]:
        for index, zone_name in enumerate(rops.conflict_zones):
            if index > 0:
                previous_zone = list(rops.conflict_zones)[index - 1]
                if not rops.m.country(jtf_blue).find_group(previous_zone + " FARP Static"):
                    continue
                z_farps_trig = dcs.triggers.TriggerOnce(comment="Activate " + previous_zone + " FARP")
                z_farps_trig.rules.append(dcs.condition.FlagEquals(game_flag, index + 1))
                z_farps_trig.rules.append(dcs.condition.FlagIsMore(111, 20))
                z_farps_trig.actions.append(dcs.action.DoScript(dcs.action.String(
                    "--The 100 flag indicates which zone is active.  The 111 flag value is the percentage of staged units remaining")))
                z_farps_trig.actions.append(
                    dcs.action.ActivateGroup(rops.m.country(jtf_blue).find_group(previous_zone + " FARP Static").id))
                # z_farps_trig.actions.append(dcs.action.SoundToAll(str(rops.res_map['forward_base_established.ogg'])))
                z_farps_trig.actions.append(dcs.action.DoScript(dcs.action.String(
                    "RotorOps.farpEstablished(" + str(index) + ")")))
                rops.m.triggerrules.triggers.append(z_farps_trig)

    # Add attack helos triggers
    for index in range(options["e_attack_helos"]):
        random_zone_obj = random.choice(list(rops.conflict_zones.items()))
        zone = random_zone_obj[1]
        z_weak_trig = dcs.triggers.TriggerOnce(comment=zone.name + " Attack Helo")
        z_weak_trig.rules.append(dcs.condition.FlagIsMore(zone.flag, 1))
        z_weak_trig.rules.append(dcs.condition.FlagIsLess(zone.flag, random.randrange(20, 90)))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String("---Flag " + str(
            zone.flag) + " value represents the percentage of defending ground units remaining in zone. ")))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String("RotorOps.spawnAttackHelos()")))
        rops.m.triggerrules.triggers.append(z_weak_trig)

    # Add attack plane triggers
    for index in range(options["e_attack_planes"]):
        random_zone_obj = random.choice(list(rops.conflict_zones.items()))
        zone = random_zone_obj[1]
        z_weak_trig = dcs.triggers.TriggerOnce(comment=zone.name + " Attack Plane")
        z_weak_trig.rules.append(dcs.condition.FlagIsMore(zone.flag, 1))
        z_weak_trig.rules.append(dcs.condition.FlagIsLess(zone.flag, random.randrange(20, 90)))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String("---Flag " + str(
            zone.flag) + " value represents the percentage of defending ground units remaining in zone. ")))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String("RotorOps.spawnAttackPlanes()")))
        rops.m.triggerrules.triggers.append(z_weak_trig)

    # Add transport helos triggers
    for index in range(options["e_transport_helos"]):
        random_zone_obj = random.choice(list(rops.conflict_zones.items()))
        zone = random_zone_obj[1]
        z_weak_trig = dcs.triggers.TriggerOnce(comment=zone.name + " Transport Helo")
        z_weak_trig.rules.append(dcs.condition.FlagIsMore(zone.flag, 1))
        z_weak_trig.rules.append(dcs.condition.FlagIsLess(zone.flag, random.randrange(20, 100)))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String(
            "---Flag " + str(game_flag) + " value represents the index of the active zone. ")))
        z_weak_trig.actions.append(dcs.action.DoScript(dcs.action.String("---Flag " + str(
            zone.flag) + " value represents the percentage of defending ground units remaining in zone. ")))
        z_weak_trig.actions.append(dcs.action.DoScript(
            dcs.action.String("RotorOps.spawnTranspHelos(8," + str(options["transport_drop_qty"]) + ")")))
        rops.m.triggerrules.triggers.append(z_weak_trig)

    # Add game won/lost triggers
    trig = dcs.triggers.TriggerOnce(comment="RotorOps Conflict WON")
    trig.rules.append(dcs.condition.FlagEquals(game_flag, 99))
    trig.actions.append(
        dcs.action.DoScript(dcs.action.String("---Add an action you want to happen when the game is WON")))
    trig.actions.append(
        dcs.action.DoScript(dcs.action.String("RotorOps.gameMsg(RotorOps.gameMsgs.success)")))
    rops.m.triggerrules.triggers.append(trig)
    trig = dcs.triggers.TriggerOnce(comment="RotorOps Conflict LOST")
    trig.rules.append(dcs.condition.FlagEquals(game_flag, 98))
    trig.actions.append(
        dcs.action.DoScript(dcs.action.String("---Add an action you want to happen when the game is LOST")))
    trig.actions.append(
        dcs.action.DoScript(dcs.action.String("RotorOps.gameMsg(RotorOps.gameMsgs.failure)")))
    rops.m.triggerrules.triggers.append(trig)