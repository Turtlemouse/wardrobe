from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from supabase_client import supabase
import os

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

DEFAULT_USER_EMAIL = "DEFAULT_DEFAULT"


# -------------------------------------------------------
# HELPER FUNCTION TO COPY DEFAULT DATA
# -------------------------------------------------------

def copy_default_data_to_user(new_user_id):
    """
    Copies slots, attributes, and attribute-slot relationships from the default template user
    to a newly registered user.
    """
    try:
        # Get the default user
        default_user = supabase.table("users").select("*").eq("email", DEFAULT_USER_EMAIL).execute().data
        if not default_user:
            print("No default template user found. Skipping default data copy.")
            return
        
        default_user_id = default_user[0]["id"]
        
        # 1. Copy Slots
        default_slots = supabase.table("slots").select("*").eq("user_id", default_user_id).execute().data
        slot_id_mapping = {}  # Maps old slot_id to new slot_id
        
        for slot in default_slots:
            new_slot = supabase.table("slots").insert({
                "user_id": new_user_id,
                "slot_name": slot["slot_name"],
                "order_index": slot["order_index"]
            }).execute()
            
            slot_id_mapping[slot["slot_id"]] = new_slot.data[0]["slot_id"]
        
        # 2. Copy Attributes
        default_attributes = supabase.table("attributes").select("*").eq("user_id", default_user_id).execute().data
        attr_id_mapping = {}  # Maps old attr_id to new attr_id
        
        for attr in default_attributes:
            new_attr = supabase.table("attributes").insert({
                "user_id": new_user_id,
                "attr_name": attr["attr_name"],
                "attr_type": attr["attr_type"],
                "attr_possiblevals": attr["attr_possiblevals"],
                "allow_multiple": attr["allow_multiple"]
            }).execute()
            
            attr_id_mapping[attr["attr_id"]] = new_attr.data[0]["attr_id"]
        
        # 3. Copy Attribute-Slot relationships
        default_attr_slots = supabase.table("attr_slots").select("*").eq("user_id", default_user_id).execute().data
        
        for attr_slot in default_attr_slots:
            old_slot_id = attr_slot["slot_id"]
            old_attr_id = attr_slot["attr_id"]
            
            # Only copy if both the slot and attribute were successfully copied
            if old_slot_id in slot_id_mapping and old_attr_id in attr_id_mapping:
                supabase.table("attr_slots").insert({
                    "user_id": new_user_id,
                    "attr_id": attr_id_mapping[old_attr_id],
                    "slot_id": slot_id_mapping[old_slot_id],
                    "order_index": attr_slot["order_index"]
                }).execute()
        
        # 4. Copy Rules (if any)
        default_rules = supabase.table("rules").select("*").eq("user_id", default_user_id).execute().data
        
        for rule in default_rules:
            supabase.table("rules").insert({
                "user_id": new_user_id,
                "rule_definition": rule["rule_definition"]
            }).execute()
        
        print(f"Successfully copied default data to user {new_user_id}")
        
    except Exception as e:
        print(f"Error copying default data: {str(e)}")
        # Don't fail signup if default data copy fails

# -------------------------------------------------------
# AUTH
# -------------------------------------------------------

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return redirect("/wardrobe")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # ---------------------------
        # Validate null / empty fields
        # ---------------------------
        if not first or not last or not email or not password:
            flash("All fields are required.")
            return render_template("signup.html")

        # ---------------------------
        # Check if email already exists
        # ---------------------------
        existing = supabase.table("users") \
            .select("user_id") \
            .eq("email", email) \
            .execute()

        if existing.data:
            flash("An account with that email already exists.")
            return render_template("signup.html")

        # ---------------------------
        # Create new user
        # ---------------------------
        hashed = generate_password_hash(password)

        new_user = supabase.table("users").insert({
            "email": email,
            "password_hash": hashed,
            "first_name": first,
            "last_name": last
        }).execute()

        # Insert returns a list with the created row
        user = new_user.data[0]

        # ---------------------------
        # Start session
        # ---------------------------
        session["user_id"] = user["user_id"]
        session["email"] = email
        session["first_name"] = first
        session["last_name"] = last

        return redirect("/wardrobe")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        result = supabase.table("users").select("*").eq("email", email).execute()
        if not result.data:
            flash("User not found!")
            return render_template("login.html")

        user = result.data[0]

        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password!")
            return render_template("login.html")

        session["user_id"] = user["user_id"]
        return redirect("/wardrobe")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------------------------------------------
