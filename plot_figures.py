import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import lines, font_manager
from matplotlib.dates import YearLocator, DateFormatter

# Add Helvetica font
font_path = '/System/Library/Fonts/Helvetica.ttc'  # Adjust this path if necessary
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Helvetica'

def plot_practice_sizes(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Countries to plot
    countries = ['Poland', 'Portugal', 'Germany', 'European average']

    # Select relevant columns and rows
    plot_df = df[df['Country'].isin(countries)].set_index('Country')
    plot_df = plot_df.reindex(countries)

    # Group 11+ staff into one category
    plot_df['11+ staff'] = plot_df.iloc[:, 4:-1].sum(axis=1)
    plot_df = plot_df[['1 staff', '2 staff', '3-5 staff', '6-10 staff', '11+ staff']]

    # Calculate percentages
    plot_df_pct = plot_df.div(plot_df.sum(axis=1), axis=0) * 100

    # Set up the plot
    fig, ax = plt.subplots(figsize=(6.69, 4))  # 6.69 inches wide, 4 inches high

    # Create a color map
    colors = plt.cm.viridis(np.linspace(0, 1, len(plot_df.columns)))

    # Create grouped bar chart
    bar_width = 0.15
    index = np.arange(len(countries))

    # Add grid
    ax.grid(axis='y', color='#A8BAC4', linestyle='-', linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    for i, column in enumerate(plot_df_pct.columns):
        bars = ax.bar(index + i * bar_width, plot_df_pct[column], bar_width, color=colors[i], label=None)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=6)

    # Customize the plot
    plt.xticks(index + bar_width * 2, countries)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5, labels=plot_df.columns)

    # Add percentage labels to y-axis
    ax.set_yticks(range(0, 81, 10))
    ax.set_yticklabels([f'{i}%' for i in range(0, 81, 10)])

    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Adjust layout
    plt.tight_layout()

    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_wage_evolution(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Prepare the data
    df['Date'] = pd.to_datetime(df['Date'], format='%Y')
    categories = ['Minimal wage', 'Median wage', 'Lower quartile architect', 'Median architect']
    colors = ['#A8BAC4', '#A8BAC4', '#076FA1', '#E3120B']

    # Set up the plot
    fig, ax = plt.subplots(figsize=(6.69, 4))  # 6.69 inches wide, 4 inches high
    
    # Plot lines
    for category, color in zip(categories, colors):
        data = df[df['Quartile'] == category]
        ax.plot(data['Date'], data['Monthly earnings'], color=color, lw=3)
        
        # Add dots
        ax.scatter(data['Date'], data['Monthly earnings'], color=color, s=60, zorder=10, edgecolors='white')

    # Customize x-axis
    ax.xaxis.set_major_locator(YearLocator(2))
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))

    # Customize y-axis
    ax.set_ylim(0, 2100)
    ax.yaxis.set_major_locator(plt.MultipleLocator(500))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
    ax.tick_params(axis='y', which='both', length=0)  # Remove tick marks
    ax.yaxis.set_tick_params(labelleft=True)  # Ensure labels are shown

    # Add grid
    ax.grid(axis='y', color='#A8BAC4', linestyle='-', linewidth=0.5, zorder=0)

    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Set bottom spine width and capstyle
    ax.spines["bottom"].set_lw(1.2)
    ax.spines["bottom"].set_capstyle("butt")

    # Add labels for each line
    for category, color in zip(categories, colors):
        data = df[df['Quartile'] == category]
        last_point = data.iloc[-1]
        x = last_point['Date']
        y = last_point['Monthly earnings']
        
        # Calculate angle of the line at the end point
        if len(data) > 1:
            prev_point = data.iloc[-2]
            dx = (x - prev_point['Date']).days
            dy = y - prev_point['Monthly earnings']
            angle = np.degrees(np.arctan2(dy, dx))
        else:
            angle = 0
        
        # Adjust text position and rotation
        ax.annotate(category, 
                    xy=(x, y),
                    xytext=(0, 15), 
                    textcoords='offset points',
                    color=color,
                    fontsize=10,
                    fontweight='bold',
                    va='top',
                    ha='right',
                    rotation=angle)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()

def plot_fee_structures(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Countries to plot
    countries = ['Poland', 'Portugal', 'Germany', 'European average']

    # Select relevant columns and rows
    plot_df = df[df['Country'].isin(countries)].set_index('Country')
    plot_df = plot_df.reindex(countries)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(6.69, 4))  # 6.69 inches wide, 4 inches high

    # Create a color map
    colors = plt.cm.viridis(np.linspace(0, 1, len(plot_df.columns)))

    # Create grouped bar chart
    bar_width = 0.15
    index = np.arange(len(countries))

    # Add grid
    ax.grid(axis='y', color='#A8BAC4', linestyle='-', linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    for i, column in enumerate(plot_df.columns):
        bars = ax.bar(index + i * bar_width, plot_df[column], bar_width, color=colors[i], label=None)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                    f'{height}', ha='center', va='bottom', fontsize=8)

    # Customize the plot
    plt.title('Fee Structures in Architectural Practices', fontsize=14, fontweight='bold')
    plt.xticks(index + bar_width * 2, countries, rotation=0, ha='center')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, labels=plot_df.columns)

    # Add percentage labels to y-axis
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels([f'{i}%' for i in range(0, 101, 10)])

    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Adjust layout
    plt.tight_layout()

    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()

# Example usage
if __name__ == "__main__":
    #plot_practice_sizes('data/ACE/number_size_of_practices.csv', 'img/architectural_practices_by_country_grouped_bar.png')
    #plot_wage_evolution('data/Median monthly earnings of architects in Poland.csv', 'img/wage_evolution_poland.png')
    plot_fee_structures('data/ACE/fee_structures.csv', 'img/fee_structures_by_country_grouped_bar.png')
