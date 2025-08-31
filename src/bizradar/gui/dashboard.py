"""
Dashboard view for BizRadar application.

Contains the main dashboard interface showing competitors, metrics, and monitoring status.
"""

import flet as ft
from typing import List, Optional
from datetime import datetime

from ..models.business import Business
from ..models.monitoring import MonitoringSettings

class DashboardView:
    """Dashboard view component."""
    
    def __init__(self, app):
        self.app = app
        self.businesses = []
        self.filtered_businesses = []
        self.search_query = ""
        self.category_filter = "All"
        self.rating_filter = 0.0
        
        # UI components
        self.search_field = None
        self.category_dropdown = None
        self.rating_slider = None
        self.businesses_list = None
        self.stats_cards = None
    
    def build(self) -> ft.Control:
        """Build the dashboard interface."""
        # Load data
        self.load_data()
        
        # Create search and filter controls
        self.search_field = ft.TextField(
            label="Search businesses",
            prefix_icon=ft.icons.SEARCH,
            on_change=self.on_search_change,
            width=300
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option("All")] + [
                ft.dropdown.Option(cat) for cat in self.get_unique_categories()
            ],
            value="All",
            on_change=self.on_category_change,
            width=200
        )
        
        self.rating_slider = ft.Slider(
            min=0,
            max=5,
            divisions=10,
            value=0,
            label="Min Rating: {value}",
            on_change=self.on_rating_change,
            width=200
        )
        
        # Create action buttons
        scan_button = ft.ElevatedButton(
            text="Run Scan",
            icon=ft.icons.RADAR,
            on_click=self.run_manual_scan,
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE
        )
        
        export_button = ft.OutlinedButton(
            text="Export Data",
            icon=ft.icons.DOWNLOAD,
            on_click=self.export_data
        )
        
        # Create filter row
        filter_row = ft.Row([
            self.search_field,
            self.category_dropdown,
            ft.Column([
                ft.Text("Minimum Rating"),
                self.rating_slider
            ]),
            scan_button,
            export_button
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Create statistics cards
        self.stats_cards = self.create_stats_cards()
        
        # Create businesses list
        self.businesses_list = self.create_businesses_list()
        
        # Main dashboard layout
        dashboard = ft.Column([
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.stats_cards,
            ft.Divider(),
            filter_row,
            ft.Divider(),
            self.businesses_list
        ], spacing=20, expand=True)
        
        return ft.Container(
            content=dashboard,
            padding=20,
            expand=True
        )
    
    def load_data(self):
        """Load businesses and monitoring data."""
        try:
            # Get all businesses from database
            self.businesses = self.app.db_manager.get_all_businesses()
            self.apply_filters()
        except Exception as e:
            print(f"Error loading data: {e}")
            self.businesses = []
            self.filtered_businesses = []
    
    def apply_filters(self):
        """Apply current filters to the businesses list."""
        filtered = self.businesses
        
        # Apply search filter
        if self.search_query:
            filtered = [b for b in filtered if 
                       self.search_query.lower() in b.name.lower() or
                       any(self.search_query.lower() in cat.lower() for cat in b.categories)]
        
        # Apply category filter
        if self.category_filter != "All":
            filtered = [b for b in filtered if 
                       any(self.category_filter.lower() in cat.lower() for cat in b.categories)]
        
        # Apply rating filter
        if self.rating_filter > 0:
            filtered = [b for b in filtered if b.rating and b.rating >= self.rating_filter]
        
        self.filtered_businesses = filtered
    
    def get_unique_categories(self) -> List[str]:
        """Get unique categories from all businesses."""
        categories = set()
        for business in self.businesses:
            categories.update(business.categories)
        return sorted(list(categories))
    
    def create_stats_cards(self) -> ft.Row:
        """Create statistics cards for the dashboard."""
        # Calculate statistics
        total_businesses = len(self.businesses)
        competitors = [b for b in self.businesses if b.is_competitor]
        total_competitors = len(competitors)
        avg_rating = sum(b.rating for b in self.businesses if b.rating) / max(len([b for b in self.businesses if b.rating]), 1)
        recent_additions = len([b for b in self.businesses if b.first_seen and 
                               (datetime.now() - b.first_seen).days <= 7])
        
        # Create cards
        cards = ft.Row([
            self.create_stat_card("Total Businesses", str(total_businesses), ft.icons.BUSINESS, ft.colors.BLUE_600),
            self.create_stat_card("Competitors", str(total_competitors), ft.icons.TRENDING_UP, ft.colors.RED_600),
            self.create_stat_card("Avg Rating", f"{avg_rating:.1f}" if avg_rating else "N/A", ft.icons.STAR, ft.colors.ORANGE_600),
            self.create_stat_card("New This Week", str(recent_additions), ft.icons.NEW_RELEASES, ft.colors.GREEN_600),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        return cards
    
    def create_stat_card(self, title: str, value: str, icon, color) -> ft.Container:
        """Create a statistics card."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=30, color=color),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=12, color=ft.colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            width=150,
            height=100,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.GREY_300,
                offset=ft.Offset(0, 2)
            )
        )
    
    def create_businesses_list(self) -> ft.Container:
        """Create the businesses list view."""
        if not self.filtered_businesses:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.BUSINESS, size=64, color=ft.colors.GREY_400),
                    ft.Text("No businesses found", size=16, color=ft.colors.GREY_600),
                    ft.Text("Try adjusting your filters or run a scan to discover businesses", 
                           size=12, color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                height=200,
                alignment=ft.alignment.center
            )
        
        # Create business cards
        business_cards = []
        for business in self.filtered_businesses[:20]:  # Limit to 20 for performance
            business_cards.append(self.create_business_card(business))
        
        return ft.Container(
            content=ft.Column([
                ft.Text(f"Showing {len(business_cards)} of {len(self.filtered_businesses)} businesses"),
                ft.Column(business_cards, spacing=10)
            ], spacing=10),
            height=400,
            expand=True
        )
    
    def create_business_card(self, business: Business) -> ft.Container:
        """Create a card for displaying business information."""
        # Create rating display
        rating_display = ft.Row([
            ft.Icon(ft.icons.STAR, size=16, color=ft.colors.ORANGE_600),
            ft.Text(f"{business.rating:.1f}" if business.rating else "N/A", size=14)
        ], spacing=2) if business.rating else ft.Text("No rating", size=14, color=ft.colors.GREY_500)
        
        # Create competitor badge
        competitor_badge = ft.Container(
            content=ft.Text("COMPETITOR", size=10, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.colors.RED_600,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        ) if business.is_competitor else None
        
        # Create categories display
        categories_text = ", ".join(business.categories[:3])
        if len(business.categories) > 3:
            categories_text += f" (+{len(business.categories) - 3} more)"
        
        # Main card content
        card_content = ft.Row([
            ft.Column([
                ft.Row([
                    ft.Text(business.name, size=16, weight=ft.FontWeight.BOLD),
                    competitor_badge
                ] if competitor_badge else [ft.Text(business.name, size=16, weight=ft.FontWeight.BOLD)]),
                ft.Text(categories_text, size=12, color=ft.colors.GREY_600),
                ft.Text(business.location.address or "Address not available", size=12, color=ft.colors.GREY_500),
                rating_display
            ], expand=True, spacing=5),
            ft.Column([
                ft.IconButton(
                    icon=ft.icons.INFO,
                    tooltip="View Details",
                    on_click=lambda e, b=business: self.show_business_details(b)
                ),
                ft.IconButton(
                    icon=ft.icons.EDIT if business.is_competitor else ft.icons.ADD,
                    tooltip="Edit" if business.is_competitor else "Mark as Competitor",
                    on_click=lambda e, b=business: self.toggle_competitor_status(b)
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        return ft.Container(
            content=card_content,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            padding=15,
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color=ft.colors.GREY_200,
                offset=ft.Offset(0, 1)
            )
        )

    def on_search_change(self, e):
        """Handle search field changes."""
        self.search_query = e.control.value
        self.apply_filters()
        self.refresh_businesses_list()

    def on_category_change(self, e):
        """Handle category dropdown changes."""
        self.category_filter = e.control.value
        self.apply_filters()
        self.refresh_businesses_list()

    def on_rating_change(self, e):
        """Handle rating slider changes."""
        self.rating_filter = e.control.value
        self.apply_filters()
        self.refresh_businesses_list()

    def refresh_businesses_list(self):
        """Refresh the businesses list display."""
        if hasattr(self, 'businesses_list') and self.businesses_list:
            # Update the businesses list content
            new_list = self.create_businesses_list()
            # Find the parent container and update it
            # This is a simplified approach - in a real app you'd want more sophisticated state management
            self.app.page.update()

    def run_manual_scan(self, e):
        """Run a manual scan for businesses."""
        if not self.app.monitoring_service:
            self.app.show_error_message("Monitoring service not available. Please configure your API key.")
            return

        settings = self.app.db_manager.get_monitoring_settings()
        if not settings:
            self.app.show_error_message("Please configure monitoring settings first.")
            return

        try:
            self.app.show_info_message("Starting scan...")
            scan_result = self.app.monitoring_service.perform_scan(settings)

            if scan_result.success:
                self.app.show_success_message(
                    f"Scan completed! Found {scan_result.new_businesses} new businesses, "
                    f"updated {scan_result.updated_businesses} existing ones."
                )
                self.refresh()
            else:
                self.app.show_error_message(f"Scan failed: {scan_result.error_message}")
        except Exception as ex:
            self.app.show_error_message(f"Scan error: {str(ex)}")

    def export_data(self, e):
        """Export business data to CSV."""
        try:
            import csv
            from datetime import datetime

            filename = f"bizradar_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'categories', 'rating', 'address', 'phone', 'website', 'is_competitor', 'first_seen']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for business in self.filtered_businesses:
                    writer.writerow({
                        'name': business.name,
                        'categories': ', '.join(business.categories),
                        'rating': business.rating or '',
                        'address': business.location.address or '',
                        'phone': business.phone or '',
                        'website': business.website or '',
                        'is_competitor': 'Yes' if business.is_competitor else 'No',
                        'first_seen': business.first_seen.strftime('%Y-%m-%d') if business.first_seen else ''
                    })

            self.app.show_success_message(f"Data exported to {filename}")
        except Exception as ex:
            self.app.show_error_message(f"Export failed: {str(ex)}")

    def show_business_details(self, business: Business):
        """Show detailed information about a business."""
        details_content = ft.Column([
            ft.Text(business.name, size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Categories: {', '.join(business.categories)}"),
            ft.Text(f"Rating: {business.rating:.1f} stars" if business.rating else "Rating: Not available"),
            ft.Text(f"Address: {business.location.address or 'Not available'}"),
            ft.Text(f"Phone: {business.phone or 'Not available'}"),
            ft.Text(f"Website: {business.website or 'Not available'}"),
            ft.Text(f"Verified: {'Yes' if business.verified else 'No'}"),
            ft.Text(f"Competitor: {'Yes' if business.is_competitor else 'No'}"),
            ft.Text(f"First seen: {business.first_seen.strftime('%Y-%m-%d %H:%M') if business.first_seen else 'Unknown'}"),
            ft.Text(f"Last updated: {business.last_updated.strftime('%Y-%m-%d %H:%M') if business.last_updated else 'Unknown'}"),
        ], spacing=10)

        dialog = ft.AlertDialog(
            title=ft.Text("Business Details"),
            content=details_content,
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.app.close_dialog())
            ]
        )

        self.app.page.dialog = dialog
        dialog.open = True
        self.app.page.update()

    def toggle_competitor_status(self, business: Business):
        """Toggle the competitor status of a business."""
        business.is_competitor = not business.is_competitor
        business.last_updated = datetime.now()

        if self.app.db_manager.save_business(business):
            status = "competitor" if business.is_competitor else "regular business"
            self.app.show_success_message(f"{business.name} marked as {status}")
            self.refresh()
        else:
            self.app.show_error_message("Failed to update business status")

    def refresh(self):
        """Refresh the entire dashboard."""
        self.load_data()
        if hasattr(self, 'stats_cards'):
            self.stats_cards = self.create_stats_cards()
        self.app.page.update()
