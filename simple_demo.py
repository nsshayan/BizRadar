#!/usr/bin/env python3
"""
Simple Demo for BizRadar - No API Key Required

A simplified version that focuses on UI exploration without database complexity.
"""

import os
import sys
import flet as ft

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_sample_business_card(name, category, rating, is_competitor=False):
    """Create a sample business card for demo."""
    competitor_badge = ft.Container(
        content=ft.Text("COMPETITOR", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.RED_600,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
        border_radius=10
    ) if is_competitor else None
    
    rating_display = ft.Row([
        ft.Icon(ft.Icons.STAR, size=16, color=ft.Colors.ORANGE_600),
        ft.Text(f"{rating:.1f}", size=14)
    ], spacing=2)
    
    card_content = ft.Row([
        ft.Column([
            ft.Row([
                ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                competitor_badge
            ] if competitor_badge else [ft.Text(name, size=16, weight=ft.FontWeight.BOLD)]),
            ft.Text(category, size=12, color=ft.Colors.GREY_600),
            ft.Text("Sample address", size=12, color=ft.Colors.GREY_500),
            rating_display
        ], expand=True, spacing=5),
        ft.Column([
            ft.IconButton(icon=ft.Icons.INFO, tooltip="View Details"),
            ft.IconButton(icon=ft.Icons.EDIT, tooltip="Edit")
        ])
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    return ft.Container(
        content=card_content,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        padding=15,
        border=ft.border.all(1, ft.Colors.GREY_300),
        margin=ft.margin.only(bottom=10)
    )

def create_stat_card(title, value, icon, color):
    """Create a statistics card."""
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=30, color=color),
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(title, size=12, color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        width=150,
        height=100,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.GREY_300,
            offset=ft.Offset(0, 2)
        )
    )

def create_notification_card(title, message, notification_type="info"):
    """Create a notification card."""
    icon_map = {
        "info": (ft.Icons.INFO, ft.Colors.BLUE_600),
        "new": (ft.Icons.BUSINESS, ft.Colors.GREEN_600),
        "warning": (ft.Icons.WARNING, ft.Colors.ORANGE_600),
        "error": (ft.Icons.ERROR, ft.Colors.RED_600)
    }
    
    icon, color = icon_map.get(notification_type, icon_map["info"])
    
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=24, color=color),
            ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(message, size=12, color=ft.Colors.GREY_700),
                ft.Text("2 hours ago", size=10, color=ft.Colors.GREY_500)
            ], expand=True, spacing=2),
            ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Dismiss")
        ], spacing=10),
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        padding=15,
        border=ft.border.all(1, ft.Colors.GREY_300),
        margin=ft.margin.only(bottom=10)
    )

