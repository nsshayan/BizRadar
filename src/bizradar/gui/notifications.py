"""
Notifications view for BizRadar application.

Contains the notifications interface for viewing and managing alerts.
"""

import flet as ft
from typing import List
from datetime import datetime, timedelta

from ..models.monitoring import Notification, NotificationType

class NotificationsView:
    """Notifications view component."""
    
    def __init__(self, app):
        self.app = app
        self.notifications = []
        self.filter_type = "all"
        self.show_read = True
        
        # UI components
        self.filter_dropdown = None
        self.show_read_checkbox = None
        self.notifications_list = None
        self.stats_row = None
    
    def build(self) -> ft.Control:
        """Build the notifications interface."""
        self.load_notifications()
        
        # Create filter controls
        self.filter_dropdown = ft.Dropdown(
            label="Filter by Type",
            options=[
                ft.dropdown.Option("all", "All Notifications"),
                ft.dropdown.Option("new_business", "New Businesses"),
                ft.dropdown.Option("business_updated", "Business Updates"),
                ft.dropdown.Option("trending_activity", "Trending Activity"),
                ft.dropdown.Option("rating_change", "Rating Changes"),
                ft.dropdown.Option("competitor_alert", "Competitor Alerts")
            ],
            value="all",
            on_change=self.on_filter_change,
            width=200
        )
        
        self.show_read_checkbox = ft.Checkbox(
            label="Show read notifications",
            value=True,
            on_change=self.on_show_read_change
        )
        
        # Create action buttons
        mark_all_read_button = ft.ElevatedButton(
            text="Mark All Read",
            icon=ft.icons.MARK_EMAIL_READ,
            on_click=self.mark_all_read,
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE
        )
        
        clear_old_button = ft.OutlinedButton(
            text="Clear Old",
            icon=ft.icons.DELETE_SWEEP,
            on_click=self.clear_old_notifications
        )
        
        # Create filter row
        filter_row = ft.Row([
            self.filter_dropdown,
            self.show_read_checkbox,
            mark_all_read_button,
            clear_old_button
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Create statistics row
        self.stats_row = self.create_stats_row()
        
        # Create notifications list
        self.notifications_list = self.create_notifications_list()
        
        # Main notifications layout
        notifications_layout = ft.Column([
            ft.Text("Notifications", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.stats_row,
            ft.Divider(),
            filter_row,
            ft.Divider(),
            self.notifications_list
        ], spacing=20, expand=True)
        
        return ft.Container(
            content=notifications_layout,
            padding=20,
            expand=True
        )
    
    def load_notifications(self):
        """Load notifications from database."""
        try:
            self.notifications = self.app.db_manager.get_notifications(limit=100)
            self.apply_filters()
        except Exception as e:
            print(f"Error loading notifications: {e}")
            self.notifications = []
    
    def apply_filters(self):
        """Apply current filters to notifications."""
        filtered = self.notifications
        
        # Filter by type
        if self.filter_type != "all":
            filtered = [n for n in filtered if n.type.value == self.filter_type]
        
        # Filter by read status
        if not self.show_read:
            filtered = [n for n in filtered if not n.read]
        
        self.filtered_notifications = filtered
    
    def create_stats_row(self) -> ft.Row:
        """Create statistics row for notifications."""
        total_count = len(self.notifications)
        unread_count = len([n for n in self.notifications if not n.read and not n.dismissed])
        today_count = len([n for n in self.notifications if n.created_at and 
                          n.created_at.date() == datetime.now().date()])
        
        stats = ft.Row([
            self.create_stat_item("Total", str(total_count), ft.icons.NOTIFICATIONS, ft.colors.BLUE_600),
            self.create_stat_item("Unread", str(unread_count), ft.icons.MARK_EMAIL_UNREAD, ft.colors.RED_600),
            self.create_stat_item("Today", str(today_count), ft.icons.TODAY, ft.colors.GREEN_600),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        return stats
    
    def create_stat_item(self, label: str, value: str, icon, color) -> ft.Container:
        """Create a statistics item."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=color),
                ft.Column([
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(label, size=12, color=ft.colors.GREY_600)
                ], spacing=2)
            ], spacing=10),
            padding=10,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
    
    def create_notifications_list(self) -> ft.Container:
        """Create the notifications list view."""
        if not hasattr(self, 'filtered_notifications'):
            self.apply_filters()
        
        if not self.filtered_notifications:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.NOTIFICATIONS_NONE, size=64, color=ft.colors.GREY_400),
                    ft.Text("No notifications found", size=16, color=ft.colors.GREY_600),
                    ft.Text("Notifications will appear here when businesses are detected", 
                           size=12, color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                height=200,
                alignment=ft.alignment.center
            )
        
        # Create notification cards
        notification_cards = []
        for notification in self.filtered_notifications:
            notification_cards.append(self.create_notification_card(notification))
        
        return ft.Container(
            content=ft.Column([
                ft.Text(f"Showing {len(notification_cards)} notifications"),
                ft.Column(notification_cards, spacing=10, scroll=ft.ScrollMode.AUTO)
            ], spacing=10),
            height=400,
            expand=True
        )
    
    def create_notification_card(self, notification: Notification) -> ft.Container:
        """Create a card for displaying notification information."""
        # Get notification type icon and color
        type_info = self.get_notification_type_info(notification.type)
        
        # Create timestamp display
        time_ago = self.get_time_ago(notification.created_at) if notification.created_at else "Unknown time"
        
        # Create read/unread indicator
        read_indicator = ft.Container(
            width=8,
            height=8,
            bgcolor=ft.colors.GREY_400 if notification.read else ft.colors.BLUE_600,
            border_radius=4
        )
        
        # Main card content
        card_content = ft.Row([
            read_indicator,
            ft.Icon(type_info["icon"], size=24, color=type_info["color"]),
            ft.Column([
                ft.Text(notification.title, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(notification.message, size=12, color=ft.colors.GREY_700),
                ft.Text(time_ago, size=10, color=ft.colors.GREY_500)
            ], expand=True, spacing=2),
            ft.Column([
                ft.IconButton(
                    icon=ft.icons.MARK_EMAIL_READ if not notification.read else ft.icons.MARK_EMAIL_UNREAD,
                    tooltip="Mark as read" if not notification.read else "Mark as unread",
                    on_click=lambda e, n=notification: self.toggle_read_status(n)
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="Dismiss",
                    on_click=lambda e, n=notification: self.dismiss_notification(n)
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10)
        
        # Card styling based on read status
        bgcolor = ft.colors.WHITE if notification.read else ft.colors.BLUE_50
        border_color = ft.colors.GREY_300 if notification.read else ft.colors.BLUE_300
        
        return ft.Container(
            content=card_content,
            bgcolor=bgcolor,
            border_radius=8,
            padding=15,
            border=ft.border.all(1, border_color),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color=ft.colors.GREY_200,
                offset=ft.Offset(0, 1)
            )
        )
    
    def get_notification_type_info(self, notification_type: NotificationType) -> dict:
        """Get icon and color for notification type."""
        type_map = {
            NotificationType.NEW_BUSINESS: {"icon": ft.icons.BUSINESS, "color": ft.colors.GREEN_600},
            NotificationType.BUSINESS_UPDATED: {"icon": ft.icons.UPDATE, "color": ft.colors.BLUE_600},
            NotificationType.TRENDING_ACTIVITY: {"icon": ft.icons.TRENDING_UP, "color": ft.colors.ORANGE_600},
            NotificationType.RATING_CHANGE: {"icon": ft.icons.STAR, "color": ft.colors.PURPLE_600},
            NotificationType.COMPETITOR_ALERT: {"icon": ft.icons.WARNING, "color": ft.colors.RED_600}
        }
        return type_map.get(notification_type, {"icon": ft.icons.NOTIFICATIONS, "color": ft.colors.GREY_600})
    
    def get_time_ago(self, timestamp: datetime) -> str:
        """Get human-readable time ago string."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def on_filter_change(self, e):
        """Handle filter dropdown changes."""
        self.filter_type = e.control.value
        self.apply_filters()
        self.refresh_notifications_list()
    
    def on_show_read_change(self, e):
        """Handle show read checkbox changes."""
        self.show_read = e.control.value
        self.apply_filters()
        self.refresh_notifications_list()
    
    def refresh_notifications_list(self):
        """Refresh the notifications list display."""
        self.notifications_list = self.create_notifications_list()
        self.app.page.update()
    
    def toggle_read_status(self, notification: Notification):
        """Toggle the read status of a notification."""
        if notification.read:
            # Mark as unread (not directly supported by database, but we can work around it)
            notification.read = False
        else:
            if self.app.db_manager.mark_notification_read(notification.id):
                notification.read = True
                self.app.show_success_message("Notification marked as read")
            else:
                self.app.show_error_message("Failed to update notification")
                return
        
        self.refresh()
    
    def dismiss_notification(self, notification: Notification):
        """Dismiss a notification."""
        if self.app.db_manager.dismiss_notification(notification.id):
            self.app.show_success_message("Notification dismissed")
            self.refresh()
        else:
            self.app.show_error_message("Failed to dismiss notification")
    
    def mark_all_read(self, e):
        """Mark all notifications as read."""
        count = self.app.notification_service.mark_all_read()
        if count > 0:
            self.app.show_success_message(f"Marked {count} notifications as read")
            self.refresh()
        else:
            self.app.show_info_message("No unread notifications to mark")
    
    def clear_old_notifications(self, e):
        """Clear old notifications (older than 30 days)."""
        # This would require a new database method
        self.app.show_info_message("Clear old notifications feature coming soon")
    
    def refresh(self):
        """Refresh the entire notifications view."""
        self.load_notifications()
        self.stats_row = self.create_stats_row()
        self.app.page.update()
