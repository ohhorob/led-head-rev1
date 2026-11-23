# Pico 2 W antenna notch

Source: Raspberry Pi Pico 2 W datasheet section 2.2.1, 14 x 9 mm antenna clearance. https://pip-assets.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w/documents/RP-008304-DS-3-pico-2-w-datasheet.pdf

Layout: J10 pin 1 at (76.76,98.72), J11 pin 21 at (28.50,116.50), centre y=107.61. Pico antenna end x=27.13; 9 mm inward boundary x=36.13. Notch opens from carrier left edge x=26, y=100.61..114.61, extending to x=36.63 with 0.50 mm internal corner radii. The extra depth accommodates the fillets without intruding into the 14 x 9 mm rectangular clearance. Header strips and component pads are outside notch.

Only Edge.Cuts changed. All tracks, vias, zones, footprints and electrical properties retained exactly. Existing zone fills must be refilled to follow the new outline; any tracks near/across the notch need manual rerouting. This implements the recommended clearance, not a measured RF performance guarantee.