def main(page: ft.Page):
    """Main demo application."""
    page.title = "BizRadar Demo - No API Key Required"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    # Current view state
    current_view = ft.Ref[str]()
    current_view.current = "dashboard"
    
    # Content area
    content_area = ft.Container(expand=True, padding=20)
    
    def create_dashboard():
        """Create dashboard view."""
        # Statistics cards
        stats = ft.Row([
            create_stat_card("Total Businesses", "8", ft.Icons.BUSINESS, ft.Colors.BLUE_600),
            create_stat_card("Competitors", "4", ft.Icons.TRENDING_UP, ft.Colors.RED_600),
            create_stat_card("Avg Rating", "4.2", ft.Icons.STAR, ft.Colors.ORANGE_600),
            create_stat_card("New This Week", "2", ft.Icons.NEW_RELEASES, ft.Colors.GREEN_600),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        # Search and filters
        search_row = ft.Row([
            ft.TextField(label="Search businesses", prefix_icon=ft.Icons.SEARCH, width=300),
            ft.Dropdown(label="Category", options=[ft.dropdown.Option("All"), ft.dropdown.Option("Restaurant")], value="All", width=200),
            ft.ElevatedButton("Run Scan", icon=ft.Icons.RADAR, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
            ft.OutlinedButton("Export Data", icon=ft.Icons.DOWNLOAD)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Sample businesses
        businesses = ft.Column([
            create_sample_business_card("Tony's Italian Bistro", "Restaurant, Italian", 4.5, True),
            create_sample_business_card("Coffee Corner Cafe", "Coffee Shop", 4.2, True),
            create_sample_business_card("Fresh Market Grocery", "Grocery Store", 3.8, False),
            create_sample_business_card("Fitness First Gym", "Gym, Fitness", 4.0, False),
        ], spacing=0)
        
        return ft.Column([
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            stats,
            ft.Divider(),
            search_row,
            ft.Divider(),
            ft.Text("Sample Businesses (Demo Data)"),
            businesses
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_notifications():
        """Create notifications view."""
        notifications = ft.Column([
            create_notification_card("New Competitor Alert", "Quick Bites Food Truck has opened nearby", "new"),
            create_notification_card("Rating Update", "Tony's Italian Bistro rating increased to 4.5 stars", "info"),
            create_notification_card("Trending Business", "Coffee Corner Cafe is showing increased activity", "warning"),
            create_notification_card("Monitoring Started", "Background monitoring is now active", "info"),
        ], spacing=0)
        
        return ft.Column([
            ft.Text("Notifications", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("Mark All Read", icon=ft.Icons.MARK_EMAIL_READ, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.OutlinedButton("Clear Old", icon=ft.Icons.DELETE_SWEEP)
            ]),
            ft.Divider(),
            ft.Text("Sample Notifications (Demo Data)"),
            notifications
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def create_settings():
        """Create settings view."""
        return ft.Column([
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("API Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.TextField(label="Foursquare API Key", value="demo_key_12345", password=True, width=400),
                    ft.Text("Get your API key from https://developer.foursquare.com/", size=12, color=ft.Colors.GREY_600)
                ], spacing=10),
                padding=15,
                bgcolor=ft.Colors.GREY_50,
                border_radius=8
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Business Location", size=18, weight=ft.FontWeight.BOLD),
                    ft.TextField(label="Business Name", value="Demo Business", width=300),
                    ft.Row([
                        ft.TextField(label="Latitude", value="40.7128", width=150),
                        ft.TextField(label="Longitude", value="-74.0060", width=150)
                    ], spacing=10),
                ], spacing=10),
                padding=15,
                bgcolor=ft.Colors.GREY_50,
                border_radius=8
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Slider(min=100, max=5000, value=1000, label="Radius: {value}m", width=300),
                    ft.Dropdown(label="Scan Interval", options=[ft.dropdown.Option("60", "1 hour")], value="60", width=200),
                    ft.TextField(label="Categories to Monitor", value="Restaurant, Coffee Shop", width=400),
                ], spacing=15),
                padding=15,
                bgcolor=ft.Colors.GREY_50,
                border_radius=8
            ),
            ft.Row([
                ft.ElevatedButton("Save Settings", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.OutlinedButton("Test Connection", icon=ft.Icons.WIFI)
            ], spacing=10)
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    def on_nav_change(e):
        """Handle navigation changes."""
        selected_index = e.control.selected_index
        
        if selected_index == 0:  # Dashboard
            current_view.current = "dashboard"
            content_area.content = create_dashboard()
        elif selected_index == 1:  # Notifications
            current_view.current = "notifications"
            content_area.content = create_notifications()
        elif selected_index == 2:  # Settings
            current_view.current = "settings"
            content_area.content = create_settings()
        
        page.update()
    
    # Navigation rail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.NOTIFICATIONS, label="Notifications"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_nav_change,
    )
    
    # App bar
    app_bar = ft.AppBar(
        title=ft.Text("BizRadar Demo", size=20, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh"),
            ft.IconButton(icon=ft.Icons.INFO, tooltip="About Demo")
        ]
    )
    
    # Initialize with dashboard
    content_area.content = create_dashboard()
    
    # Main layout
    main_layout = ft.Row([
        nav_rail,
        ft.VerticalDivider(width=1),
        content_area
    ], expand=True, spacing=0)
    
    page.appbar = app_bar
    page.add(main_layout)
    
    # Show demo message
    page.snack_bar = ft.SnackBar(
        content=ft.Text("🎯 SIMPLE DEMO: Explore BizRadar UI without API requirements!"),
        bgcolor=ft.Colors.GREEN_600
    )
    page.snack_bar.open = True
    page.update()

if __name__ == "__main__":
    print("🎯 Starting BizRadar Simple Demo")
    print("=" * 40)
    print("✓ No API key required")
    print("✓ No database setup needed") 
    print("✓ Pure UI exploration")
    print("✓ All interface elements functional")
    print("=" * 40)
    
    ft.app(target=main, view=ft.WEB_BROWSER, port=8082)
