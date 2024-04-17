import numpy as np
from noise import pnoise2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import time
import random


# Constants
WIDTH, HEIGHT = 100, 100  # Dimensions representing the map (simplified scale)
MIN_ALTITUDE, MAX_ALTITUDE = -100, 2000  # Range of altitudes in meters
SEA_LEVEL = 0  # Sea level in meters

# Configuration for Europe-like settings
NORTH_TEMPERATURE = -10  # Approx winter temp in northern Europe
SOUTH_TEMPERATURE = 30  # Approx summer temp in southern Europe

def generate_base_map(width, height):
    """Generate a base map to initialize dimensions."""
    return np.zeros((height, width))


def generate_height_map(width, height, scale=0.03, octaves=5, persistence=0.6, lacunarity=2.1, min_alt=-1000, max_alt=5000, sea_percentage=0.4):
    """Generate a height map using Perlin noise, scaled to have a specified percentage below sea level."""
    height_map = np.zeros((height, width))

    # Randomize the base offsets for each generation
    base_x = random.randint(0, 10000)
    base_y = random.randint(0, 10000)

    for i in range(height):
        for j in range(width):
            # Adjust the noise coordinates by the randomized base offsets
            altitude = pnoise2((i + base_x) * scale, (j + base_y) * scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=width, repeaty=height)
            # Scale noise output to altitude range
            scaled_altitude = min_alt + (max_alt - min_alt) * (altitude + 1) / 2
            height_map[i, j] = scaled_altitude

    # Adjust sea level based on the desired sea percentage
    sea_level = np.percentile(height_map, sea_percentage * 100)
    # Normalize height map so that the calculated sea level is at 0
    height_map -= sea_level

    return height_map, sea_level


def generate_temperature_map(height_map, latitude_factor):
    """Generate temperature maps for each season affected by latitude and altitude."""
    temp_maps = {}
    lat_range = np.linspace(NORTH_TEMPERATURE, SOUTH_TEMPERATURE, height_map.shape[0])
    for season, temp_shift in [('winter', -15), ('spring', 0), ('summer', 15), ('fall', 0)]:
        temp_map = lat_range[:, np.newaxis] + temp_shift - 0.005 * height_map  # Decrease 0.5°C per 100m
        # Round the temperatures to one decimal place
        temp_map = np.round(temp_map, 1)
        temp_maps[season] = temp_map

    return temp_maps


def generate_water_features(width, height, scale, water_type):
    """Generate a noise map for water features."""
    water_map = np.zeros((height, width))
    base_x = int(time.time()) % 1000  # Changing base offsets dynamically
    base_y = int(time.time()) % 1000  # Based on the current time

    for i in range(height):
        for j in range(width):
            noise_val = pnoise2((i + base_x) * scale, (j + base_y) * scale, octaves=6)
            water_map[i, j] = noise_val
    return water_map

def generate_water_presence_map(height_map, sea_level=0):
    """Generate a map of water presence as a percentage based on altitude and additional features."""
    width, height = height_map.shape
    water_presence_map = np.zeros_like(height_map)

    lake_map = generate_water_features(width, height, scale=0.05, water_type='lake')
    river_map = generate_water_features(width, height, scale=0.02, water_type='river')
    
    # Basic water presence from altitude
    water_presence_map[height_map <= sea_level] = 100  # Sea
    water_presence_map[(height_map > sea_level) & (height_map <= sea_level + 50)] = 80  # Near shore, potential for rivers
    water_presence_map[(height_map > sea_level + 50) & (height_map <= sea_level + 100)] = 95  # Potential for swamps

    # Apply river map
    river_threshold = 0.15  # Threshold for river presence
    water_presence_map[(river_map > river_threshold) & (height_map > sea_level) & (height_map <= sea_level + 100)] = 80

    # Apply lake map
    lake_threshold = 0.25  # Threshold for lake presence
    water_presence_map[(lake_map > lake_threshold) & (height_map > sea_level) & (height_map <= sea_level + 100)] = 100

    # Valleys and desert conditions
    desert_map = np.random.rand(height, width)  # Random distribution for desert
    valley_threshold = 0.9  # 85% valleys, 15% desert
    desert_threshold = valley_threshold + 0.1

    water_presence_map[(height_map > sea_level ) & (desert_map <= valley_threshold)] = np.random.randint(15, 26)  # Valley with some water presence
    water_presence_map[(height_map > sea_level + 2300) & (desert_map > valley_threshold*.8)] = np.random.randint(5, 16)  # Desert with low water presence

    return water_presence_map


def generate_light_map(latitude_factor):
    """Generate light levels for each season, considering latitude."""
    light_maps = {}
    for season, light_hours in [('winter', 8), ('spring', 12), ('summer', 16), ('fall', 12)]:
        # Simulate longer days in the north during summer and shorter during winter
        light_map = np.full((HEIGHT, WIDTH), light_hours)
        light_maps[season] = light_map
    return light_maps

