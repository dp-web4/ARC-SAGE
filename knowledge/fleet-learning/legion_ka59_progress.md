# ka59 Progress — Legion

## Game Understanding
- Sokoban push puzzle: push boxes onto goal markers
- CLICK to select which box is active (white center = active, gray = inactive)
- Directional keys move the ACTIVE box 3px per step  
- Two boxes, two goals per level (at least on L1)
- Purple wall divides playing field, must navigate around it
- Step counter at bottom limits total moves
- Push is recursive — pushing into another box pushes both

## L1 Layout
- Entity 1 (movable box): starts at ~(19, 31)
- Entity 2 (movable box): starts at ~(28, 31)  
- Left goal (dark bordered): center (13, 34)
- Right goal (dark bordered): center (46, 28)
- Purple wall: divides center vertically

## Key Discoveries
- GREEN border + WHITE center = active/selected box
- GREEN border + BLACK center = inactive/unselected box
- DARK GRAY center = placed/deactivated after click
- Click at entity center to switch selection (2px change confirms)
- Entity 1 blocks Entity 2's LEFT path
- Wall blocks both entities' RIGHT path

## Remaining Challenge
Need to find the correct ORDER:
1. Push Entity 1 to left goal (13, 34) — need LEFT 2, DOWN 1
2. Switch to Entity 2  
3. Navigate Entity 2 around the wall to right goal (46, 28)
   - Must go either UP or DOWN to get around the wall
   - Wall appears to extend most of the vertical space
   - Need to find the gap in the wall
