# Saved Pigrow connections

The connection panel shows connection status, a Pigrow selector, Connect/Disconnect,
Edit list, and an arrow that shows or hides address, username and password.
Passwords are masked. Select **New connection…** to use the default credentials
from GUI Settings. Selecting an unlinked device fills its saved credentials and
opens the address controls.

Successful SSH connections save the entered credentials. A detected box name
updates the selector immediately, including after installation or a name refresh.
Devices without a readable Pigrow name remain **unknown pi** until a name is
available. Known names reconnecting at a new address update their stored location.

When an older named Pigrow shares the newly connected address, the dialog offers:

- **Remove**: delete the older saved profile.
- **Unlink**: clear its address and retain its name, username and password.
- **Ignore**: retain both profiles.

## Edit list and discovery

The list editor supports manual additions, edits, removal and unlinking. **Save**
keeps the draft; **Cancel** discards it, including devices found during discovery.
Pending form edits are applied on Save or when selecting another row.

**Seek IPs** accepts individual IPs, hostnames, IPv4 prefixes and multiple CIDR
subnets. It suggests local interfaces/routes and saved locations, probes SSH and
optionally ping, checks Raspberry Pi MAC prefixes, resolves hostnames, and uses
Avahi mDNS announcements when available. Scan results stay open for inspection.
IPs and discovered hostnames can be selected separately. **Stop** retains partial
results; **Use results** stages detected Pis and selected other candidates as
unknown pi profiles. A found location can also replace the selected profile's
address while preserving its credentials.

Discovery is tentative: MAC/hostname evidence cannot identify every Pi, especially
across routers where MAC addresses are unavailable. Enter another subnet to scan
when routing permits it. NAT or firewall isolation requires a route or appropriate
port forwarding. An open SSH port alone does not classify a device as a Pi.

## Settings and checks

Profiles are stored as JSON in the existing `gui_settings.txt` settings file.
Legacy address/credentials migrate to a tentative profile, and an explicitly empty
saved list stays empty. Writes are atomic, and the settings file is private to the
owner on POSIX systems. Credentials are stored locally in this file as requested;
they are not encrypted. GUI Settings contains defaults for new connections and the
shared SSH port; Edit list controls each stored device.

Run the regression suite from the repository root with Python and wxPython:

```sh
python -m unittest discover -s scripts/gui/tests -v
```

On a headless Linux machine, run the command through `xvfb-run -a`. Without
wxPython the desktop checks are skipped; profile and discovery checks still run.
SSH and network responses in these tests are simulated. Hardware discovery and
real SSH/SFTP require a reachable Pi for integration testing.
