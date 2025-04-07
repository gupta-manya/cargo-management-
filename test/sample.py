import pandas as pd
from typing import List, Tuple


# Load CSV files
items = pd.read_csv('input_items2.csv')
containers = pd.read_csv('containers.csv')

def fits(item, container):
    return (item['width_cm'] <= container['width_cm'] and
            item['depth_cm'] <= container['depth_cm'] and
            item['height_cm'] <= container['height_cm'])

# Mock used space tracker
used_space = {cid: [] for cid in containers['container_id']}

# Check if space is overlapping
def is_overlapping(start1, end1, start2, end2):
    return not (
        end1[0] <= start2[0] or start1[0] >= end2[0] or
        end1[1] <= start2[1] or start1[1] >= end2[1] or
        end1[2] <= start2[2] or start1[2] >= end2[2]
    )

# Try to find empty space in a container
def find_empty_space(container, item_dims, used):
    step = 5
    max_x, max_y, max_z = container['width_cm'], container['depth_cm'], container['height_cm']
    item_w, item_d, item_h = item_dims

    for x in range(0, int(max_x - item_w) + 1, step):
        for y in range(0, int(max_y - item_d) + 1, step):
            for z in range(0, int(max_z - item_h) + 1, step):
                start = (x, y, z)
                end = (x + item_w, y + item_d, z + item_h)
                if all(not is_overlapping(start, end, s, e) for s, e in used):
                    return start, end
    return None, None

# Main algorithm
def place_items(items_df, containers_df):
    items_df = items_df.sort_values(by='priority', ascending=False)
    placement_results = []

    for _, item in items_df.iterrows():
        item_dims = (item['width_cm'], item['depth_cm'], item['height_cm'])
        preferred_zone = item['preferred_zone']
        placed = False
        fallback = []

        for _, container in containers_df.iterrows():
            if not fits(item, container):
                continue

            container_id = container['container_id']
            zone = container['zone']
            used = used_space[container_id]

            start, end = find_empty_space(container, item_dims, used)

            if start and end:
                if zone == preferred_zone:
                    used_space[container_id].append((start, end))
                    placement_results.append({
                        'item_id': item['item_id'],
                        'name': item['name'],
                        'placed_in': container_id,
                        'zone': zone,
                        'priority': item['priority'],
                        'start': start,
                        'end': end
                    })
                    placed = True
                    break
                else:
                    fallback.append((container_id, zone, start, end))

        if not placed and fallback:
            cid, zone, start, end = fallback[0]
            used_space[cid].append((start, end))
            placement_results.append({
                'item_id': item['item_id'],
                'name': item['name'],
                'placed_in': cid,
                'zone': zone,
                'priority': item['priority'],
                'start': start,
                'end': end,
                'note': 'Placed in non-preferred zone'
            })
        elif not placed:
            placement_results.append({
                'item_id': item['item_id'],
                'name': item['name'],
                'priority': item['priority'],
                'status': 'Could not be placed',
                'suggestion': 'Rearrange lower-priority items or expand storage'
            })

    return placement_results
# Run the placement function
placements = place_items(items, containers)

# Print formatted results
for result in placements:
    print("-----")
    for key, value in result.items():
        print(f"{key}: {value}")
