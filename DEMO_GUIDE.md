# 🎯 BizRadar Demo Guide - Explore Without API Key

This guide shows you how to fully explore BizRadar's features without needing a working Foursquare API key.

## 🚀 Quick Start - Demo Mode

### Option 1: Full Demo Mode (Recommended)
```bash
# Run the complete demo with sample data
python demo_mode.py
```

This launches BizRadar with:
- ✅ 8 sample businesses with realistic data
- ✅ Mock API responses (no internet required)
- ✅ Sample notifications and scan history
- ✅ Full UI functionality
- ✅ All features working without API key

### Option 2: Regular Mode with Mock Data
```bash
# Set a dummy API key and run normally
echo "FOURSQUARE_API_KEY=demo_key_for_testing" > .env
python main.py
```

## 📱 What You Can Explore

### 🏠 **Dashboard View**
**Features to Test:**
- **Business Listings**: View 8 sample businesses with different categories
- **Statistics Cards**: See competitor counts, average ratings, recent additions
- **Search & Filtering**: 
  - Search by business name (try "Tony's" or "Coffee")
  - Filter by category (Restaurant, Coffee Shop, etc.)
  - Filter by minimum rating (use slider)
- **Business Cards**: Click on businesses to see detailed information
- **Competitor Management**: Toggle competitor status with the edit button
- **Export Function**: Export sample data to CSV
- **Manual Scan**: Test the "Run Scan" button (uses mock data)

**Sample Data Included:**
- Tony's Italian Bistro (4.5⭐, Competitor)
- Coffee Corner Cafe (4.2⭐, Competitor) 
- Fresh Market Grocery (3.8⭐)
- Fitness First Gym (4.0⭐)
- Quick Bites Food Truck (4.3⭐, Competitor)
- Sunset Bar & Grill (4.1⭐, Competitor)
- Tech Repair Shop (4.7⭐)
- Bella's Beauty Salon (4.4⭐)

### 🔔 **Notifications View**
**Features to Test:**
- **Notification Types**: See examples of all notification types:
  - New Business alerts
  - Rating change notifications
  - Trending activity alerts
  - System notifications
- **Filtering**: Filter by notification type and read status
- **Management**: Mark notifications as read/unread, dismiss notifications
- **Statistics**: View notification counts and recent activity
- **Time Display**: See relative time stamps ("2 hours ago", etc.)

**Sample Notifications Included:**
- New competitor alert for Quick Bites Food Truck
- Rating update for Tony's Italian Bistro
- Trending activity for Coffee Corner Cafe
- System monitoring status

### ⚙️ **Settings View**
**Features to Test:**
- **API Configuration**: See the API key field (pre-filled in demo)
- **Business Location**: Set your business coordinates
  - Try: Latitude: 40.7128, Longitude: -74.0060 (NYC)
- **Monitoring Settings**:
  - Radius slider (100m - 5km)
  - Scan interval dropdown (15 min - 24 hours)
  - Categories to monitor (comma-separated)
  - Exclude categories
  - Minimum rating filter
- **Notification Preferences**: Toggle different alert types
- **Test Connection**: Test the mock API connection
- **Save Settings**: All settings are saved to the demo database

## 🧪 Testing Scenarios

### Scenario 1: New Business Owner Setup
1. **Launch Demo**: `python demo_mode.py`
2. **Configure Location**: Go to Settings → Set business location
3. **Set Monitoring**: Choose radius (try 1000m) and categories
4. **Run First Scan**: Dashboard → "Run Scan" button
5. **Review Results**: See discovered businesses
6. **Mark Competitors**: Click edit buttons to mark relevant competitors

### Scenario 2: Ongoing Monitoring
1. **Check Dashboard**: Review competitor statistics
2. **Filter Competitors**: Use "Competitor" filter to see only marked businesses
3. **Review Notifications**: Check for new alerts
4. **Export Data**: Download business data for analysis
5. **Adjust Settings**: Modify monitoring preferences

### Scenario 3: Data Analysis
1. **Search Function**: Test search with different terms
2. **Category Analysis**: Filter by different business types
3. **Rating Analysis**: Use rating slider to filter high-rated businesses
4. **Export & Analyze**: Export data to CSV and open in spreadsheet
5. **Notification History**: Review alert patterns

## 🔍 UI Components to Explore

### Navigation
- **Navigation Rail**: Switch between Dashboard, Notifications, Settings
- **App Bar**: Use refresh button and info button
- **Responsive Design**: Resize window to see responsive behavior

### Interactive Elements
- **Search Field**: Real-time filtering as you type
- **Dropdowns**: Category and interval selectors
- **Sliders**: Radius and rating controls
- **Checkboxes**: Notification preferences
- **Buttons**: All buttons are functional in demo mode
- **Cards**: Business and notification cards with hover effects

### Data Display
- **Statistics**: Live-updating counters and metrics
- **Lists**: Scrollable business and notification lists
- **Icons**: Category and status indicators
- **Time Stamps**: Relative time display
- **Status Indicators**: Read/unread, competitor badges

## 📊 Understanding the Full Application

### What Works in Demo Mode:
✅ **Complete UI**: All interface elements functional  
✅ **Data Management**: Save/load settings and preferences  
✅ **Search & Filtering**: All filtering options work  
✅ **Notifications**: Full notification system  
✅ **Export**: CSV export with sample data  
✅ **Database**: Local SQLite storage  

### What You'll Get with Real API Key:
🔑 **Live Data**: Real businesses from Foursquare  
🔑 **Real-time Updates**: Actual business changes  
🔑 **Background Monitoring**: Automated periodic scans  
🔑 **Trending Detection**: Real popularity trends  
🔑 **Accurate Locations**: Precise business coordinates  
🔑 **Current Information**: Up-to-date ratings and details  

## 🛠️ Advanced Testing

### Database Exploration
```bash
# View the demo database
sqlite3 data/bizradar_demo.db
.tables
SELECT * FROM businesses;
SELECT * FROM notifications;
```

### Component Testing
```bash
# Run individual tests
python -m unittest tests.test_database
python -m unittest tests.test_foursquare_client

# Run all tests
python run_tests.py
```

### Log Analysis
```bash
# Check application logs (if any issues)
ls logs/
```

## 🎯 Demo Limitations

**What's Simulated:**
- API responses use static sample data
- Background monitoring uses mock scans
- Trending data is pre-generated
- Geographic calculations use sample coordinates

**What's Real:**
- All UI interactions and navigation
- Database operations and data persistence
- Settings management and configuration
- Notification system and management
- Export functionality
- Error handling and user feedback

## 🚀 Next Steps

After exploring the demo:

1. **Get API Key**: Visit [developer.foursquare.com](https://developer.foursquare.com/)
2. **Configure Real App**: Update `.env` with your actual API key
3. **Set Real Location**: Enter your actual business coordinates
4. **Start Monitoring**: Begin real competitor tracking
5. **Customize Settings**: Adjust for your specific business needs

## 💡 Tips for Demo Exploration

- **Try All Features**: Click every button and explore every view
- **Test Edge Cases**: Try empty searches, extreme filter values
- **Simulate Usage**: Pretend you're a real business owner
- **Check Responsiveness**: Resize the window to test different sizes
- **Export Data**: Download the CSV to see the data format
- **Read Documentation**: Check DOCUMENTATION.md for detailed feature explanations

**The demo gives you a complete picture of BizRadar's capabilities!** 🎯
