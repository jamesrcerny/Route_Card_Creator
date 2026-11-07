# Route Card Tool

> A Windows desktop app that turns a primary and an alternate KML route into a printable Excel sheet of navigation route cards, one per team member.

<img width="2306" height="1181" alt="Screenshot 2026-11-07 134957" src="https://github.com/user-attachments/assets/d3dd9e47-db04-40e9-a47f-39df21af36c5" />
<img width="1128" height="723" alt="Screenshot 2026-11-07 135433" src="https://github.com/user-attachments/assets/49bbb4b2-5bbe-44ac-a032-5a5187d0eff0" />
<img width="2429" height="1246" alt="Screenshot 2026-11-07 135547" src="https://github.com/user-attachments/assets/9eac39bc-c0ea-4bc4-b5db-7eec3e9ce056" />
<img width="2237" height="1163" alt="Screenshot 2026-11-07 135613" src="https://github.com/user-attachments/assets/f3381b0a-cd3a-464b-8d99-c15fda0c935b" />
<img width="2352" height="860" alt="Screenshot 2026-11-07 135634" src="https://github.com/user-attachments/assets/9bc8c712-c71c-4144-ac33-67eddbca8131" />


---

## Overview

Building route cards by hand means looking up a grid reference for every checkpoint, then measuring the distance and bearing to the next one, then copying it all out for each person. This tool does the math and the formatting. Drop in two KML files exported from a mapping app and it produces a sheet that is ready to print.

## Features

- **Drag and drop:** one Primary Route KML and one Alternate Route KML.
- **Checkpoint parsing:** reads point placemarks in order and labels checkpoints from their names (for example CP 1, CP A).
- **Navigation data:** 8-digit MGRS grid reference (10 m precision), distance to the next point in meters, and magnetic bearing.
- **Magnetic bearings:** true bearing corrected with declination from the World Magnetic Model for the current date.
- **Printable output:** one card per team member (team size is configurable), tiled across a landscape Excel sheet scaled to fit the page width. Card height adapts to the number of checkpoints.
- **Single output file:** `RouteCards.xlsx`, saved next to the primary KML.

## Tech Stack

- **Language:** Python 3.12
- **Framework / UI:** customtkinter, tkinterdnd2 (drag and drop)
- **Key libraries:** mgrs, geopy (geodesic distance), pygeomag (World Magnetic Model), openpyxl
- **Other tools:** PyInstaller (Windows executable)
- **Platform:** Windows 10/11 desktop application

## Getting Started

### Option A — Run the app (for users)
1. Download the latest release from the [Releases](../../releases) page.
2. Requires Windows 10 or 11.
3. Run `RouteCardTool.exe`.
   *(Only run executables you trust.)*

### Option B — Build from source (for developers)
```bash
# clone the repo
git clone https://github.com/jamesrcerny/RouteCardTool.git
cd RouteCardTool

# install dependencies
pip install customtkinter tkinterdnd2 mgrs geopy pygeomag openpyxl

# run the app
python route_card_app.py
```

## Why I Built This

Doing route cards by hand is slow, and one typo in a grid or bearing causes problems later. I wanted the calculations done the same way every time, with a layout that prints cleanly.

## Roadmap / Known Limitations

- Reads point placemarks only. Lines and polygons in the KML are ignored.
- This is a planning aid. Check every grid, distance, and bearing against your map and official sources before relying on it.
- No automated tests yet.

## License

[Choose a license, for example MIT. See the LICENSE file.]

---

*Built by James Cerny — [github.com/jamesrcerny](https://github.com/jamesrcerny)*
