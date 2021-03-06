# Compound Serial Dilution

### Author
[Opentrons](http://www.opentrons.com/)

## Categories
* Basic Pipetting
    * Serial Dilution

## Description
With this protocol, your robot can perform compound serial dilution on up to 10 96-well plates by transferring samples from column 1 down the plate. You can also customize the number of dilutions by changing the number of columns in all of the plates.

---

You will need:
* P300 Multi-channel Pipette
* 96-well Plates

### Robot
* [OT-2](https://opentrons.com/ot-2)

### Modules

### Reagents

## Process
1. Set the number of plate you are processing in this protocol.
2. Set the number of dilutions (max=11).
3. Set the transfer volume.
4. Download your protocol.
5. Upload your protocol into the [OT App](https://opentrons.com/ot-app).
6. Set up your deck according to the deck map.
7. Calibrate your labware, tiprack and pipette using the OT App. For calibration tips, check out our [support article](https://support.opentrons.com/ot-2/getting-started-software-setup/deck-calibration).
8. Hit "Run".
9. Robot will mix and transfer the preloaded samples in column 1 to column 2; mix and transfer volume from column 2 to column 3, and so on until it has completed the number of dilutions set by the user.
10. Robot will repeat step 9 for every plate that is defined in the protocol.


### Additional Notes
The samples should be preloaded in column 1, and the dilution buffer should be preloaded in the rest of the columns.

The same set of tips will be used for the dilutions within the same plate.

The excess volume in the last column of the dilution will remain in the column after the mixing.

If you have any questions about this protocol, please contact protocols@opentrons.com.

###### Internal
NRezHffi
1486
