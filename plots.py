import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # Added for formatting y-axis ticks
import matplotlib.colors as mcolors # Added for RGBA conversion
from matplotlib.ticker import FuncFormatter # Added for y-axis formatting
import pandas as pd
import numpy as np
from scipy.stats import linregress
import scipy.stats as st # Added for jitter calculation
import os # Added for creating output directory

# --- Configuration ---
OUTPUT_DIR = "img"
POZNAN_AVG = 11845
CSD_AVG_PRICE_PER_SQM = 9870
FONT_NAME = 'Inter' # Make sure 'Inter' font is installed on your system

# --- Consistent X-Axis Range for Both Plots ---
# Use the wider range needed for the violin plot context
COMMON_X_MIN = 25
COMMON_X_MAX = 185
COMMON_X_PADDING = 5 # Padding for limits

# Filters for specific plot elements (if needed, though less critical now with common axis)
# FILTER_MIN_SIZE = 25 # For violin plot elements
# FILTER_MAX_SIZE = 200 # For violin plot elements
SCATTER_AREA_MIN = 25  # Still useful for filtering points displayed if desired
SCATTER_AREA_MAX = 185 # Still useful for filtering points displayed if desired
BENCHMARK_SIZE = 100 # For violin plot benchmark line

# --- Aesthetic Choices ---
VIRIDIS_CMAP = sns.color_palette('viridis', as_cmap=True)

# Core Palette
CSD_COLOR = VIRIDIS_CMAP(0.01)       # Dark blue/purple end
KOLEJOVA_COLOR = VIRIDIS_CMAP(0.99)    # Yellow end
VIOLIN_BODY_COLOR = '#EEEEEE'
MARKET_SCATTER_COLOR_ALPHA = mcolors.to_rgba('#BDBDBD', alpha=0.3) # Light gray background points
AVG_REF_COLOR = '#AAAAAA'             # Medium-light gray for average line

# Marker Styling (Consistent)
CSD_EDGE_COLOR = CSD_COLOR
CSD_FACE_COLOR_RGBA = mcolors.to_rgba(CSD_COLOR, alpha=0.8)
KOLEJOVA_EDGE_COLOR = KOLEJOVA_COLOR
KOLEJOVA_FACE_COLOR_RGBA = mcolors.to_rgba(KOLEJOVA_COLOR, alpha=0.8)

# General Styling
TEXT_COLOR_MUTED = '#666666' # Muted gray for axes/ticks
GRID_COLOR_FAINT = '#EEEEEE' # Very light grid
TEXT_COLOR_DARK = '#333333' # Darker text for annotations if needed


# --- Load and Prepare Data ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
try:
    okna_bej = pd.read_csv('/Users/michaldeja/Library/CloudStorage/OneDrive-Personal/Documents/Politechnika Gdańska/Magister/Dyplom/08_market_data/OKNABEJ_mieszkanka_mega.csv')
    # Clean data slightly - remove potential outliers or missing values needed for plot 2
    okna_bej = okna_bej.dropna(subset=['area', 'price'])
    okna_bej = okna_bej[(okna_bej['area'] > 10) & (okna_bej['price'] > 10000)] # Basic sanity check
except FileNotFoundError:
    print("Error: Main data file not found. Please check the path.")
    exit()
except KeyError as e:
    print(f"Error: Missing expected column in CSV: {e}")
    exit()


price_ours = [562590, 621810, 700770, 809340, 1302840, 1460760, 1825950]
area_ours = [57, 63, 71, 82, 132, 148, 185]
csd_df = pd.DataFrame({'area': area_ours, 'price': price_ours})

poznan = okna_bej[okna_bej['city'] == 'Poznań'].copy()
kolejova = poznan[poznan['investment'] == 'Kolejova 1'].copy()
# Ensure Kolejova data is valid for regression
kolejova = kolejova.dropna(subset=['area', 'price'])
kolejova = kolejova[kolejova['area'] > 0]


# --- Plot Styling Function ---
def apply_elegant_style(bottom_spine=True): # Added arg to control bottom spine
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'sans-serif'
    try:
        plt.rcParams['font.sans-serif'] = FONT_NAME
        # print(f"Using font: {FONT_NAME}") # Optional: uncomment for debug
    except Exception as e:
        print(f"Warning: Font '{FONT_NAME}' not found or not registered. Using default. Error: {e}")
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR_MUTED
    plt.rcParams['xtick.color'] = TEXT_COLOR_MUTED
    plt.rcParams['ytick.color'] = TEXT_COLOR_MUTED
    plt.rcParams['text.color'] = TEXT_COLOR_DARK
    plt.rcParams['axes.edgecolor'] = TEXT_COLOR_MUTED
    plt.rcParams['grid.color'] = GRID_COLOR_FAINT
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.6

    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.left'] = True
    plt.rcParams['axes.spines.bottom'] = bottom_spine # Control bottom spine visibility

# --- Y-axis Formatter ---
def millions_formatter(x, pos):
    return f'{x / 1e6:.1f}M'
formatter = FuncFormatter(millions_formatter)

