# shark2mqtt (Claude fork)

Bridge SharkNinja robot vacuums to [Home Assistant](https://www.home-assistant.io/) via MQTT autodiscovery.

> [!IMPORTANT]
> **This is a fork.** The original project is [CamSoper/shark2mqtt](https://github.com/CamSoper/shark2mqtt) by [Cam Soper](https://github.com/CamSoper), and nearly all of the code and the rest of this README are his work (MIT licence). This fork adds fixes found on a Shark **UR2850ZEUS** (vacuum + mop with a self-empty, self-fill dock). It is published so that the [Claude Shark2MQTT Home Assistant app](https://github.com/Heff2010/shark2mqtt-addon-claude_fork) can use it.

## What this fork changes, and why

The original bridge works on many Shark models, but on the UR2850ZEUS several things were wrong. This fork fixes them. Each change only switches on when the robot reports the data it needs, so other models should behave as they do with the original.

| Change | Why |
|---|---|
| **Configurable pause value** (`PAUSE_OPERATING_MODE`) | The UR2850 ignores the standard pause command (`1`). Sending `0` pauses it. |
| **Correct paused, docked and cleaning states** | The UR2850 reports a system status code and a clean job. The bridge now uses them, so Home Assistant shows Paused, Returning and Docked correctly, shows Docked while the robot empties its bin mid-job, and shows Cleaning for runs started from the Shark app or a Shark schedule. |
| **Faster updates during a job** | Fast polling starts as soon as a clean job exists, not only once the robot is moving. |
| **New diagnostic entities** | **System Status Code** and **Job Active**, on models that report them. |
| **Token login** (`BROWSER_LOGIN=false`) | The automated browser login fails on many setups and repeated failures can lock the Shark account. With it off, you log in yourself in a normal browser and give the bridge the token file. |
| **Side by side mode** (`ENTITY_ID_PREFIX`) | Lets this fork run next to the original during testing, with its own entities and MQTT topics. |
| **Stop no longer crashes** | Stop failed when the robot's mode was unknown. |

Saving the log to daily files is a feature of the [Home Assistant app](https://github.com/Heff2010/shark2mqtt-addon-claude_fork), not of this bridge.

**Where to report problems:** problems with this fork's changes go to [this repository's issues](https://github.com/Heff2010/shark2mqtt-claude_fork/issues). Issue and pull request numbers further down this README (such as #38) refer to the [original project](https://github.com/CamSoper/shark2mqtt/issues).

> [!NOTE]
> **EU region support:** Set `SHARK_REGION=eu` to use with EU Shark accounts. Thanks to [@hjennerway](https://github.com/hjennerway) for capturing the EU API traffic that made this possible.

## Confirmed Working Models

A growing list of models confirmed working in the wild lives in [CONFIRMED_MODELS.md](CONFIRMED_MODELS.md). That list comes from the original project and was reported against the original bridge. Other SharkNinja robot vacuums likely work too -- the list reflects what's been reported, not the limit of what's supported.

## Quick Start

1. Copy the example config and fill in your credentials:

   ```bash
   cp config.example.env .env
   # Edit .env with your Shark account and MQTT broker details
   ```

2. Run with Docker Compose:

   ```bash
   docker compose up -d
   ```

   This uses the pre-built image of this fork (see [Pre-built Image](#pre-built-image)). To build it yourself from this folder instead, run `docker compose up -d --build`.

## Home Assistant OS App (Add-on)

Running HAOS? Use **[Heff2010/shark2mqtt-addon-claude_fork](https://github.com/Heff2010/shark2mqtt-addon-claude_fork)**. It installs **Claude Shark2MQTT**, which runs this fork's bridge, from the Home Assistant app store (called the add-on store in older versions). No Docker setup needed.

It is itself a fork of the original add-on by [@400HPMustang](https://github.com/400HPMustang), **[400HPMustang/shark2mqtt-addon](https://github.com/400HPMustang/shark2mqtt-addon)**, which runs the *original* bridge without this fork's changes.

## Pre-built Image

A pre-built image of this fork is published, free and public, in GitHub's container registry: [`ghcr.io/heff2010/shark2mqtt`](https://github.com/users/Heff2010/packages/container/package/shark2mqtt). It is built for `amd64` and `arm64`.

There is **no `latest` tag**, on purpose: pick an exact version so an update never arrives by surprise. The current version is `1.5.5-claude.3`. All versions are listed on the [package page](https://github.com/users/Heff2010/packages/container/package/shark2mqtt).

```bash
docker run -d \
  --name shark2mqtt \
  --env-file .env \
  -v shark2mqtt_data:/data \
  --restart unless-stopped \
  ghcr.io/heff2010/shark2mqtt:1.5.5-claude.3
```

Or with Docker Compose (no `build` needed):

```yaml
services:
  shark2mqtt:
    image: ghcr.io/heff2010/shark2mqtt:1.5.5-claude.3
    env_file: .env
    volumes:
      - shark2mqtt_data:/data
    restart: unless-stopped

volumes:
  shark2mqtt_data:
```

The original, unmodified bridge is published separately by its author as `ghcr.io/camsoper/shark2mqtt`. It does not include this fork's changes.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `SHARK_USERNAME` | Yes | | Shark account email |
| `SHARK_PASSWORD` | Yes | | Shark account password |
| `MQTT_HOST` | Yes | | MQTT broker hostname |
| `SHARK_REGION` | No | `us` | `us` or `eu` |
| `SHARK_HOUSEHOLD_ID` | No | Auto-discovered | SharkNinja household ID |
| `MQTT_PORT` | No | `1883` | MQTT broker port |
| `MQTT_USERNAME` | No | | MQTT broker username |
| `MQTT_PASSWORD` | No | | MQTT broker password |
| `MQTT_PREFIX` | No | `shark2mqtt` | MQTT topic prefix |
| `POLL_INTERVAL` | No | `300` | Polling interval in seconds |
| `POLL_INTERVAL_ACTIVE` | No | `20` | Polling interval while cleaning |
| `PAUSE_OPERATING_MODE` | No | `1` | `Operating_Mode` value sent for pause: `1` or `0`. Some models ignore `1`; `0` is also "stop" on many models, so test it first |
| `BROWSER_LOGIN` | No | `true` | Set `false` to never launch the automated browser login. A missing or expired token then logs a "Shark login needed" error instead (see [Authentication](#authentication)) |
| `ENTITY_ID_PREFIX` | No | | Lowercase prefix for discovery IDs, to run a second copy beside the first. `claude` gives entities like `vacuum.claude_<name>`. Also set a different `MQTT_PREFIX` |
| `TOKEN_DIR` | No | `/data` | Directory for persisted auth tokens |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

See [`config.example.env`](config.example.env) for a ready-to-edit template.

## Authentication

shark2mqtt authenticates to SharkNinja's cloud using a browser-based Auth0 flow. The container runs a headed Chromium browser inside a virtual display (`xvfb`) to complete login automatically.

Auth tokens are persisted to the `/data` volume so the browser flow only runs when tokens expire.

To test authentication without starting the full service:

```bash
docker compose run --rm shark2mqtt --auth-once
```

This authenticates, lists discovered vacuums, saves tokens, and exits.

### If the "Verify you are human" challenge never passes

Cloudflare's bot detection occasionally flags the automated browser on some hosts or networks, leaving the Turnstile checkbox unchecked forever (with a red validation border in the failure screenshot). If you've hit this, you can bootstrap tokens on a different machine and copy them over:

1. On a desktop or laptop (ideally on a different network, e.g. your main PC rather than the server), clone this repo and run the auth flow once:

   ```bash
   docker compose run --rm shark2mqtt --auth-once
   ```

2. Copy `shark2mqtt_tokens.json` from that machine's `/data` volume into the `/data` volume on your server.

3. Start the service normally. It will use the saved refresh token and skip the browser flow entirely.

Another way to get the token file, without Docker on a second machine, is the **Shark Token Saver** Firefox extension in this fork's Home Assistant app repository ([tools/firefox-token-saver](https://github.com/Heff2010/shark2mqtt-addon-claude_fork/tree/main/tools/firefox-token-saver)). You log in to Shark yourself in Firefox and it saves `shark2mqtt_tokens.json`.

If you always supply tokens this way, set `BROWSER_LOGIN=false` so the service never tries the automated login itself. When the token stops working it logs "Shark login needed" and waits for a new token file instead.

The refresh token is long-lived, so once you have a working `shark2mqtt_tokens.json` the browser flow shouldn't be needed again unless SharkNinja revokes the session (e.g. after a password change).

Repeated failed attempts can temporarily lock your SharkNinja account, so if the challenge is failing, stop the retry loop (set restart policy to `no` or use `--auth-once`) before trying again.

### If login says "Your account has been locked"

This one is a different animal from the Turnstile problem above, and the message is misleading. The signature is:

- The automated login fails with *"Your account has been locked. Please check your email to log in"*.
- No lockout email ever arrives (check spam).
- Logging into [login.sharkninja.com](https://login.sharkninja.com) by hand, in a normal browser, with the same credentials, works immediately.
- Resetting your password changes nothing -- you get a byte-identical failure screenshot.

That combination means Auth0's risk-based bot detection has flagged the *automated sign-in pattern*, not your account. There is nothing wrong with your credentials and nothing to unlock. Thanks to @dewbot6 for diagnosing this in [#38](https://github.com/CamSoper/shark2mqtt/issues/38).

**What to do:** stop the retry loop and wait it out. Set the restart policy to `no` (or stop the add-on) and leave it alone for several hours -- overnight is a reasonable first attempt. Retrying against an already-flagged pattern tends to extend the block rather than clear it.

While you're waiting, it's worth confirming this isn't just a dead refresh token, which produces a similar "vacuum went unavailable but the app works fine" symptom. Look for this in the logs:

```
Auth0 refresh_token grant failed: <reason>
```

The reason is logged as of v1.5.5. An `invalid_grant` there means the saved token was revoked (a password change will do it), in which case you need a fresh browser login rather than a wait -- see the token bootstrap steps above.

If you hit this, please add what you find to [#38](https://github.com/CamSoper/shark2mqtt/issues/38), especially how long the block took to clear. How long the cooldown actually runs is still an open question.

## Home Assistant Entities

Each vacuum is automatically discovered by Home Assistant with the following entities:

| Entity | Type | Description |
|---|---|---|
| `vacuum.<name>` | Vacuum | Main entity with start/stop/pause/return/locate/fan speed |
| `sensor.<name>_battery` | Sensor | Battery level (%) |
| `sensor.<name>_rssi` | Sensor | WiFi signal strength (dBm) |
| `sensor.<name>_error_text` | Sensor | Current error description |
| `binary_sensor.<name>_charging` | Binary Sensor | Charging state |
| `binary_sensor.<name>_error` | Binary Sensor | Error state (on when error present) |
| `button.<name>_clean_<room>` | Button | One-tap room cleaning (one per room) |
| `select.<name>_clean_mode` | Select | Normal or Matrix (double-pass) cleaning mode |
| `select.<name>_water_flow` | Select | Mop water flow level (vac+mop models only) |
| `sensor.<name>_sys_st` | Sensor | System Status Code, the robot's raw status number (models that report it, such as the UR2850) |
| `binary_sensor.<name>_job_active` | Binary Sensor | On while a clean job is assigned (models that report it, such as the UR2850) |

Room buttons and the clean mode select appear automatically when room data is available from the Shark cloud. The water flow select appears only on models that report `Flow_Mode` -- i.e. those with a mop tank -- so vacuum-only models won't get a control their hardware ignores.

An error device trigger fires when a new error is detected, usable in HA automations.

### Vacuum States

| State | Description |
|---|---|
| `cleaning` | Vacuuming, mopping, or exploring |
| `paused` | Paused mid-clean |
| `returning` | Returning to dock |
| `docked` | On dock, idle or charging |
| `idle` | Stopped, not docked |
| `error` | Error detected |

### Fan Speeds

`eco`, `normal`, `max` — set via the fan speed control on the vacuum card. The selected speed is preserved while docked (the hardware resets to eco, but shark2mqtt remembers your choice).

## Commands

Standard vacuum commands (start, stop, pause, return to base, locate) work through the Home Assistant vacuum card.

### Room Cleaning

When room data is available from the Shark cloud, shark2mqtt creates **button entities** for each room (e.g., `button.shark_robot_clean_kitchen`). Press a button to start cleaning that room.

A **Clean Mode** select entity (`select.shark_robot_clean_mode`) lets you toggle between:

- **Normal** — single-pass clean
- **Matrix** — two-pass UltraClean (deep clean)

The selected mode applies to all room button presses.

### Advanced: `vacuum.send_command`

For automations that need multi-room cleaning or fine-grained control, you can still use `vacuum.send_command`:

#### Clean a Single Room

```yaml
service: vacuum.send_command
target:
  entity_id: vacuum.shark_robot
data:
  command: clean_room
  params:
    room: "Kitchen"
```

#### Clean Multiple Rooms

```yaml
service: vacuum.send_command
target:
  entity_id: vacuum.shark_robot
data:
  command: clean_rooms
  params:
    rooms: ["Kitchen", "Living Room"]
    clean_type: "dry"       # optional, default: dry
    clean_count: 1          # optional, default: 1
```

#### Deep Clean (Matrix Clean)

Two-pass UltraClean mode:

```yaml
service: vacuum.send_command
target:
  entity_id: vacuum.shark_robot
data:
  command: matrix_clean
  params:
    room: "Kitchen"
```

## Contributing

The text below is the original author's, about the original project. For this fork, open an issue or pull request on [this repository](https://github.com/Heff2010/shark2mqtt-claude_fork).

This project scratches a personal itch — I'm sharing it in case it helps others, not looking to take on a maintenance burden. If something doesn't work for you, please submit a **pull request** rather than an issue. I only own two vacuum models, so I can't test or troubleshoot devices I don't have. PRs with fixes or support for additional models are welcome; issues requesting changes are likely to be closed.

### Capturing a shadow dump

Nearly every model-specific fix here started as a shadow dump from someone else's hardware, so if you're reporting or fixing behaviour on a model I don't own, this is the single most useful thing to include.

Set `LOG_LEVEL=debug` and look for these lines, logged once per poll cycle per device:

```
Shadow values for <name>: {...}        # skegox backend
Ayla property values for <name>: {...} # Ayla backend
```

That's every property the device reports, **with its value**. Long blobs (map URLs, error logs) are truncated so the line stays readable.

Two things worth knowing:

- Some properties only hold their interesting value while a clean is actively assigned. `AreasToClean_V3`, for example, reverts to `*` once the robot docks, so start the clean and capture within the first couple of poll cycles. Setting `POLL_INTERVAL_ACTIVE=5` helps.
- Dumps contain your DSN, floor IDs, and room names. Redact them before posting.

## Acknowledgements

This fork exists thanks to [Cam Soper](https://github.com/CamSoper), who wrote shark2mqtt, and [@400HPMustang](https://github.com/400HPMustang), who wrote the Home Assistant add-on it builds on. The thanks below are Cam's, from the original project; issue numbers refer to that project.

Big thanks to the folks who've made this project better than I could've made it alone:

- [@hjennerway](https://github.com/hjennerway) -- captured the EU API traffic that made EU region support possible.
- [@hslabbert](https://github.com/hslabbert) -- patiently dug through round after round of DEBUG shadow dumps to shake out the room-naming bugs on PowerDetect models ([#4](https://github.com/CamSoper/shark2mqtt/issues/4)). Led to the MARD-as-authoritative-room-source fix.
- [@400HPMustang](https://github.com/400HPMustang) -- built the [Home Assistant OS add-on](https://github.com/400HPMustang/shark2mqtt-addon).
- [@Shadinss](https://github.com/Shadinss) -- ran capture after capture on RV2820YEUS mop behaviour ([#27](https://github.com/CamSoper/shark2mqtt/issues/27)), turning up the `cleantype: "wet"` payload and error code 48. Also the reason shadow dumps now log property *values* -- he was the one who pointed out they only ever logged the names.
- [@dewbot6](https://github.com/dewbot6) -- worked out that Auth0's "your account has been locked" message is bot detection flagging the automated login rather than a real lock ([#38](https://github.com/CamSoper/shark2mqtt/issues/38)), and found the `page.goto()` call sitting outside the try/except that fed the circuit breaker ([#37](https://github.com/CamSoper/shark2mqtt/pull/37)).
- [@xytras78](https://github.com/xytras78) -- caught that dry room cleans report `Operating_Mode 6` and had therefore been showing as `idle` in Home Assistant for their entire duration ([#39](https://github.com/CamSoper/shark2mqtt/pull/39)). Tested every mode on hardware and wrote down the negative result for mode 5 so nobody has to run that experiment again.
- [@adurham](https://github.com/adurham) -- added mop water flow level control after spotting `Flow_Mode` in a shadow dump ([#36](https://github.com/CamSoper/shark2mqtt/pull/36)), with a control test against the known-good `Power_Mode` path.

## Building from Source

```bash
git clone https://github.com/Heff2010/shark2mqtt-claude_fork.git
cd shark2mqtt-claude_fork
docker build -t shark2mqtt .
```

The image is ~1.2 GB due to the bundled Chromium browser required for authentication.
