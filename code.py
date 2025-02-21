import time
import board
import terminalio
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_display_shapes.rect import Rect

# API URL defined directly here (include your API key if needed)
DATA_URL = "https://api.diadata.org/v1/assetQuotation/Alephium/tgx7VNFoP9DJiFMFgXXtafQZkUvyEdDHT9ryamHJYrjq"

# Debug flag for dot printouts (set to False to suppress all dot debug messages)
DEBUG_DOTS = False

# Set to False by default to use live data
USE_TEST_DATA = False

# Define test data: 56 dictionaries with a mix of volatile and less volatile price fluctuations.
test_data = [
    {"Price": 0.9000, "PriceYesterday": 0.9500},
    {"Price": 0.9200, "PriceYesterday": 0.9500},
    {"Price": 0.9100, "PriceYesterday": 0.9500},
    {"Price": 0.9300, "PriceYesterday": 0.9500},
    {"Price": 0.9400, "PriceYesterday": 0.9500},
    {"Price": 0.9500, "PriceYesterday": 0.9500},
    {"Price": 0.9600, "PriceYesterday": 0.9500},
    {"Price": 0.9800, "PriceYesterday": 0.9500},
    {"Price": 1.0000, "PriceYesterday": 0.9500},
    {"Price": 1.0200, "PriceYesterday": 0.9500},
    {"Price": 1.1000, "PriceYesterday": 0.9500},
    {"Price": 0.8700, "PriceYesterday": 0.9500},
    {"Price": 1.1200, "PriceYesterday": 0.9500},
    {"Price": 1.0300, "PriceYesterday": 0.9500},
    {"Price": 0.8800, "PriceYesterday": 0.9500},
    {"Price": 1.1500, "PriceYesterday": 0.9500},
    {"Price": 1.1700, "PriceYesterday": 0.9500},
    {"Price": 1.0000, "PriceYesterday": 0.9500},
    {"Price": 0.8900, "PriceYesterday": 0.9500},
    {"Price": 1.1800, "PriceYesterday": 0.9500},
    {"Price": 1.2200, "PriceYesterday": 0.9500},
    {"Price": 0.8600, "PriceYesterday": 0.9500},
    {"Price": 1.0800, "PriceYesterday": 0.9500},
    {"Price": 0.9400, "PriceYesterday": 0.9500},
    {"Price": 1.1300, "PriceYesterday": 0.9500},
    {"Price": 0.9600, "PriceYesterday": 0.9500},
    {"Price": 1.1600, "PriceYesterday": 0.9500},
    {"Price": 1.0000, "PriceYesterday": 0.9500},
    {"Price": 0.9000, "PriceYesterday": 0.9500},
    {"Price": 1.1900, "PriceYesterday": 0.9500},
    {"Price": 0.8800, "PriceYesterday": 0.9500},
    {"Price": 1.1400, "PriceYesterday": 0.9500},
    {"Price": 1.0500, "PriceYesterday": 0.9500},
    {"Price": 0.9300, "PriceYesterday": 0.9500},
    {"Price": 1.2100, "PriceYesterday": 0.9500},
    {"Price": 1.1000, "PriceYesterday": 0.9500},
    {"Price": 0.8700, "PriceYesterday": 0.9500},
    {"Price": 1.0900, "PriceYesterday": 0.9500},
    {"Price": 1.0300, "PriceYesterday": 0.9500},
    {"Price": 0.9100, "PriceYesterday": 0.9500},
    {"Price": 1.1200, "PriceYesterday": 0.9500},
    {"Price": 1.0000, "PriceYesterday": 0.9500},
    {"Price": 0.9400, "PriceYesterday": 0.9500},
    {"Price": 1.1500, "PriceYesterday": 0.9500},
    {"Price": 0.9700, "PriceYesterday": 0.9500},
    {"Price": 1.2000, "PriceYesterday": 0.9500},
    {"Price": 1.0200, "PriceYesterday": 0.9500},
    {"Price": 0.8900, "PriceYesterday": 0.9500},
    {"Price": 1.1700, "PriceYesterday": 0.9500},
    {"Price": 1.0800, "PriceYesterday": 0.9500},
    {"Price": 0.9000, "PriceYesterday": 0.9500},
    {"Price": 1.1000, "PriceYesterday": 0.9500},
    {"Price": 0.9500, "PriceYesterday": 0.9500},
    {"Price": 1.0500, "PriceYesterday": 0.9500},
    {"Price": 0.9200, "PriceYesterday": 0.9500},
    {"Price": 1.1800, "PriceYesterday": 0.9500},
    {"Price": 1.0000, "PriceYesterday": 0.9500}
]
test_index = 0

# Initialize MatrixPortal.
matrixportal = MatrixPortal()

# Create a border covering the display.
border = Rect(
    0,
    0,
    matrixportal.graphics.display.width,
    matrixportal.graphics.display.height,
    outline=0x0000FF,  # neutral blue
    stroke=1
)
matrixportal.graphics.splash.insert(0, border)

# Add a text area for the price.
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(10, 16),
    text_scale=1,
    text_color=0x0000FF,  # neutral blue
    scrolling=False,
)

# Create a display group for the dots.
dots_group = displayio.Group()
matrixportal.graphics.splash.append(dots_group)