# --- X-axis Formatting Function (for consistency) ---
def format_xaxis(ax):
    ax.set_xlabel("Apartment Size (m²)", fontsize=11, labelpad=10, color=TEXT_COLOR_MUTED)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(25))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(5))
    ax.tick_params(axis='x', which='major', length=4, direction='out', color=TEXT_COLOR_MUTED, labelsize=9)
    ax.tick_params(axis='x', which='minor', length=2, direction='out', color=TEXT_COLOR_MUTED)
    ax.set_xlim(COMMON_X_MIN - COMMON_X_PADDING, COMMON_X_MAX + COMMON_X_PADDING)
    ax.grid(True, axis='x', color=GRID_COLOR_FAINT, linestyle='--', linewidth=0.6, zorder=0)
    ax.grid(False, axis='y')


# --- Plot 1: Horizontal Violin Plot with Jittered Kolejova Points ---
apply_elegant_style(bottom_spine=False) # Remove bottom spine for this plot
print("Generating Horizontal Violin Plot with Kolejova points...")

# Filter data for plot range
poznan_filtered_v = poznan[(poznan['area'] >= COMMON_X_MIN) & (poznan['area'] <= COMMON_X_MAX)].copy()
csd_sizes_filtered_v = sorted([s for s in area_ours if COMMON_X_MIN <= s <= COMMON_X_MAX])
kolejova_filtered_v = kolejova[(kolejova['area'] >= COMMON_X_MIN) & (kolejova['area'] <= COMMON_X_MAX)].copy()

print(f"Filtered Poznan market data: {len(poznan_filtered_v)}")
print(f"Filtered CSD data: {len(csd_sizes_filtered_v)}")
print(f"Filtered Kolejova data: {len(kolejova_filtered_v)}")

fig1, ax1 = plt.subplots(figsize=(12, 5)) # Keep aspect ratio appropriate for horizontal violin

# 1. Violin Plot
sns.violinplot(x='area', data=poznan_filtered_v, color=VIOLIN_BODY_COLOR, inner=None, linewidth=1.0, scale='width', ax=ax1, saturation=1, zorder=1)

# 2. Vertical Benchmark Line
ax1.axvline(BENCHMARK_SIZE, color='#cccccc', linestyle='--', linewidth=1.0, label=f'{BENCHMARK_SIZE} m\u00B2 Family Benchmark', zorder=2)

# 3. Kolejova Jittered Points
y_base = 0 # Center line y-coordinate
jitter_scale = 0.04 # How much to jitter vertically
kolejova_y_jittered = y_base + st.t(df=6, scale=jitter_scale).rvs(len(kolejova_filtered_v))
ax1.scatter(kolejova_filtered_v['area'], kolejova_y_jittered,
            marker='o', s=35, # Smaller size for background points
            facecolor=KOLEJOVA_FACE_COLOR_RGBA,
            edgecolor=KOLEJOVA_EDGE_COLOR,
            linewidth=0.8,
            label='Kolejova 1 Units', zorder=3, alpha=0.8) # Added slight alpha overall

# 4. CSD Markers (on center line)
ax1.plot(csd_sizes_filtered_v, [y_base] * len(csd_sizes_filtered_v),
         'o', markersize=9,
         markerfacecolor=CSD_FACE_COLOR_RGBA, # Use consistent CSD color
         markeredgecolor=CSD_EDGE_COLOR,    # Use consistent CSD color
         markeredgewidth=1.0,
         label='Proposed CSD Units', clip_on=False, zorder=4) # Higher zorder

# 5. Labels for CSD Units (below markers)
label_y_offset_v = -0.04
for area_val_v in csd_sizes_filtered_v:
    ax1.text(area_val_v, y_base + label_y_offset_v, f"{area_val_v} m\u00B2", ha='center', va='top', fontsize=8, color=TEXT_COLOR_DARK, fontweight='normal', zorder=5) # Ensure labels are on top

# --- Customize Violin Plot Appearance ---
format_xaxis(ax1) # Apply consistent X-axis formatting
ax1.set_ylabel("Market Distribution", fontsize=11, labelpad=10, color=TEXT_COLOR_MUTED) # No conceptual Y label for violin density
ax1.set_yticks([])
ax1.legend(loc='upper right', ncol=1, fontsize=9, frameon=False)

plt.tight_layout()

violin_plot_path = os.path.join(OUTPUT_DIR, "violin_plot_apartment_sizes_with_kolejova.png") # New name
fig1.savefig(violin_plot_path, dpi=300, bbox_inches='tight')
print(f"Aligned violin plot saved to {violin_plot_path}")
plt.close(fig1)


# --- Plot 2: Scatter Plot Price vs Area (Large Apartments) ---
apply_elegant_style(bottom_spine=False) # Use bottom spine for scatter
print("Generating Scatter Plot (Large Apartments)...")

# Filter data for scatter plot points
poznan_large = poznan[(poznan['area'] >= SCATTER_AREA_MIN) & (poznan['area'] <= SCATTER_AREA_MAX)].copy()
kolejova_large = kolejova[(kolejova['area'] >= SCATTER_AREA_MIN) & (kolejova['area'] <= SCATTER_AREA_MAX)].copy()
csd_large = csd_df[(csd_df['area'] >= SCATTER_AREA_MIN) & (csd_df['area'] <= SCATTER_AREA_MAX)].copy()

