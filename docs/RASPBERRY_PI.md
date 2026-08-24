# Raspberry Pi integration guide

## Reference hardware

The provided adapter supports this low voltage reference pattern:

* Raspberry Pi with I2C enabled.
* ADS1115 analog to digital converter on I2C bus 1.
* Voltage output pressure and flow transmitters whose output is electrically compatible with the ADS1115 input range.
* One isolated low voltage output driver for a normally closed demonstration valve or indicator load.
* One emergency stop input wired so that the software sees the active state when the loop is opened.
* Optional driver feedback input.

The Raspberry Pi has no native analog input. A 4 to 20 mA transmitter needs an appropriately rated precision shunt, input protection, isolation where required, and an ADC arrangement reviewed for the transmitter and grounding scheme. Do not copy a generic resistor value without checking power, tolerance, common mode voltage, fault energy, and isolation.

## GPIO and output rule

GPIO may drive only the logic input of a suitable isolated driver. It must not power a relay coil, solenoid, valve, MCB, contactor, or mains circuit directly. The final driver must be rated for the actual voltage, current, inductive energy, duty, fault condition, and required isolation.

The example configuration uses GPIO 23 for the command, GPIO 24 for emergency stop input, and GPIO 25 for optional feedback. Change these values to match the reviewed wiring.

## Installation

```bash
sudo apt update
sudo apt install python3-venv i2c-tools
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[pi]'
```

Enable I2C using the normal Raspberry Pi configuration utility, reboot, and confirm that the ADC appears at the configured address:

```bash
i2cdetect -y 1
```

## Read only commissioning

1. Set `hardware.mode` to `raspberry_pi`.
2. Set `CERTARIG_ENABLE_ACTUATION=0`.
3. Start the service on the Pi.
4. Request `/v1/snapshot` from the engineering computer.
5. Apply known independent reference values and compare raw voltage and engineering values.
6. Disconnect each sensor and operate the emergency stop to verify detectable fault states.

## Computer to Pi connection

Keep the Pi on a private engineering network. Use a strong operator key and restrict port 8080 to the engineering computer. For a longer lived deployment, place the service behind a mutually authenticated proxy or a VPN instead of exposing the plain HTTP service to a shared network.

```bash
export CERTARIG_OPERATOR_KEY='same-long-random-key-as-the-pi'
python3 -m certarig_edge.cli demo --url http://PI_ADDRESS:8080
```

The command above creates and validates a plan only. Add `--execute` only after the physical approval checklist has been completed.

## Hardware validation record

Record these items for every physical test:

* Pi model and operating system image.
* Git commit and configuration hash.
* ADC model, address, reference, and wiring.
* Sensor manufacturer, model, serial, range, output type, and calibration identifier.
* Driver and load ratings.
* Emergency stop and relief test evidence.
* Independent reference instrument and uncertainty.
* Reviewer, date, deviations, final outcome, and evidence checksum.