# LOAD WARDROBE SUMMARY PAGE
# -------------------------------------------------------

@app.route("/wardrobe")
def wardrobe_home():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    try:
        items = supabase.table("items").select("*").eq("user_id", user_id).execute().data
        attributes = supabase.table("attributes").select("*").eq("user_id", user_id).execute().data
        rules = supabase.table("rules").select("*").eq("user_id", user_id).execute().data

        return render_template(
            "wardrobe.html",
            items=items,
            attributes=attributes,
            rules=rules
        )
    except Exception as e:
        print(f"Error in wardrobe_home: {str(e)}")
        flash(f"Error loading wardrobe: {str(e)}")
        return render_template(
            "wardrobe.html",
            items=[],
            attributes=[],
            rules=[]
        )


# -------------------------------------------------------
# SLOTS
# -------------------------------------------------------

@app.route("/slots/new", methods=["GET", "POST"])
def add_slot():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":
        slot_name = request.form.get("slot_name", "").strip()
        order_index = int(request.form.get("order_index", 0))

        if not slot_name:
            flash("Slot name is required.")
            return redirect(request.referrer)

        # Shift existing slots at or after this order_index
        existing_slots = supabase.table("slots").select("*").eq("user_id", user_id).gte("order_index", order_index).execute().data
        for slot in existing_slots:
            supabase.table("slots").update({"order_index": slot["order_index"] + 1}).eq("slot_id", slot["slot_id"]).execute()

        # Insert new slot
        supabase.table("slots").insert({
            "user_id": user_id,
            "slot_name": slot_name,
            "order_index": order_index
        }).execute()

        return redirect("/items")

    order_index = request.args.get("order_index", 0)
    return render_template("add_slot.html", order_index=order_index)