print(f"Filtered Poznan market points for scatter: {len(poznan_large)}")
print(f"Filtered Kolejova 1 points for scatter: {len(kolejova_large)}")
print(f"Filtered CSD points for scatter: {len(csd_large)}")

fig2, ax2 = plt.subplots(figsize=(8, 8))

# Calculate Lines (Kolejova regression uses FULL dataset)
x_ref = np.array([SCATTER_AREA_MIN, SCATTER_AREA_MAX])
y_ref_avg = POZNAN_AVG * x_ref
y_ref_csd = CSD_AVG_PRICE_PER_SQM * x_ref

if len(kolejova) >= 2:
    kolejova_slope_full, kolejova_intercept_full, kolejova_r_value_full, _, _ = linregress(kolejova['area'], kolejova['price'])
    y_reg_kolejova_full = kolejova_slope_full * x_ref + kolejova_intercept_full
    kolejova_label = f'Kolejova 1 Trend (Full Data R²={kolejova_r_value_full**2:.2f})'
    print(f"Kolejova Regression (Full Data): Slope={kolejova_slope_full:.2f}, R²={kolejova_r_value_full**2:.2f}")
else:
    print("Not enough Kolejova data points in the full dataset for regression.")
    y_reg_kolejova_full = None
    kolejova_label = 'Kolejova 1 Trend (N/A)'

# --- Plot Scatter Elements ---
# 1. Background Market Points
ax2.scatter(poznan_large['area'], poznan_large['price'], color=MARKET_SCATTER_COLOR_ALPHA, s=20, label='_nolegend_', zorder=1, edgecolors='none')

# 2. Lines
ax2.plot(x_ref, y_ref_avg, color=AVG_REF_COLOR, linestyle='--', linewidth=1.0, label=f'Poznań Avg. ({POZNAN_AVG:,} PLN/m²)'.replace(',', ' '), zorder=2)
ax2.plot(x_ref, y_ref_csd, color=CSD_COLOR, linestyle=':', linewidth=1.5, label=f'Proposed CSD ({CSD_AVG_PRICE_PER_SQM:,} PLN/m²)'.replace(',', ' '), zorder=3) # Use CSD_COLOR
if y_reg_kolejova_full is not None:
    ax2.plot(x_ref, y_reg_kolejova_full, color=KOLEJOVA_COLOR, linestyle='-.', linewidth=1.5, label=kolejova_label, zorder=3) # Use KOLEJOVA_COLOR
ax2.axvline(BENCHMARK_SIZE, color='#cccccc', linestyle='--', linewidth=1.0, label=f'{BENCHMARK_SIZE} m\u00B2 Family Benchmark', zorder=2)

# 3. Highlighted Dots (Styled)
# Kolejova Dots
ax2.scatter(kolejova_large['area'], kolejova_large['price'], marker='o', s=70,
            facecolor=KOLEJOVA_FACE_COLOR_RGBA, edgecolor=KOLEJOVA_EDGE_COLOR,
            linewidth=1.0, label='Kolejova 1 Units', zorder=4)
# CSD Dots
ax2.scatter(csd_large['area'], csd_large['price'], marker='o', s=90,
            facecolor=CSD_FACE_COLOR_RGBA, edgecolor=CSD_EDGE_COLOR,
            linewidth=1.0, label='Proposed CSD Units', zorder=5)

# --- Customize Scatter Plot Appearance ---
format_xaxis(ax2) # Apply consistent X-axis formatting
ax2.set_ylabel("Total Price (PLN)", fontsize=11, labelpad=10, color=TEXT_COLOR_MUTED)
ax2.yaxis.set_major_formatter(formatter)
ax2.set_xlim(SCATTER_AREA_MIN - 5, SCATTER_AREA_MAX + 5)
min_price_filtered = min(poznan_large['price'].min(), csd_large['price'].min(), kolejova_large['price'].min() if not kolejova_large.empty else np.inf)
max_price_filtered = max(poznan_large['price'].max(), csd_large['price'].max(), kolejova_large['price'].max() if not kolejova_large.empty else -np.inf)
ax2.set_ylim(bottom=0, top=max_price_filtered * 1.1)
ax2.tick_params(axis='both', which='major', labelsize=9, color=TEXT_COLOR_MUTED)
ax2.legend(loc='upper left', fontsize=9, frameon=False)
ax2.grid(True, axis='both', color=GRID_COLOR_FAINT, linestyle='--', linewidth=0.6, zorder=0)

plt.tight_layout()

# --- Save the figure ---
scatter_plot_path = os.path.join(OUTPUT_DIR, "scatter_plot_price_area_large_v3.png") # New filename
fig2.savefig(scatter_plot_path, dpi=300, bbox_inches='tight')
print(f"Large apartment scatter plot v3 saved to {scatter_plot_path}")
plt.close(fig2)


# --- Add code for subsequent plots below ---
# print("Generating Kolejova Comparison Plot...")
# ... kolejova comparison plot code ...


print("Script finished.")







