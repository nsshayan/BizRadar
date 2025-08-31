# BizRadar - Business Monitoring Application

BizRadar helps business owners track their local competitive landscape in real-time using the Foursquare Places API.

## Features

- **Competitor Monitoring**: Automatically monitor competitors within a configurable radius
- **Real-time Notifications**: Get alerts when new businesses open nearby or existing ones show trending activity
- **Data-driven Insights**: Receive personalized recommendations based on local market analysis
- **Comprehensive Dashboard**: View competitor information including business type, ratings, hours, and recent activity

## Requirements

- Python 3.8+
- Foursquare Places API key

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd BizRadar
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Foursquare API key
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Configuration

- Set your business location and monitoring preferences in the Settings tab
- Configure monitoring radius and scan frequency
- Enable/disable notifications as needed

## API Key Setup

1. Visit [Foursquare Developer Portal](https://developer.foursquare.com/)
2. Create a new app and get your API key
3. Add the API key to your `.env` file