def generate_comprehensive_map():
    """Generate a comprehensive map with all required properties."""
    #base_map = generate_base_map(WIDTH, HEIGHT)
    height_map, sea_level = generate_height_map(WIDTH, HEIGHT)
    print("Sea level altitude:", sea_level)
    temperature_maps = generate_temperature_map(height_map, latitude_factor=0.5)
    water_presence_map = generate_water_presence_map(height_map)
    light_maps = generate_light_map(latitude_factor=0.5)
    
    return {
        'height': height_map,
        'temperature': temperature_maps,
        'water_presence': water_presence_map,
        'light': light_maps
    }



def get_terrain_info(comprehensive_map, x, y):
    """Retrieve and print detailed information for a specific coordinate."""
    info = {
        'Height': comprehensive_map['height'][y, x],
        'Water Presence': f"{comprehensive_map['water_presence'][y, x]}%",
        'Light Levels': {season: comprehensive_map['light'][season][y, x] for season in comprehensive_map['light']},
        'Temperature': {season: comprehensive_map['temperature'][season][y, x] for season in comprehensive_map['temperature']}
    }
    return info

def save_detailed_map(comprehensive_map, file_path="detailed_map.txt"):
    """Save detailed map information to a file."""
    with open(file_path, "w") as file:
        for i in range(comprehensive_map['height'].shape[0]):
            for j in range(comprehensive_map['height'].shape[1]):
                file.write(f"{i},{j},Height:{comprehensive_map['height'][i, j]},")
                file.write(f"Water:{comprehensive_map['water_presence'][i, j]}%,")
                file.write(','.join([f"{season} Temp:{comprehensive_map['temperature'][season][i, j]}" for season in comprehensive_map['temperature']]))
                file.write(','.join([f"{season} Light:{comprehensive_map['light'][season][i, j]}" for season in comprehensive_map['light']]))
                file.write('\n')

def plot_maps(comprehensive_map):
    """Plot all layers of the map including the water presence map with percentages."""
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))  # Setting up a 1x3 grid of plots

    # Plotting the height map
    im = axs[0].imshow(comprehensive_map['height'], cmap='terrain')
    axs[0].set_title('Height Map')
    fig.colorbar(im, ax=axs[0], fraction=0.046, pad=0.04)  # Add a colorbar to the height map

    # Plotting the water presence map as percentages
    im = axs[1].imshow(comprehensive_map['water_presence'], cmap='Blues', vmin=0, vmax=100)
    axs[1].set_title('Water Presence Map (%)')
    cbar = fig.colorbar(im, ax=axs[1], fraction=0.046, pad=0.04)
    cbar.set_label('% Water Presence')  # Label the colorbar

    # Additional plot (for example, a temperature map or another feature)
    # This is a placeholder for any additional data you might want to plot
    im = axs[2].imshow(comprehensive_map['temperature']['summer'], cmap='coolwarm')
    axs[2].set_title('Summer Temperature Map')
    fig.colorbar(im, ax=axs[2], fraction=0.046, pad=0.04)

    plt.tight_layout()  # Adjust the layout to make room for all plot elements
    plt.show()

# Assuming comprehensive_map has been populated with necessary data
# comprehensive_map = {
#     'height': height_map,
#     'water_presence': water_presence_map,
#     'temperature': {
#         'summer': summer_temp_map,
#         # Add other seasons if needed
#     }
# }
# plot_maps(comprehensive_map)

'''


def get_terrain_info(terrain_values, world_map, x, y):
    if x < 0 or y < 0 or x >= terrain_values.shape[1] or y >= terrain_values.shape[0]:
        return "Invalid coordinates"
    terrain_type = terrain_values[y, x]
    altitude = world_map[y, x]
    if terrain_type == -1:
        terrain_desc = "Sea"
    elif terrain_type == 0:
        terrain_desc = "Freshwater"
    else:
        terrain_desc = "Land"
    return f"Terrain: {terrain_desc}, Altitude: {altitude:.2f}"

def generate_map(width, height, scale=0.05, octaves=6, persistence=0.5, lacunarity=2.0, min_alt=-1000, max_alt=5000):
    world_map = np.zeros((height, width))
    for i in range(height):
        for j in range(width):
            altitude = pnoise2(i * scale, j * scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=width, repeaty=height, base=0)
            # Scale the Perlin noise output to the desired altitude range
            scaled_altitude = min_alt + (max_alt - min_alt) * (altitude + 1) / 2
            world_map[i][j] = scaled_altitude
    return world_map


def save_detailed_map(terrain_values, world_map, file_path="detailed_map.txt"):
    height, width = terrain_values.shape
    with open(file_path, "w") as file:
        for i in range(height):
            for j in range(width):
                terrain_type = terrain_values[i, j]
                altitude = world_map[i, j]
                if terrain_type == -1:
                    terrain_desc = "Sea"
                elif terrain_type == 0:
                    terrain_desc = "Freshwater"
                else:
                    terrain_desc = "Land"
                file.write(f"{i},{j},{terrain_desc},{altitude:.2f}\n")
'''