import frappe
from frappe import _
from frappe.utils import now_datetime, flt, getdate, add_to_date
from datetime import datetime, timedelta

@frappe.whitelist()
def get_dashboard_stats():
    """Return dashboard statistics"""
    today = getdate()
    
    # Get room statistics
    rooms = frappe.get_all("Room", fields=["status"])
    total_rooms = len(rooms)
    available_rooms = len([r for r in rooms if r.status == "Available"])
    occupied_rooms = len([r for r in rooms if r.status == "Occupied"])
    
    # Get today's checkouts
    checkouts = frappe.get_all(
        "Checked In",
        filters={
            "actual_check_out": ["between", [today, add_to_date(today, days=1)]],
            "docstatus": 1
        },
        fields=["name"]
    )
    checkouts_today = len(checkouts)
    
    # Get today's revenue
    revenue = frappe.db.sql("""
        SELECT SUM(total_amount) as total
        FROM `tabChecked In`
        WHERE DATE(actual_check_in) = %s AND docstatus = 1
    """, today, as_dict=True)
    
    revenue_today = flt(revenue[0].total) if revenue else 0
    
    return {
        "available_rooms": available_rooms,
        "occupied_rooms": occupied_rooms,
        "checkouts_today": checkouts_today,
        "revenue_today": revenue_today
    }

@frappe.whitelist()
def get_recent_activities():
    """Return recent hotel activities"""
    activities = []
    
    # Get recent check-ins
    checkins = frappe.get_all(
        "Checked In",
        filters={
            "actual_check_in": [">=", add_to_date(getdate(), days=-1)],
            "docstatus": 1
        },
        fields=["name", "guest", "room", "actual_check_in", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    for checkin in checkins:
        guest_name = frappe.db.get_value("Guest", checkin.guest, "guest_name") or "Unknown"
        room_number = frappe.db.get_value("Room", checkin.room, "room_number") or "Unknown"
        
        activities.append({
            "name": checkin.name,
            "activity_type": "check_in",
            "title": "Guest Check-in",
            "description": f"{guest_name} checked into Room {room_number}",
            "creation": checkin.creation
        })
    
    # Get recent check-outs
    checkouts = frappe.get_all(
        "Checked In",
        filters={
            "actual_check_out": [">=", add_to_date(getdate(), days=-1)],
            "docstatus": 1
        },
        fields=["name", "guest", "room", "actual_check_out", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    for checkout in checkouts:
        guest_name = frappe.db.get_value("Guest", checkout.guest, "guest_name") or "Unknown"
        room_number = frappe.db.get_value("Room", checkout.room, "room_number") or "Unknown"
        
        activities.append({
            "name": checkout.name,
            "activity_type": "check_out",
            "title": "Guest Check-out",
            "description": f"{guest_name} checked out from Room {room_number}",
            "creation": checkout.creation
        })
    
    # Get recent reservations
    reservations = frappe.get_all(
        "Reservation",
        filters={
            "creation": [">=", add_to_date(getdate(), days=-1)],
            "docstatus": 1
        },
        fields=["name", "guest", "room_type", "arrival_date", "departure_date", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    for reservation in reservations:
        guest_name = frappe.db.get_value("Guest", reservation.guest, "guest_name") or "Unknown"
        
        activities.append({
            "name": reservation.name,
            "activity_type": "reservation",
            "title": "New Reservation",
            "description": f"Booking for {guest_name} - {reservation.room_type}",
            "creation": reservation.creation
        })
    
    # Sort all activities by creation time
    activities.sort(key=lambda x: x["creation"], reverse=True)
    
    return activities[:20]  # Return latest 20 activities

@frappe.whitelist()
def get_rooms():
    """Get all rooms with current status"""
    return frappe.get_all(
        "Room",
        fields=["name", "room_number", "room_type", "floor", "status"],
        order_by="room_number asc"
    )

@frappe.whitelist()
def get_reservations():
    """Get all reservations"""
    return frappe.get_all(
        "Reservation",
        fields=[
            "name", "guest", "room_type", "arrival_date", "departure_date",
            "adults", "children", "status", "total_amount", "creation"
        ],
        order_by="arrival_date desc"
    )

@frappe.whitelist()
def get_guests():
    """Get all guests"""
    return frappe.get_all(
        "Guest",
        fields=[
            "name", "guest_name", "email", "phone", "address", 
            "id_type", "id_number", "nationality", "creation"
        ],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_housekeeping_tasks():
    """Get housekeeping tasks"""
    return frappe.get_all(
        "Housekeeping Task",
        fields=[
            "name", "room", "task_type", "priority", "assigned_to",
            "status", "notes", "creation", "completion_time"
        ],
        order_by="creation desc"
    )

@frappe.whitelist()
def create_housekeeping_task(task_type, room, priority="Medium", assigned_to="", notes=""):
    """Create a new housekeeping task"""
    task = frappe.get_doc({
        "doctype": "Housekeeping Task",
        "task_type": task_type,
        "room": room,
        "priority": priority,
        "assigned_to": assigned_to,
        "notes": notes,
        "status": "Pending"
    })
    task.insert(ignore_permissions=True)
    return task.name

@frappe.whitelist()
def create_reservation(guest_name, email, phone, room_type, arrival_date, departure_date, adults=1, children=0):
    """Create a new reservation"""
    # First create guest if not exists
    guest = frappe.db.exists("Guest", {"email": email})
    if not guest:
        guest_doc = frappe.get_doc({
            "doctype": "Guest",
            "guest_name": guest_name,
            "email": email,
            "phone": phone
        })
        guest_doc.insert(ignore_permissions=True)
        guest = guest_doc.name
    
    # Create reservation
    reservation = frappe.get_doc({
        "doctype": "Reservation",
        "guest": guest,
        "room_type": room_type,
        "arrival_date": arrival_date,
        "departure_date": departure_date,
        "adults": adults,
        "children": children,
        "status": "Pending"
    })
    reservation.insert(ignore_permissions=True)
    return reservation.name

@frappe.whitelist()
def create_guest(guest_name, email="", phone="", address="", nationality="", id_type="", id_number=""):
    """Create a new guest"""
    guest = frappe.get_doc({
        "doctype": "Guest",
        "guest_name": guest_name,
        "email": email,
        "phone": phone,
        "address": address,
        "nationality": nationality,
        "id_type": id_type,
        "id_number": id_number
    })
    guest.insert(ignore_permissions=True)
    return guest.name