@app.route("/slots/edit/<slot_id>", methods=["GET", "POST"])
def edit_slot(slot_id):
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":
        slot_name = request.form.get("slot_name", "").strip()

        if not slot_name:
            flash("Slot name is required.")
            return redirect(request.referrer)

        supabase.table("slots").update({"slot_name": slot_name}).eq("slot_id", slot_id).eq("user_id", user_id).execute()
        return redirect("/items")

    slot = supabase.table("slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).execute().data
    if not slot:
        flash("Slot not found.")
        return redirect("/items")

    return render_template("edit_slot.html", slot=slot[0])


@app.route("/slots/delete/<slot_id>", methods=["POST"])
def delete_slot(slot_id):
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    # Get the slot to find its order_index
    slot = supabase.table("slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).execute().data
    if slot:
        order_index = slot[0]["order_index"]
        
        # Delete the slot (cascade will handle items, attr_slots, etc.)
        supabase.table("slots").delete().eq("slot_id", slot_id).eq("user_id", user_id).execute()
        
        # Shift down slots that come after
        later_slots = supabase.table("slots").select("*").eq("user_id", user_id).gt("order_index", order_index).execute().data
        for s in later_slots:
            supabase.table("slots").update({"order_index": s["order_index"] - 1}).eq("slot_id", s["slot_id"]).execute()

    return redirect("/items")


# -------------------------------------------------------
# ITEMS
# -------------------------------------------------------

@app.route("/items")
def list_items():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    try:
        # Fetch all slots for this user, ordered by order_index
        slots = supabase.table("slots").select("*").eq("user_id", user_id).order("order_index").execute().data
        
        # Fetch all attributes
        all_attributes = supabase.table("attributes").select("*").eq("user_id", user_id).execute().data
        
        # Fetch all attribute-slot relationships
        attr_slots = supabase.table("attr_slots").select("*").eq("user_id", user_id).execute().data
        
        # Fetch all items
        items = supabase.table("items").select("*").eq("user_id", user_id).execute().data
        
        # Fetch all item attribute values
        attr_items = supabase.table("attr_items").select("*").eq("user_id", user_id).execute().data
        
        # Organize attributes by slot
        slot_attrs = {}
        for slot in slots:
            # Get attr_slots for this slot, ordered by order_index
            slot_attr_relations = [as_rel for as_rel in attr_slots if as_rel["slot_id"] == slot["slot_id"]]
            slot_attr_relations.sort(key=lambda x: x["order_index"])
            
            # Get the actual attribute objects
            slot_attributes = []
            for as_rel in slot_attr_relations:
                attr = next((a for a in all_attributes if a["attr_id"] == as_rel["attr_id"]), None)
                if attr:
                    slot_attributes.append(attr)
            
            slot_attrs[slot["slot_id"]] = slot_attributes
        
        # Organize items by slot with their attribute values
        slot_items = {}
        for slot in slots:
            slot_item_list = [item for item in items if item["slot_id"] == slot["slot_id"]]
            
            # For each item, get its attribute values
            for item in slot_item_list:
                item["attr_values"] = {}
                item_attrs = [ai for ai in attr_items if ai["item_id"] == item["item_id"]]
                for ai in item_attrs:
                    item["attr_values"][ai["attr_id"]] = ai["value"]
            
            slot_items[slot["slot_id"]] = slot_item_list
        
        return render_template("items.html", 
                             slots=slots, 
                             slot_attrs=slot_attrs,
                             slot_items=slot_items)
    except Exception as e:
        # Log the error and show a friendly message
        print(f"Error in list_items: {str(e)}")
        flash(f"Error loading items: {str(e)}")
        return render_template("items.html", 
                             slots=[], 
                             slot_attrs={},
                             slot_items={})


@app.route("/items/new", methods=["GET", "POST"])
def add_item():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    slot_id = request.args.get("slot_id")

    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        slot_id = request.form.get("slot_id")

        if not item_name or not slot_id:
            flash("Item name and slot are required.")
            return redirect(request.referrer)

        # Create the item
        new_item = supabase.table("items").insert({
            "user_id": user_id,
            "item_name": item_name,
            "slot_id": slot_id,
            "times_generated": 0,
            "times_worn": 0
        }).execute()

        item_id = new_item.data[0]["item_id"]

        # Add attribute values
        for key, value in request.form.items():
            if key.startswith("attr_"):
                attr_id = key.replace("attr_", "")
                if value.strip():  # Only insert if value is not empty
                    supabase.table("attr_items").insert({
                        "user_id": user_id,
                        "attr_id": attr_id,
                        "item_id": item_id,
                        "value": value.strip()
                    }).execute()

        return redirect("/items")

    # Fetch slot info
    slot = supabase.table("slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).execute().data
    if not slot:
        flash("Slot not found.")
        return redirect("/items")

    # Fetch attributes for this slot
    attr_slots = supabase.table("attr_slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).order("order_index").execute().data
    
    attributes = []
    for as_rel in attr_slots:
        attr = supabase.table("attributes").select("*").eq("attr_id", as_rel["attr_id"]).execute().data
        if attr:
            attributes.append(attr[0])

    return render_template("add_item.html", slot=slot[0], attributes=attributes)


@app.route("/items/edit/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()

        if not item_name:
            flash("Item name is required.")
            return redirect(request.referrer)

        # Update item name
        supabase.table("items").update({"item_name": item_name}).eq("item_id", item_id).eq("user_id", user_id).execute()

        # Update attribute values
        # First, delete existing attr_items for this item
        supabase.table("attr_items").delete().eq("item_id", item_id).eq("user_id", user_id).execute()

        # Then insert new values
        for key, value in request.form.items():
            if key.startswith("attr_"):
                attr_id = key.replace("attr_", "")
                if value.strip():
                    supabase.table("attr_items").insert({
                        "user_id": user_id,
                        "attr_id": attr_id,
                        "item_id": item_id,
                        "value": value.strip()
                    }).execute()

        return redirect("/items")

    # Fetch item
    item = supabase.table("items").select("*").eq("item_id", item_id).eq("user_id", user_id).execute().data
    if not item:
        flash("Item not found.")
        return redirect("/items")
    
    item = item[0]
    slot_id = item["slot_id"]

    # Fetch slot
    slot = supabase.table("slots").select("*").eq("slot_id", slot_id).execute().data[0]

    # Fetch attributes for this slot
    attr_slots = supabase.table("attr_slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).order("order_index").execute().data
    
    attributes = []
    for as_rel in attr_slots:
        attr = supabase.table("attributes").select("*").eq("attr_id", as_rel["attr_id"]).execute().data
        if attr:
            attributes.append(attr[0])

    # Fetch current attribute values
    attr_items = supabase.table("attr_items").select("*").eq("item_id", item_id).eq("user_id", user_id).execute().data
    attr_values = {ai["attr_id"]: ai["value"] for ai in attr_items}

    return render_template("edit_item.html", item=item, slot=slot, attributes=attributes, attr_values=attr_values)


@app.route("/items/delete/<item_id>", methods=["POST"])
def delete_item(item_id):
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    supabase.table("items").delete().eq("item_id", item_id).eq("user_id", user_id).execute()
    return redirect("/items")


# -------------------------------------------------------
# ATTRIBUTE DEFINITIONS
# -------------------------------------------------------

@app.route("/attributes")
def list_attributes():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    attrs = supabase.table("attributes").select("*").eq("user_id", user_id).execute().data
    return render_template("attributes.html", attributes=attrs)


@app.route("/attributes/new", methods=["GET", "POST"])
def add_attribute():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    slot_id = request.args.get("slot_id")
    order_index = int(request.args.get("order_index", 0))

    if request.method == "POST":
        attr_name = request.form.get("attr_name", "").strip()
        attr_type = request.form.get("attr_type", "string")
        allowed_values = request.form.get("allowed_values", "")
        allow_multiple = request.form.get("allow_multiple") == "on"
        slot_id = request.form.get("slot_id")
        order_index = int(request.form.get("order_index", 0))

        if not attr_name:
            flash("Attribute name is required.")
            return redirect(request.referrer)

        # Parse allowed values
        allowed_values_list = None
        if allowed_values.strip():
            allowed_values_list = [v.strip() for v in allowed_values.split(",") if v.strip()]

        # Create attribute
        new_attr = supabase.table("attributes").insert({
            "user_id": user_id,
            "attr_name": attr_name,
            "attr_type": attr_type,
            "attr_possiblevals": allowed_values_list,
            "allow_multiple": allow_multiple
        }).execute()

        attr_id = new_attr.data[0]["attr_id"]

        # If slot_id is provided, link it to the slot
        if slot_id:
            # Shift existing attributes at or after this order_index
            existing_attr_slots = supabase.table("attr_slots").select("*").eq("slot_id", slot_id).gte("order_index", order_index).execute().data
            for as_rel in existing_attr_slots:
                supabase.table("attr_slots").update({"order_index": as_rel["order_index"] + 1}).eq("attr_slot_id", as_rel["attr_slot_id"]).execute()

            # Create attr_slot relationship
            supabase.table("attr_slots").insert({
                "user_id": user_id,
                "attr_id": attr_id,
                "slot_id": slot_id,
                "order_index": order_index
            }).execute()

            return redirect("/items")

        return redirect("/attributes")

    # If adding to a specific slot, get slot info
    slot = None
    if slot_id:
        slot_data = supabase.table("slots").select("*").eq("slot_id", slot_id).eq("user_id", user_id).execute().data
        if slot_data:
            slot = slot_data[0]

    return render_template("add_attribute.html", slot=slot, order_index=order_index)


# -------------------------------------------------------
# RULES
# -------------------------------------------------------

@app.route("/rules")
def list_rules():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    try:
        rules = supabase.table("rules").select("*").eq("user_id", user_id).execute().data
        return render_template("rules.html", rules=rules)
    except Exception as e:
        print(f"Error in list_rules: {str(e)}")
        flash(f"Error loading rules: {str(e)}")
        return render_template("rules.html", rules=[])


@app.route("/rules/new", methods=["GET", "POST"])
def add_rule():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":
        rule_definition = request.form.get("rule_definition", "").strip()

        if not rule_definition:
            flash("Rule definition is required.")
            return redirect(request.referrer)

        supabase.table("rules").insert({
            "user_id": user_id,
            "rule_definition": rule_definition
        }).execute()

        return redirect("/rules")

    return render_template("add_rule.html")


# -------------------------------------------------------
# RUN FLASK
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)