import math
import curses

from package.util import get_direction_text, get_direction_icon

def render_scene(mRenderWidth, mRenderHeight, mScreenWidth, mScreenHeight, mMapWidth, mMapHeight,
                 mPlayerX, mPlayerY, mPlayerA, mFOV, mDepth, mElapsedTime, mMapData, stdscr):
    # Render the scene
    for x in range(mRenderWidth):
        # Calculate the ray angle (fixed to correct horizontal mirroring)
        fRayAngle = mPlayerA + mFOV / 2.0 - (x / mRenderWidth) * mFOV

        # Initial ray position and direction
        fDistanceToWall = 0.0
        bHitWall = False
        bBoundary = False

        fEyeX = math.sin(fRayAngle)
        fEyeY = math.cos(fRayAngle)

        # Variables to store the exact hit point
        fHitX = 0.0
        fHitY = 0.0

        # Incrementally cast ray from player
        while not bHitWall and fDistanceToWall < mDepth:
            fDistanceToWall += 0.1
            fTestX = mPlayerX + fEyeX * fDistanceToWall
            fTestY = mPlayerY + fEyeY * fDistanceToWall
            nTestX = int(fTestX)
            nTestY = int(fTestY)

            # Test if ray is out of bounds
            if nTestX < 0 or nTestX >= mMapWidth or nTestY < 0 or nTestY >= mMapHeight:
                bHitWall = True
                fDistanceToWall = mDepth
            else:
                # Ray is inbounds so test to see if the ray cell is a wall block
                if mMapData[nTestY][nTestX] == '#':
                    # Wall hit
                    bHitWall = True

                    # Store exact hit coordinates
                    fHitX = fTestX
                    fHitY = fTestY

                    # Boundary detection
                    # Check for boundaries (edges) between blocks
                    # We will sample points around the hit point and see if they are different

                    # List of distance and dot product pairs
                    p = []

                    for tx in range(2):
                        for ty in range(2):
                            # Compute vector from ray origin to corner
                            vy = nTestY + ty - mPlayerY
                            vx = nTestX + tx - mPlayerX
                            d = math.hypot(vx, vy)
                            if d != 0:
                                dot = (fEyeX * vx / d) + (fEyeY * vy / d)
                                p.append((d, dot))

                    # Sort pairs based on distance
                    p.sort(key=lambda x: x[0])

                    # Check if closest 2-3 hits are close to 90 degrees
                    fBound = 0.01
                    if len(p) >= 3:
                        if math.acos(p[0][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[1][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[2][1]) < fBound:
                            bBoundary = True

        if fDistanceToWall == 0:
            fDistanceToWall = 0.0001  # Prevent division by zero

        nCeiling = int(mScreenHeight / 2 - mScreenHeight / fDistanceToWall)
        nFloor = mScreenHeight - nCeiling

        # Use ASCII art to enhance wall appearance with vertical repetition
        # Define wall patterns for different distances and vertical positions
        wall_patterns = [
            ('#', curses.color_pair(1)),   # Very close walls
            ('%', curses.color_pair(2)),   # Close walls
            ('*', curses.color_pair(3)),   # Medium walls
            ('-', curses.color_pair(4)),   # Far walls
            (' ', curses.color_pair(5)),   # Very far walls
        ]

        # Determine which pattern to use based on distance
        if bBoundary:
            nShade, color_pair = ('|', curses.color_pair(7))  # Boundary color
        elif fDistanceToWall <= mDepth / 4.0:
            nShade_base, color_pair = wall_patterns[0]
        elif fDistanceToWall < mDepth / 3.0:
            nShade_base, color_pair = wall_patterns[1]
        elif fDistanceToWall < mDepth / 2.0:
            nShade_base, color_pair = wall_patterns[2]
        elif fDistanceToWall < mDepth:
            nShade_base, color_pair = wall_patterns[3]
        else:
            nShade_base, color_pair = wall_patterns[4]

        # Create vertical repetition by alternating characters based on y-coordinate
        for y in range(mScreenHeight):
            if y < nCeiling:
                # Sky
                ch = ' '
                stdscr.addch(y, x, ch, curses.color_pair(9))
            elif y >= nCeiling and y < nFloor:
                # Wall with vertical patterning
                # Alternate characters every few lines to create vertical repetition
                pattern_index = (y - nCeiling) % 4
                if pattern_index == 0:
                    nShade = nShade_base
                elif pattern_index == 1:
                    nShade = '|'
                elif pattern_index == 2:
                    nShade = nShade_base
                else:
                    nShade = '|'
                stdscr.addch(y, x, nShade, color_pair)
            elif y == nFloor:
                # Floor boundary (outline)
                stdscr.addch(y, x, '_', curses.color_pair(6))
            else:
                # Floor
                floor_char = '.'
                floor_color = curses.color_pair(8)
                stdscr.addch(y, x, floor_char, floor_color)

    # Draw separator between the rendering area and the map
    separator_x = mRenderWidth
    for y in range(mScreenHeight):
        try:
            stdscr.addch(y, separator_x, '|', curses.color_pair(7))
        except curses.error:
            pass

    # Display the map on the right side
    map_offset_x = mRenderWidth + 1  # +1 for separator
    for ny in range(mMapHeight):
        for nx in range(mMapWidth):
            ch = mMapData[ny][nx]
            screen_x = nx + map_offset_x
            screen_y = ny
            if 0 <= screen_x < mScreenWidth and 0 <= screen_y < mScreenHeight:
                color = curses.color_pair(4) if ch == '#' else curses.color_pair(0)
                try:
                    stdscr.addch(screen_y, screen_x, ch, color)
                except curses.error:
                    pass

    # Display the player on the map
    player_map_x = int(mPlayerX) + map_offset_x
    player_map_y = int(mPlayerY)
    if 0 <= player_map_x < mScreenWidth and 0 <= player_map_y < mScreenHeight:
        try:
            stdscr.addch(player_map_y, player_map_x, get_direction_icon(mPlayerA), curses.color_pair(2))
        except curses.error:
            pass

    # Display stats under the map
    stats_start_y = mMapHeight + 1  # Start below the map
    fps = 1.0 / mElapsedTime if mElapsedTime != 0 else 0.0  # Prevent division by zero

    dir_text = get_direction_text(mPlayerA)
    stats = [
        f"X={mPlayerX:.2f}",
        f"Y={mPlayerY:.2f}",
        f"Dir={dir_text}",
        f"FPS={fps:.2f}"
    ]
    for i, stat in enumerate(stats):
        screen_y = stats_start_y + i
        screen_x = mRenderWidth + 1
        if screen_y < mScreenHeight:
            try:
                stdscr.addstr(screen_y, screen_x, stat)
            except curses.error:
                pass
