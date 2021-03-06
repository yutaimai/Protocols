from opentrons import labware, instruments, modules, robot

metadata = {
    'protocolName': 'NGS Prep',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request'
}

# labware
new_plate = labware.load('biorad-hardshell-96-PCR', '2')
trough = labware.load('trough-12row', '3')
tips10_rack = [labware.load('tiprack-10ul', slot)
               for slot in ['4', '5', '6', '7']]
tips300_rack = [labware.load('tiprack-200ul', slot)
                for slot in ['8', '9', '10', '11']]

# modules
magdeck = modules.load('magdeck', '1')
mag_plate = labware.load('biorad-hardshell-96-PCR',
                         '1',
                         share=True)

# pipettes
p10 = instruments.P10_Single(
    mount='right',
    tip_racks=tips10_rack
)

p300 = instruments.P300_Single(
    mount='left',
    tip_racks=tips300_rack
)

# reagent setup
beads = trough.wells('A1')
EtOH = trough.wells('A2')
water = trough.wells('A3')
liquid_trash = trough.wells('A4', to='A12')


def run_custom_protocol(number_of_columns: int = 12,
                        start_column: int = 1,
                        volume_of_beads: float = 10.0,
                        volume_of_first_supernatant_to_remove: float = 50,
                        number_of_washes: int = 2,
                        minutes_to_dry: int = 10,
                        resuspension_volume: float = 100,
                        volume_of_second_supernatant_to_remove: float = 50):
    # check for valid columns
    if number_of_columns + start_column > 13:
        raise Exception('Invalid columns.')

    # check for valid number of number of washes
    if number_of_washes > 9:
        raise Exception('Too many EtOH washes.')

    # setup sample locations
    mag_cols = mag_plate.columns(str(start_column), length=number_of_columns)
    mag_samples = [well for col in mag_cols for well in col]

    super_cols = new_plate.columns(str(start_column), length=number_of_columns)
    super_samples = [well for col in super_cols for well in col]

    # mix and transfer beads
    p300.pick_up_tip()
    p300.mix(10, 300, beads)
    p300.drop_tip()

    if volume_of_beads > 10:
        pipette = p300
    else:
        pipette = p10
    pipette.transfer(volume_of_beads,
                     beads,
                     [s.top() for s in mag_samples],
                     mix_after=(10, volume_of_beads))

    # incubate at room temperature for 15 minutes
    robot.comment('Incubating at room temperature for 15 minutes.')
    pipette.delay(minutes=15)

    magdeck.engage()
    robot.comment('Incubating with magnet engaged for 5 minutes.')
    pipette.delay(minutes=5)
    robot.pause('Ensure the sample liquid is clear before resuming. If not, '
                'allow the samples to incubate further until the liquid is '
                'clear.')

    # set tip for EtOH
    p300.pick_up_tip()
    EtOH_tip = p300.current_tip()
    p300.return_tip()

    # initialize sample tips for supernatant transfer
    sample_tips = []

    # remove supernatant from samples
    for s in mag_samples:
        p300.pick_up_tip()
        sample_tips.append(p300.current_tip())
        p300.transfer(volume_of_first_supernatant_to_remove,
                      s.bottom(2),
                      liquid_trash[0],
                      new_tip='never')
        p300.return_tip()

        # immediately transfer EtOH to sample
        p300.pick_up_tip(EtOH_tip)
        p300.transfer(200, EtOH, s.top(), new_tip='never')
        p300.return_tip()

    # perform supernatant transfer and EtOH washes
    for wash in range(1, number_of_washes):
        for s, tip in zip(mag_samples, sample_tips):
            p300.pick_up_tip(tip)
            p300.transfer(200,
                          s.bottom(2),
                          liquid_trash[wash],
                          new_tip='never')
            p300.return_tip()

            # immediately transfer EtOH to sample
            p300.pick_up_tip(EtOH_tip)
            p300.transfer(200, EtOH, s.top(), new_tip='never')
            p300.return_tip()

    # perform final supernatant disposal
    for s, t in zip(mag_samples, sample_tips):
        p300.pick_up_tip(t)
        p300.transfer(200,
                      s.bottom(2),
                      liquid_trash[wash],
                      new_tip='never')
        p300.return_tip()

    # dry beads
    p300.delay(minutes=minutes_to_dry)
    robot.pause('Ensure beads are completely dry before resuming.')
    magdeck.disengage()

    # resuspend in water
    if resuspension_volume > 10:
        pipette = p300
    else:
        pipette = p10

    # transfer and mix water
    for s in mag_samples:
        pipette.pick_up_tip()
        pipette.transfer(resuspension_volume,
                         water,
                         s,
                         new_tip='never')
        pipette.mix(10, pipette.max_volume, s)
        pipette.drop_tip()

    robot.comment('Incubating at room temperature for 2 minutes.')
    pipette.delay(minutes=2)

    robot.comment('Incubating with magnet engaged for 5 minutes.')
    magdeck.engage()
    pipette.delay(minutes=5)
    robot.pause('Ensure the sample liquid is clear before resuming. If not, '
                'allow the samples to incubate further until the liquid is '
                'clear.')

    # remove and discard supernatant in liquid trash
    if volume_of_second_supernatant_to_remove > 10:
        pipette = p300
    else:
        pipette = p10

    for source, dest in zip(mag_samples, super_samples):
        pipette.pick_up_tip()
        pipette.transfer(volume_of_second_supernatant_to_remove,
                         source.bottom(2),
                         dest,
                         new_tip='never')
        pipette.drop_tip()
