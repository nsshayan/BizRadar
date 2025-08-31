# BizRadar - Complete Documentation

## Overview

BizRadar is a comprehensive business monitoring application that helps business owners track their local competitive landscape in real-time using the Foursquare Places API and a modern Flet-based GUI.

## Features

### Core Features
- **Real-time Competitor Monitoring**: Automatically scan for businesses within a configurable radius
- **Intelligent Notifications**: Get alerts for new businesses, rating changes, and trending activity
- **Interactive Dashboard**: View competitor information with filtering and search capabilities
- **Background Scanning**: Automated periodic monitoring with customizable intervals
- **Data Export**: Export business data to CSV for analysis
- **Comprehensive Settings**: Configure monitoring preferences, API settings, and notification options

### Technical Features
- **Foursquare API Integration**: Full integration with rate limiting and error handling
- **Local Data Storage**: SQLite database for tracking changes over time
- **Modern GUI**: Flet-based interface with responsive design
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Extensible Architecture**: Modular design for easy feature additions

## Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for API access
- Foursquare Places API key

### Quick Setup
1. Clone or download the BizRadar application
2. Run the setup script:
   ```bash
   python setup.py
   ```
3. Get your Foursquare API key from [developer.foursquare.com](https://developer.foursquare.com/)
4. Edit the `.env` file and add your API key:
   ```
   FOURSQUARE_API_KEY=your_actual_api_key_here
   ```
5. Launch the application:
   ```bash
   python main.py
   ```

### Manual Installation
If you prefer manual installation:
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python main.py
```

## Configuration

### Environment Variables
Edit the `.env` file to configure:

```bash
# Required: Foursquare API Configuration
FOURSQUARE_API_KEY=your_foursquare_api_key_here

# Optional: Application Configuration
DEFAULT_RADIUS=1000                # Default monitoring radius in meters
SCAN_INTERVAL_MINUTES=60          # Default scan interval
MAX_RESULTS_PER_SCAN=50           # Maximum results per API call

# Optional: Database Configuration
DATABASE_PATH=data/bizradar.db    # Database file location

# Optional: Notification Settings
ENABLE_NOTIFICATIONS=true         # Enable desktop notifications
NOTIFICATION_SOUND=true           # Enable notification sounds
```

### Application Settings
Configure through the Settings tab in the application:

1. **Business Location**: Set your business name and coordinates
2. **Monitoring Radius**: Choose scanning radius (100m - 5km)
3. **Scan Interval**: Set automatic scanning frequency
4. **Categories**: Specify business types to monitor or exclude
5. **Notifications**: Configure alert preferences
6. **Rating Filters**: Set minimum rating thresholds

## Usage Guide

### Getting Started
1. **Initial Setup**: Configure your API key and business location
2. **Run First Scan**: Click "Run Scan" to discover nearby businesses
3. **Review Results**: Browse discovered businesses in the dashboard
4. **Mark Competitors**: Identify and mark relevant competitors
5. **Enable Monitoring**: Activate background scanning for ongoing monitoring

### Dashboard Features
- **Search and Filter**: Find specific businesses by name or category
- **Business Cards**: View detailed information for each business
- **Statistics**: Monitor competitor counts, ratings, and trends
- **Export Data**: Download business data for external analysis

### Notifications
BizRadar provides several types of notifications:
- **New Business Alerts**: When new businesses open nearby
- **Rating Changes**: When competitor ratings change significantly
- **Trending Activity**: When businesses show increased activity
- **System Alerts**: For scan results and errors

### Background Monitoring
- Automatic scanning runs at configured intervals
- Monitors for new businesses and changes to existing ones
- Sends notifications for significant events
- Maintains scan history for analysis

## API Integration

### Foursquare Places API
BizRadar integrates with the Foursquare Places API to:
- Search for businesses by location and category
- Retrieve detailed business information
- Monitor business changes over time
- Respect API rate limits and handle errors gracefully

### Rate Limiting
- Built-in rate limiting to respect API quotas
- Automatic retry logic for temporary failures
- Graceful degradation when limits are reached

## Data Management

### Database Schema
BizRadar uses SQLite with the following main tables:
- **businesses**: Store business information and competitor status
- **monitoring_settings**: Configuration and preferences
- **notifications**: Alert history and status
- **scan_history**: Record of monitoring scans

### Data Export
Export business data in CSV format including:
- Business names and categories
- Ratings and verification status
- Contact information and addresses
- Competitor status and discovery dates

## Architecture

### Project Structure
```
BizRadar/
├── src/bizradar/           # Main application code
│   ├── api/               # Foursquare API client
│   ├── models/            # Data models
│   ├── services/          # Business logic services
│   ├── gui/               # Flet GUI components
│   └── utils/             # Utilities and configuration
├── tests/                 # Unit tests
├── data/                  # Database and data files
├── logs/                  # Application logs
├── main.py               # Application entry point
├── setup.py              # Installation script
└── run_tests.py          # Test runner
```

### Key Components
- **FoursquareClient**: API integration with rate limiting
- **MonitoringService**: Core business monitoring logic
- **NotificationService**: Alert management and delivery
- **BackgroundMonitor**: Automated scanning service
- **DatabaseManager**: Data persistence and retrieval
- **GUI Components**: Dashboard, settings, and notifications views

## Testing

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test files
python -m unittest tests.test_foursquare_client
python -m unittest tests.test_database
```

### Test Coverage
- API client functionality and error handling
- Database operations and data integrity
- Business logic and monitoring algorithms
- Configuration management

## Troubleshooting

### Common Issues

**API Key Problems**
- Ensure your API key is valid and active
- Check that you haven't exceeded rate limits
- Verify the key is correctly set in the .env file

**Database Issues**
- Check that the data directory is writable
- Ensure SQLite is available (built into Python)
- Try deleting the database file to reset

**GUI Problems**
- Ensure Flet is properly installed
- Check that port 8080 is available
- Try running with different browser settings

**Network Issues**
- Verify internet connectivity
- Check firewall settings
- Ensure Foursquare API is accessible

### Logging
Check the `logs/` directory for detailed error information and debugging data.

## Contributing

### Development Setup
1. Fork the repository
2. Install development dependencies
3. Run tests to ensure everything works
4. Make your changes
5. Add tests for new functionality
6. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write comprehensive tests for new features

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support and questions:
1. Check this documentation
2. Review the troubleshooting section
3. Check the logs directory for error details
4. Run the test suite to identify issues

## Version History

### v1.0.0
- Initial release with core monitoring functionality
- Foursquare API integration
- Flet-based GUI
- Background monitoring service
- Notification system
- Data export capabilities