# Maintain up to 56 historical prices.
price_history = []

if USE_TEST_DATA:
    price_history = [d["Price"] for d in test_data]
    print("Pre-populated price history:", price_history)

def weighted_average(prices):
    n = len(prices)
    total_weight = 0
    weighted_sum = 0
    for i, price in enumerate(prices):
        weight = (n - i)
        weighted_sum += price * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight else 0

def get_dot_color(current_price, previous_price):
    if previous_price is None or previous_price == 0:
        return 0x0000FF
    pct = (current_price - previous_price) / previous_price
    # For positive changes: cyan if 0% < change < 1%, green if ≥ 1%
    if pct > 0:
        if pct < 0.01:
            return 0x00FFFF  # cyan
        else:
            return 0x00FF00  # green
    # For negative changes: purple if -1% < change < 0%, red if ≤ -1%
    elif pct < 0:
        if pct > -0.01:
            return 0x800080  # purple
        else:
            return 0xFF0000  # red
    else:
        return 0x0000FF

def compute_color(reference_price, new_price, cap=0.05):
    if reference_price == 0:
        return 0x0000FF
    pct = (new_price - reference_price) / reference_price
    if pct > 0:
        t = min(pct / cap, 1.0)
        r = 0
        g = int(255 * t)
        b = int(255 * (1 - t))
    elif pct < 0:
        t = min(abs(pct) / cap, 1.0)
        r = int(255 * t)
        g = 0
        b = int(255 * (1 - t))
    else:
        return 0x0000FF
    return (r << 16) | (g << 8) | b

while True:
    try:
        print("Fetching asset data...")
        if USE_TEST_DATA:
            data = test_data[test_index]
            print("Using test JSON:", data)
            test_index = (test_index + 1) % len(test_data)
        else:
            response = matrixportal.network.fetch(DATA_URL)
            data = response.json()

        new_price = data.get("Price")
        price_yesterday = data.get("PriceYesterday")

        if new_price is not None and price_yesterday is not None:
            print("New Price: {:.4f}".format(new_price))
            print("Yesterday's Price: {:.4f}".format(price_yesterday))

            price_history.append(new_price)
            if len(price_history) > 56:
                removed = price_history.pop(0)
                print("Removed oldest price:", removed)

            border_color = compute_color(price_yesterday, new_price, cap=0.02)
            print("Border color (compared to yesterday):", hex(border_color))

            weighted_avg = weighted_average(price_history)
            if new_price == weighted_avg:
                text_color = 0x0000FF
                print("New price equals weighted average; using blue for text.")
            else:
                text_color = compute_color(weighted_avg, new_price, cap=0.01)
                pct_weighted = ((new_price - weighted_avg) / weighted_avg) * 100 if weighted_avg != 0 else 0
                print("Weighted average of historical prices: {:.4f}".format(weighted_avg))
                print("Percent change from weighted average: {:.2f}%".format(pct_weighted))
            print("Text color (compared to weighted average):", hex(text_color))

            border.outline = border_color
            matrixportal.set_text_color(text_color, 0)
            price_text = "{:.4f}".format(new_price)
            matrixportal.set_text(price_text, 0)
            print("Displayed Price:", price_text)

            while len(dots_group) > 0:
                dots_group.pop()

            if len(price_history) > 0:
                num_dots = len(price_history)
                display_width = matrixportal.graphics.display.width
                margin = 2
                available_width = display_width - (2 * margin)
                start_x = margin + (available_width - num_dots) // 2
                dot_y = 28
                for i, hist_price in enumerate(price_history):
                    if i == 0:
                        dot_color = 0x0000FF
                        dot = Rect(start_x + i, dot_y, 1, 1, fill=dot_color)
                        dots_group.append(dot)
                        if DEBUG_DOTS:
                            print("Dot {}: Price {:.4f}, Color {}".format(i, hist_price, hex(dot_color)))
                    else:
                        pct = (price_history[i] - price_history[i - 1]) / price_history[i - 1]
                        if pct >= 0.05:
                            dot = Rect(start_x + i, dot_y - 1, 1, 1, fill=0x00FF00)
                            dots_group.append(dot)
                            if DEBUG_DOTS:
                                print("Extra green dot at index {} (increase {:.2f}%)".format(i, pct * 100))
                        elif pct <= -0.05:
                            dot = Rect(start_x + i, dot_y + 1, 1, 1, fill=0xFF0000)
                            dots_group.append(dot)
                            if DEBUG_DOTS:
                                print("Extra red dot at index {} (decrease {:.2f}%)".format(i, pct * 100))
                        else:
                            dot_color = get_dot_color(price_history[i], price_history[i - 1])
                            dot = Rect(start_x + i, dot_y, 1, 1, fill=dot_color)
                            dots_group.append(dot)
                            if DEBUG_DOTS:
                                print("Dot {}: Price {:.4f}, Base Color {}".format(i, hist_price, hex(dot_color)))
            else:
                if DEBUG_DOTS:
                    print("No historical data for dots.")
        else:
            print("Missing price or yesterday's price data.")
            matrixportal.set_text("N/A", 0)
    except Exception as e:
        print("Error fetching data:", e)
        matrixportal.set_text("Fetch Error", 0)

    print("Waiting 30 seconds before next fetch...\n")
    time.sleep(30)
